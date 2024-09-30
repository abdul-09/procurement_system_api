import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from faker import Faker
from api.models import (
    User, Role, UserRole, VendorProfile, VendorProfileAuditLog, Tender, TenderAmendment,
    TenderVendorNotification, Bid, EvaluationCriteria, BidEvaluation, BidScore, Contract, ContractMilestone,
    ContractAmendment, VendorContractPerformance, ApprovalStage, ApprovalWorkflow, ApprovalLog,
    Notification, NotificationPreferences, TenderReport, VendorPerformance
)

fake = Faker()

class Command(BaseCommand):
    help = "Generates test data for the application models."

    def handle(self, *args, **kwargs):
        # Call all functions in order
        self.create_roles()
        users = self.create_users()
        self.assign_user_roles(users)
        self.create_vendor_profiles(users)
        tenders = self.create_tenders(users)
        self.create_bids(tenders)
        self.create_evaluation_criteria(tenders)
        self.create_contracts()
        self.create_approval_stages()
        self.create_approval_workflows()
        self.create_notification_preferences()
        self.stdout.write(self.style.SUCCESS('Successfully created test data for models.'))

    def create_roles(self):
        roles = ['procurement_officer', 'vendor', 'admin']
        for role in roles:
            Role.objects.get_or_create(name=role)
        self.stdout.write(self.style.SUCCESS('Created roles.'))

    def create_users(self):
        users = []
        for _ in range(15):
            email = fake.email()
            role = random.choice(['procurement_officer', 'vendor', 'auditor'])
            user = User.objects.create(
                email=email,
                role=role,
                is_active=True,
                is_staff=False,
                date_joined=timezone.now()
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS('Created 15 users.'))
        return users

    def assign_user_roles(self, users):
        roles = Role.objects.all()
        for user in users:
            user_role = random.choice(roles)
            UserRole.objects.create(user=user, role=user_role)
        self.stdout.write(self.style.SUCCESS('Assigned roles to users.'))

    def create_vendor_profiles(self, users):
        for user in users:
            if user.role == 'vendor':
                VendorProfile.objects.create(
                    user=user,
                    business_name=fake.company(),
                    contact_person=fake.name(),
                    phone_number=fake.phone_number(),
                    address=fake.address(),
                    tax_id=fake.ssn(),
                    business_license=None,
                    certification=None,
                    status=random.choice(['pending', 'approved', 'rejected'])
                )
        self.stdout.write(self.style.SUCCESS('Created vendor profiles for vendor users.'))

    def create_tenders(self, users):
        tenders = []
        for _ in range(15):
            tender = Tender.objects.create(
                title=fake.bs(),
                description=fake.text(),
                tender_type=random.choice([Tender.OPEN, Tender.RESTRICTED]),
                created_by=random.choice(users),
                created_at=timezone.now(),
                deadline=timezone.now() + timezone.timedelta(days=random.randint(30, 60)),
                is_published=random.choice([True, False]),
                is_closed=random.choice([True, False])
            )
            tenders.append(tender)
        self.stdout.write(self.style.SUCCESS('Created 15 tenders.'))
        return tenders

    def create_bids(self, tenders):
        for tender in tenders:
            for _ in range(3):  # Create 3 bids per tender
                vendor_profile = random.choice(VendorProfile.objects.all())
                Bid.objects.create(
                    vendor=vendor_profile,
                    tender=tender,
                    price=random.uniform(1000, 50000),
                    technical_specifications=fake.text(),
                    submitted_at=timezone.now()
                )
        self.stdout.write(self.style.SUCCESS('Created bids for tenders.'))

    def create_evaluation_criteria(self, tenders):
        for tender in tenders:
            for _ in range(3):  # Create 3 evaluation criteria per tender
                criteria = EvaluationCriteria.objects.create(
                    tender=tender,
                    name=fake.bs(),
                    weight=random.uniform(1, 100)
                )
                # Assign random scores to the criteria for each bid
                for bid in Bid.objects.filter(tender=tender):
                    BidEvaluation.objects.create(
                        bid=bid,
                        criterion=criteria,
                        score=random.uniform(1, 100)
                    )
                    BidScore.objects.create(bid=bid, total_score=random.uniform(50, 100))
        self.stdout.write(self.style.SUCCESS('Created evaluation criteria and bid scores.'))

    def create_contracts(self):
        for bid in Bid.objects.all():
            contract = Contract.objects.create(
                bid=bid,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=random.randint(365, 730)),
                terms=fake.text()
            )
            # Create 3 milestones per contract
            for _ in range(3):
                ContractMilestone.objects.create(
                    contract=contract,
                    description=fake.bs(),
                    due_date=timezone.now().date() + timezone.timedelta(days=random.randint(30, 60)),
                    completed=random.choice([True, False])
                )
        self.stdout.write(self.style.SUCCESS('Created contracts and contract milestones.'))

    def create_approval_stages(self):
        # Assuming you have approval stages predefined or want to create random ones
        for _ in range(5):
            ApprovalStage.objects.create(
                name=fake.bs(),
                description=fake.text(),
                order=random.randint(1, 5)
            )
        self.stdout.write(self.style.SUCCESS('Created approval stages.'))

    def create_approval_workflows(self):
        # Create a random workflow with stages
        for contract in Contract.objects.all():
            approval_stage = random.choice(ApprovalStage.objects.all())
            ApprovalWorkflow.objects.create(
                contract=contract,
                stage=approval_stage,
                approved=random.choice([True, False]),
                approval_date=timezone.now()
            )
        self.stdout.write(self.style.SUCCESS('Created approval workflows.'))

    def create_notification_preferences(self):
        for user in User.objects.all():
            NotificationPreferences.objects.create(
                user=user,
                email_notifications_enabled=random.choice([True, False]),
                sms_notifications_enabled=random.choice([True, False]),
                push_notifications_enabled=random.choice([True, False])
            )
        self.stdout.write(self.style.SUCCESS('Created notification preferences.'))