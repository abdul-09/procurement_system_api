import venv
import pytest
# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'procurement_system.settings')


from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from api.models import Tender, User, Bid, VendorProfile, EvaluationCriteria, Contract, ApprovalStage, ApprovalWorkflow, ApprovalLog, VendorPerformance, SpendAnalytics
from django.utils import timezone
from datetime import date, timedelta


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        return User.objects.create_user(**kwargs)
    return make_user

@pytest.fixture
def create_procurement_officer():
    """Fixture to create a procurement officer for testing."""
    return User.objects.create_user(
        email='officer@example.com',
        password='password123',
        role='procurement_officer',
        is_staff=True
    )

@pytest.fixture
def tender_fake(create_procurement_officer):
    officer = create_procurement_officer
    return Tender.objects.create(
        title="Office Supplies",
        description="Procurement of office supplies for Q3.",
        tender_type="open",
        created_by=officer,
        deadline=timezone.now() + timezone.timedelta(days=30),
    )

@pytest.fixture
def vendor_profile(create_user):
    user = create_user(email='testlogin@example.com', password='testpassword')
    return VendorProfile.objects.create(
        user=user,
        business_name='trash',
        contact_person='zeroin',
        phone_number='233384647',
        address='add cegvf',
        tax_id='217474',
        business_license='',
        certification='',
    )

@pytest.fixture
def bid_fake(vendor_profile, tender_fake):
    return Bid.objects.create(
        vendor=vendor_profile,
        tender=tender_fake,
        price=100000,
        technical_specifications="Tech specs for the tender"
    )

@pytest.fixture
def criteria(tender_fake):
    return EvaluationCriteria.objects.create(
        tender=tender_fake,
        name="Price",
        weight=50
    )

@pytest.fixture
def contract_fake(bid_fake):
    return Contract.objects.create(
            bid=bid_fake,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=180),
            terms="Contract terms here."
        )

@pytest.fixture
def approval_stage_demo():
    return ApprovalStage.objects.create(
        name = 'initial',
        order = 1
    )

@pytest.fixture
def workflow_demo(tender_fake, approval_stage_demo):
    return ApprovalWorkflow.objects.create(
        approval_type= 'bid',
        reference_id= tender_fake.id,
        current_stage= approval_stage_demo
    )

@pytest.fixture
def approvalLog_demo(workflow_demo, create_procurement_officer, approval_stage_demo):
    user = create_procurement_officer
    return ApprovalLog.objects.create(
        workflow=workflow_demo,
        approved_by= user.id,
        stage= approval_stage_demo,
        comment= 'Approval given.'
    )

@pytest.fixture
def vendor_profile_factory(create_user):
    def create_vendor_profile(email, business_name, contact_person):
        user = create_user(email=email, password='testpassword')
        return VendorProfile.objects.create(
            user=user,
            business_name=business_name,
            contact_person=contact_person,
            phone_number='233384647',
            address='123 Business St.',
            tax_id='217474',
            business_license='BL-12345',
            certification='Cert-12345',
        )
    return create_vendor_profile

@pytest.fixture
def tender_data(create_procurement_officer):
    officer = create_procurement_officer
    tender_1 = Tender.objects.create(
        title="Tender A",
        description="First tender",
        created_by=officer,
        deadline=timezone.now() + timezone.timedelta(days=10)  # use deadline instead of end_date
    )
    tender_2 = Tender.objects.create(
        title="Tender B",
        description="Second tender",
        created_by=officer,
        deadline=timezone.now() + timezone.timedelta(days=15)  # use deadline instead of end_date
    )
    return tender_1, tender_2

@pytest.fixture
def bid_data(tender_data, vendor_profile_factory):
    tender_1, tender_2 = tender_data
    vendor_1 = vendor_profile_factory(
        email='vendor1@example.com',
        business_name='Vendor 1',
        contact_person='Alice'
    )
    vendor_2 = vendor_profile_factory(
        email='vendor2@example.com',
        business_name='Vendor 2',
        contact_person='Bob'
    )
    vendor_3 = vendor_profile_factory(
        email='vendor3@example.com',
        business_name='Vendor 3',
        contact_person='Charlie'
    )
    bid_1 = Bid.objects.create(
        tender=tender_1,
        vendor=vendor_1,
        price=50000,
        technical_specifications="First tender"
    )
    bid_2 = Bid.objects.create(
        tender=tender_1,
        vendor=vendor_2,
        price=45000,
        technical_specifications="Second tender"
    )
    bid_3 = Bid.objects.create(
        tender=tender_2,
        vendor=vendor_3,
        price=60000,
        technical_specifications="Tech specs for the tender"
    )
    return bid_1, bid_2, bid_3

@pytest.fixture
def vendor_performance_data(vendor_profile_factory):
    vendor_1 = vendor_profile_factory(
        email='vendor1@example.com',
        business_name='Vendor 1',
        contact_person='Alice'
    )
    vendor_2 = vendor_profile_factory(
        email='vendor2@example.com',
        business_name='Vendor 2',
        contact_person='Bob'
    )

    VendorPerformance.objects.create(
        vendor=vendor_1,
        average_delivery_time=timedelta(days=5),
        compliance_rate=7.5,
        rating=4.5
    )
    VendorPerformance.objects.create(
        vendor=vendor_2,
        average_delivery_time=timedelta(days=7),
        compliance_rate=6.5,
        rating=3.8
    )


@pytest.fixture
def spend_analytics_data():
    SpendAnalytics.objects.create(
        category='Office Supplies',
        total_spent=50000,
        month=date(2024, 8, 1)
    )
    SpendAnalytics.objects.create(
        category='Technology',
        total_spent=120000,
        month=date(2024, 9, 1)
    )
