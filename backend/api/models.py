from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('procurement_officer', 'Procurement Officer'),
        ('vendor', 'Vendor'),
        ('auditor', 'Auditor'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    

class Role(models.Model):
    ROLE_CHOICES = (
        ('procurement_officer', 'Procurement Officer'),
        ('vendor', 'Vendor'),
        ('admin', 'Administrator'),
    )
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')  # Ensures a user cannot have duplicate roles

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
    
class VendorProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    tax_id = models.CharField(max_length=100)
    
    # Document upload field
    business_license = models.FileField(upload_to='vendor_documents/business_licenses/', blank=True, null=True)
    certification = models.FileField(upload_to='vendor_documents/certifications/', blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.business_name} ({self.user.email})"

class VendorProfileAuditLog(models.Model):
    vendor_profile = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='audit_logs')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    field_changed = models.CharField(max_length=255)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Change in {self.vendor_profile.business_name} by {self.changed_by.email}"

class Tender(models.Model):
    OPEN = 'open'
    RESTRICTED = 'restricted'

    TENDER_TYPE_CHOICES = [
        (OPEN, 'Open'),
        (RESTRICTED, 'Restricted'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    tender_type = models.CharField(max_length=20, choices=TENDER_TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'procurement_officer'})
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    def publish(self):
        """Method to publish the tender and notify vendors"""
        self.is_published = True
        self.save()
        # # Trigger notification task to vendors
        # notify_vendors_of_new_tender.delay(self.id)

    def close_tender(self):
        """Method to automatically close the tender after the deadline"""
        self.is_closed = True
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the Tender object first
        from .tasks import notify_vendors_of_new_tender  # Import inside the method to avoid circular import
        notify_vendors_of_new_tender.delay(self.id)

    def __str__(self):
        return self.title

class TenderAmendment(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='amendments')
    amended_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'procurement_officer'})
    amendment_details = models.TextField()
    amended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Amendment to {self.tender.title}"

class TenderVendorNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_tender', 'New Tender'),
        ('amendment', 'Amendment'),
    ]
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE)
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.vendor.business_name} - {self.tender.title}"
    
class Bid(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='bids')
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='bids')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    technical_specifications = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.vendor.business_name} for {self.tender.title}"

class EvaluationCriteria(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='criteria')
    name = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # Weight of the criterion in scoring

    def __str__(self):
        return f"{self.name} for {self.tender.title}"

class BidEvaluation(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='evaluations')
    criterion = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)  # Score given for this criterion

    def __str__(self):
        return f"Evaluation for {self.bid.vendor.business_name}'s bid on {self.bid.tender.title}"

class BidScore(models.Model):
    bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name='score')
    total_score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Total score for {self.bid.vendor.business_name}'s bid"


class Contract(models.Model):
    bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name='contract')
    start_date = models.DateField()
    end_date = models.DateField()
    terms = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    amended = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Contract for {self.bid.vendor.business_name} (Bid: {self.bid.id})"
    
    def is_expiring_soon(self):
        return (self.end_date - timezone.now().date()).days <= 30

class ContractMilestone(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='milestones')
    description = models.CharField(max_length=255)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Milestone for {self.contract.bid.vendor.business_name}: {self.description}"

class ContractAmendment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='amendments')
    amendment_description = models.TextField()
    amended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Amendment to {self.contract.bid.vendor.business_name} (Contract ID: {self.contract.id})"

class VendorContractPerformance(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='performance')
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 85.00 for 85%
    delivery_timeliness = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 90.00 for 90%
    quality_score = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 95.00 for 95%
    overall_performance = models.DecimalField(max_digits=5, decimal_places=2)  # Calculated based on the above

    def calculate_overall_performance(self):
        return (self.compliance_score + self.delivery_timeliness + self.quality_score) / 3
    
    def save(self, *args, **kwargs):
        self.overall_performance = self.calculate_overall_performance()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Performance for {self.contract.bid.vendor.business_name}"
    
class ApprovalStage(models.Model):
    STAGE_CHOICES = [
        ('initial', 'Initial Approval'),
        ('procurement', 'Procurement Officer Approval'),
        ('auditor', 'Auditor Approval'),
        ('admin', 'Admin Approval'),
    ]
    name = models.CharField(max_length=100, choices=STAGE_CHOICES)
    order = models.IntegerField(help_text="The order of this approval stage in the workflow")

    def __str__(self):
        return self.name

class ApprovalWorkflow(models.Model):
    APPROVAL_TYPE_CHOICES = [
        ('bid', 'Bid Approval'),
        ('contract', 'Contract Approval'),
        ('vendor', 'Vendor Registration Approval'),
    ]
    approval_type = models.CharField(max_length=50, choices=APPROVAL_TYPE_CHOICES)
    reference_id = models.PositiveIntegerField(help_text="ID of the related object (Bid, Contract, or Vendor)")
    current_stage = models.ForeignKey(ApprovalStage, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Approval Workflow for {self.get_approval_type_display()}"

class ApprovalLog(models.Model):
    workflow = models.ForeignKey(ApprovalWorkflow, on_delete=models.CASCADE, related_name='approval_logs')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    stage = models.ForeignKey(ApprovalStage, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.workflow.approval_type} approved by {self.approved_by} at {self.stage.name}"
    
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    ]
    
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    delivered = models.BooleanField(default=False)  # New field to track delivery status
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.user.email} ({self.notification_type})"

class NotificationPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification Preferences for {self.user.email}"

class TenderReport(models.Model):
    tender = models.OneToOneField(Tender, on_delete=models.CASCADE, related_name='report')
    total_bids = models.IntegerField()
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Tender Report for {self.tender.title}"

class VendorPerformance(models.Model):
    vendor = models.OneToOneField(VendorProfile, on_delete=models.CASCADE, related_name='performance')
    average_delivery_time = models.DurationField()
    compliance_rate = models.DecimalField(max_digits=5, decimal_places=2)
    rating = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Performance Report for {self.vendor.business_name}"
    
class SpendAnalytics(models.Model):
    category = models.CharField(max_length=100)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()

    def __str__(self):
        return f"Spend Report for {self.category} - {self.month}"

class AuditLog(models.Model):
    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.action} on {self.model_name} (ID: {self.object_id}) by {self.user} at {self.timestamp}"