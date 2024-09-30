from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid login credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return {
            'email': user.email,
            'access': str(access_token),
            'refresh': str(refresh),
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value

    def save(self, **kwargs):
        request = self.context.get('request')
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate password reset token
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construct password reset URL
        reset_url = request.build_absolute_uri(
            reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})
        )
        
        # Send password reset email
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_url}',
            'admin@yourapp.com',
            [user.email],
            fail_silently=False,
        )

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = urlsafe_base64_encode(data['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid user ID")

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token")

        return data

    def save(self, **kwargs):
        uid = urlsafe_base64_encode(self.validated_data['uidb64']).decode()
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def send_verification_email(self, user, request):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = request.build_absolute_uri(
            reverse('email-verify', kwargs={'uidb64': uid, 'token': token})
        )

        send_mail(
            'Verify Your Email',
            f'Click the link to verify your email: {verification_url}',
            'admin@yourapp.com',
            [user.email],
            fail_silently=False,
        )

class EmailVerificationConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        uid = urlsafe_base64_encode(data['uidb64']).decode()
        user = User.objects.get(pk=uid)

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token")

        return data

    def save(self):
        uid = urlsafe_base64_encode(self.validated_data['uidb64']).decode()
        user = User.objects.get(pk=uid)
        user.is_active = True
        user.save()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['user', 'role']

    def create(self, validated_data):
        # Ensure that the role assignment is unique
        user = validated_data.get('user')
        role = validated_data.get('role')

        user_role, created = UserRole.objects.get_or_create(user=user, role=role)
        return user_role

class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'contact_person', 'phone_number', 'address', 'tax_id', 'business_license', 'certification']

    def update(self, instance, validated_data):
        changed_fields = {}
        
        # Track changes in profile fields
        for field, value in validated_data.items():
            old_value = getattr(instance, field, None)
            if old_value != value:
                changed_fields[field] = (old_value, value)

        # Perform the actual update
        instance = super().update(instance, validated_data)

        # Log changes in the audit logs
        for field, (old_value, new_value) in changed_fields.items():
            VendorProfileAuditLog.objects.create(
                vendor_profile=instance,
                changed_by=self.context['request'].user,
                field_changed=field,
                old_value=old_value,
                new_value=new_value
            )

        return instance

class VendorProfileAuditLogSerializer(serializers.ModelSerializer):
    changed_by = serializers.CharField(source='changed_by.email', read_only=True)

    class Meta:
        model = VendorProfileAuditLog
        fields = ['vendor_profile', 'field_changed', 'old_value', 'new_value', 'changed_by', 'timestamp']


class VendorRegistrationSerializer(serializers.ModelSerializer):
    vendor_profile = VendorProfileSerializer()

    class Meta:
        model = User
        fields = ['email', 'password', 'vendor_profile']

    def create(self, validated_data):
        vendor_profile_data = validated_data.pop('vendor_profile')
        user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'], role='vendor')
        VendorProfile.objects.create(user=user, **vendor_profile_data)
        return user
    
class TenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = '__all__'
        read_only_fields = ['created_by', 'is_published', 'is_closed']

    def validate_deadline(self, deadline):
        if deadline <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return deadline

class TenderAmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderAmendment
        fields = '__all__'
        read_only_fields = ['amended_by', 'amended_at']

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 'vendor', 'tender', 'price', 'technical_specifications', 'submitted_at']

class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriteria
        fields = ['id', 'tender', 'name', 'weight']

class BidEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidEvaluation
        fields = ['id', 'bid', 'criterion', 'score']

class BidScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidScore
        fields = ['id', 'bid', 'total_score']

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['id', 'bid', 'start_date', 'end_date', 'terms', 'created_at', 'amended']

class ContractMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractMilestone
        fields = ['id', 'contract', 'description', 'due_date', 'completed']

class ContractAmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAmendment
        fields = ['id', 'contract', 'amendment_description', 'amended_by', 'amended_at']

class VendorContractPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPerformance
        fields = ['id', 'contract', 'compliance_score', 'delivery_timeliness', 'quality_score', 'overall_performance']

class ApprovalStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalStage
        fields = ['id', 'name', 'order']

class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalWorkflow
        fields = ['id', 'approval_type', 'reference_id', 'current_stage', 'is_approved', 'created_at']

class ApprovalLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalLog
        fields = ['id', 'workflow', 'approved_by', 'stage', 'comment', 'approved_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['recipient', 'message', 'notification_type', 'sent_at']

class NotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreferences
        fields = ['email_enabled', 'sms_enabled', 'in_app_enabled']

class TenderReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderReport
        fields = ['tender', 'total_bids', 'total_value', 'status']

class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPerformance
        fields = ['vendor', 'average_delivery_time', 'compliance_rate', 'rating']

class SpendAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendAnalytics
        fields = ['category', 'total_spent', 'month']

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'