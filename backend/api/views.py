from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import *
from .tasks import *


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset link has been sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, uidb64, token):
        data = {
            'uidb64': uidb64,
            'token': token,
            'new_password': request.data.get('new_password')
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            serializer.send_verification_email(user, request)
            return Response({"message": "Verification email sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationConfirmView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, uidb64, token):
        data = {
            'uidb64': uidb64,
            'token': token
        }
        serializer = EmailVerificationConfirmSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for creating a new role (optional if you want to add roles dynamically)
class RoleCreateView(generics.CreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]  # Only admin can create new roles


# View for assigning roles to users
class AssignRoleView(generics.CreateAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdminUser]  # Only admin can assign roles


# View for listing a user's roles
class UserRolesListView(generics.ListAPIView):
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdminUser]  # Restrict based on roles if needed

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return UserRole.objects.filter(user_id=user_id)
    

class ProcurementTaskView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsProcurementOfficer]

    def get(self, request):
        # Logic for procurement officers
        return Response({"message": "Welcome Procurement Officer!"})
    
class VendorProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Ensure vendors can only update their own profile
        return self.request.user.vendor_profile

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class VendorProfileAuditLogView(generics.ListAPIView):
    serializer_class = VendorProfileAuditLogSerializer
    permission_classes = [IsAdminUser]  # Only admins can view audit logs

    def get_queryset(self):
        vendor_profile_id = self.kwargs['vendor_profile_id']
        return VendorProfileAuditLog.objects.filter(vendor_profile__id=vendor_profile_id).order_by('-timestamp')

class VendorRegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VendorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Vendor registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VendorApprovalView(APIView):
    permission_classes = [IsAdminUser]
    def put(self, request, pk):
        try:
            vendor_profile = VendorProfile.objects.get(pk=pk)
        except VendorProfile.DoesNotExist:
            return Response({"error": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        status_value = request.data.get("status")  # Avoid naming it `status` to prevent conflicts
        if status_value not in ["approved", "rejected"]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        vendor_profile.status = status_value
        vendor_profile.save()
        return Response({"message": f"Vendor {status_value} successfully!"})

class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'procurement_officer':
            return Tender.objects.filter(created_by=user)
        elif user.role == 'vendor':
            return Tender.objects.filter(is_published=True, is_closed=False)
        elif user.role == 'auditor':
            return Tender.objects.all()
        return Tender.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def publish(self, request, pk=None):
        tender = self.get_object()
        if tender.is_published:
            return Response({'detail': 'Tender already published.'}, status=status.HTTP_400_BAD_REQUEST)
        tender.publish()
        return Response({'detail': 'Tender published successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def close(self, request, pk=None):
        tender = self.get_object()
        if tender.is_closed:
            return Response({'detail': 'Tender already closed.'}, status=status.HTTP_400_BAD_REQUEST)
        tender.close_tender()
        return Response({'detail': 'Tender closed successfully.'}, status=status.HTTP_200_OK)

class TenderAmendmentViewSet(viewsets.ModelViewSet):
    queryset = TenderAmendment.objects.all()
    serializer_class = TenderAmendmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['procurement_officer', 'admin']:
            return TenderAmendment.objects.all()
        return TenderAmendment.objects.none()

    def perform_create(self, serializer):
        amendment = serializer.save(amended_by=self.request.user)
        notify_vendors_of_amendment.delay(amendment.tender.id)

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

class EvaluationCriteriaViewSet(viewsets.ModelViewSet):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = EvaluationCriteriaSerializer
    permission_classes = [IsAuthenticated]

class BidEvaluationViewSet(viewsets.ModelViewSet):
    queryset = BidEvaluation.objects.all()
    serializer_class = BidEvaluationSerializer
    permission_classes = [IsAuthenticated]

class BidScoreViewSet(viewsets.ModelViewSet):
    queryset = BidScore.objects.all()
    serializer_class = BidScoreSerializer
    permission_classes = [IsAuthenticated]

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]

class ContractMilestoneViewSet(viewsets.ModelViewSet):
    queryset = ContractMilestone.objects.all()
    serializer_class = ContractMilestoneSerializer
    permission_classes = [IsAuthenticated]

class ContractAmendmentViewSet(viewsets.ModelViewSet):
    queryset = ContractAmendment.objects.all()
    serializer_class = ContractAmendmentSerializer
    permission_classes = [IsAuthenticated]

class VendorContractPerformanceViewSet(viewsets.ModelViewSet):
    queryset = VendorPerformance.objects.all()
    serializer_class = VendorPerformanceSerializer
    permission_classes = [IsAuthenticated]

class ApprovalStageViewSet(viewsets.ModelViewSet):
    queryset = ApprovalStage.objects.all()
    serializer_class = ApprovalStageSerializer
    permission_classes = [IsAuthenticated]

class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [IsAuthenticated]

class ApprovalLogViewSet(viewsets.ModelViewSet):
    queryset = ApprovalLog.objects.all()
    serializer_class = ApprovalLogSerializer
    permission_classes = [IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
class NotificationPreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferencesSerializer

    def get_queryset(self):
        return NotificationPreferences.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class TenderReportViewSet(viewsets.ModelViewSet):
    queryset = TenderReport.objects.all()
    serializer_class = TenderReportSerializer

    def get_queryset(self):
        tender_id = self.request.query_params.get('tender_id')
        if tender_id:
            return self.queryset.filter(tender_id=tender_id)
        return self.queryset

class VendorPerformanceViewSet(viewsets.ModelViewSet):
    queryset = VendorPerformance.objects.all()
    serializer_class = VendorPerformanceSerializer

    def get_queryset(self):
        vendor_id = self.request.query_params.get('vendor_id')
        if vendor_id:
            return self.queryset.filter(vendor_id=vendor_id)
        return self.queryset

class SpendAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = SpendAnalytics.objects.all()
    serializer_class = SpendAnalyticsSerializer

    def get_queryset(self):
        month = self.request.query_params.get('month')
        if month:
            return self.queryset.filter(month=month)
        return self.queryset

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset