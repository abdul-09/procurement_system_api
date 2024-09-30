import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'procurement_system.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import User, Role, UserRole, VendorProfile, Tender, Bid, EvaluationCriteria, Contract, ApprovalStage, ApprovalWorkflow, NotificationPreferences
import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker

# Initialize Faker
fake = Faker()

def create_users():
    roles = ['procurement_officer', 'vendor', 'auditor']
    for _ in range(15):
        email = fake.email()
        role = random.choice(roles)
        User.objects.create(
            email=email,
            role=role,
            is_active=True,
            is_staff=(role == 'procurement_officer'),
            date_joined=timezone.now()
        )

def create_roles():
    role_names = ['procurement_officer', 'vendor', 'admin']
    for role_name in role_names:
        Role.objects.get_or_create(name=role_name)

def assign_user_roles():
    users = User.objects.all()
    roles = Role.objects.all()
    for user in users:
        assigned_role = random.choice(roles)
        UserRole.objects.create(user=user, role=assigned_role)

def create_vendor_profiles():
    vendors = User.objects.filter(role='vendor')
    for vendor in vendors[:15]:
        VendorProfile.objects.create(
            user=vendor,
            business_name=fake.company(),
            contact_person=fake.name(),
            phone_number=fake.phone_number()[:10],
            address=fake.address(),
            tax_id=fake.bothify('???-########'),
            status='approved'
        )

def create_tenders():
    procurement_officers = User.objects.filter(role='procurement_officer')
    for _ in range(15):
        Tender.objects.create(
            title=fake.catch_phrase(),
            description=fake.text(),
            tender_type=random.choice(['open', 'restricted']),
            created_by=random.choice(procurement_officers),
            deadline=timezone.now() + timedelta(days=random.randint(30, 90)),
            is_published=random.choice([True, False]),
            is_closed=False
        )

def create_bids():
    vendors = VendorProfile.objects.all()
    tenders = Tender.objects.all()
    for vendor in vendors[:15]:
        for tender in tenders[:15]:
            Bid.objects.create(
                vendor=vendor,
                tender=tender,
                price=fake.pydecimal(left_digits=6, right_digits=2, positive=True),
                technical_specifications=fake.text(),
                submitted_at=timezone.now()
            )

def create_evaluation_criteria():
    tenders = Tender.objects.all()
    for tender in tenders:
        for _ in range(3):
            EvaluationCriteria.objects.create(
                tender=tender,
                name=fake.word(),
                weight=random.uniform(0.1, 1.0)
            )

def create_contracts():
    bids = Bid.objects.all()
    for bid in bids[:15]:
        Contract.objects.create(
            bid=bid,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=random.randint(30, 365))).date(),
            terms=fake.text(),
            created_at=timezone.now(),
            amended=False
        )

def create_approval_stages():
    stages = ['initial', 'procurement', 'auditor', 'admin']
    for order, stage in enumerate(stages, start=1):
        ApprovalStage.objects.get_or_create(name=stage, order=order)

def create_approval_workflows():
    tenders = Tender.objects.all()
    stages = ApprovalStage.objects.all()
    for tender in tenders[:15]:
        ApprovalWorkflow.objects.create(
            approval_type='tender',
            reference_id=tender.id,
            current_stage=random.choice(stages),
            is_approved=random.choice([True, False]),
            created_at=timezone.now()
        )

def create_notification_preferences():
    users = User.objects.all()
    for user in users[:15]:
        NotificationPreferences.objects.create(
            user=user,
            email_enabled=True,
            sms_enabled=random.choice([True, False]),
            in_app_enabled=True
        )

def run_seed():
    create_users()
    create_roles()
    assign_user_roles()
    create_vendor_profiles()
    create_tenders()
    create_bids()
    create_evaluation_criteria()
    create_contracts()
    create_approval_stages()
    create_approval_workflows()
    create_notification_preferences()

if __name__ == '__main__':
    run_seed()
