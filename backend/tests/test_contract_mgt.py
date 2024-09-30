import pytest
from django.utils import timezone
from api.models import User, VendorProfile, Bid, Contract, ContractMilestone, ContractAmendment, VendorContractPerformance
from api.tasks import notify_expiring_contracts, notify_upcoming_milestones
from django.core import mail



@pytest.mark.django_db
class TestContractManagement:

    def test_contract_creation(self, bid_fake):
        contract = Contract.objects.create(
            bid=bid_fake,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=180),
            terms="Contract terms here."
        )
        assert contract.terms == "Contract terms here."
        assert contract.bid == bid_fake

    def test_contract_milestone_creation(self, contract_fake):
        milestone = ContractMilestone.objects.create(
            contract=contract_fake,
            description="Deliver Phase 1",
            due_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        assert milestone.contract == contract_fake
        assert milestone.description == "Deliver Phase 1"
        assert not milestone.completed

    def test_contract_amendment(self, contract_fake, create_procurement_officer):
        officer = create_procurement_officer
        amendment = ContractAmendment.objects.create(
            contract=contract_fake,
            amendment_description="Amendment to extend deadline",
            amended_by=officer
        )
        assert amendment.contract == contract_fake
        assert amendment.amendment_description == "Amendment to extend deadline"
        assert amendment.amended_by == officer

    def test_vendor_performance_tracking(self, contract_fake):
        performance = VendorContractPerformance.objects.create(
            contract=contract_fake,
            compliance_score=90.00,
            delivery_timeliness=85.00,
            quality_score=95.00
        )
        performance.save()
        assert performance.compliance_score == 90.00
        assert performance.delivery_timeliness == 85.00
        assert performance.quality_score == 95.00
        assert performance.overall_performance == 90.00

    def test_notify_expiring_contracts(self, contract_fake):
        contract_fake.end_date = timezone.now().date() + timezone.timedelta(days=20)
        contract_fake.save()
        notify_expiring_contracts()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Contract Expiring Soon"
        assert contract_fake.bid.vendor.user.email in mail.outbox[0].to

    def test_notify_upcoming_milestones(self, contract_fake):
        milestone = ContractMilestone.objects.create(
            contract=contract_fake,
            description="Phase 1 Delivery",
            due_date=timezone.now().date() + timezone.timedelta(days=5)
        )
        notify_upcoming_milestones()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Upcoming Milestone Due"
        assert milestone.contract.bid.vendor.user.email in mail.outbox[0].to
