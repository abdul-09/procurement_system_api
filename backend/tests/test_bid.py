import pytest
from django.utils import timezone
from django.core import mail
from api.models import Tender, User, Bid, TenderVendorNotification, VendorProfile, BidEvaluation, BidScore, EvaluationCriteria
from api.tasks import notify_vendor_bid_submission, notify_procurement_bid_evaluation




@pytest.mark.django_db
class TestBidSubmissionEvaluation:

    def test_bid_submission(self, vendor_profile, tender_fake):
        bid = Bid.objects.create(
            vendor=vendor_profile,
            tender=tender_fake,
            price=100000,
            technical_specifications="Tech specs for the tender"
        )
        assert bid.price == 100000
        assert bid.technical_specifications == "Tech specs for the tender"
        assert bid.tender == tender_fake

    def test_bid_evaluation(self, bid_fake, criteria):
        evaluation = BidEvaluation.objects.create(
            bid=bid_fake,
            criterion=criteria,
            score=85.0
        )
        assert evaluation.score == 85.0
        assert evaluation.criterion == criteria
        assert evaluation.bid == bid_fake

    def test_total_bid_score(self, bid_fake):
        criteria1 = EvaluationCriteria.objects.create(
            tender=bid_fake.tender, name="Price", weight=50)
        criteria2 = EvaluationCriteria.objects.create(
            tender=bid_fake.tender, name="Delivery Time", weight=50)

        BidEvaluation.objects.create(bid=bid_fake, criterion=criteria1, score=80)
        BidEvaluation.objects.create(bid=bid_fake, criterion=criteria2, score=90)

        total_score = 0
        evaluations = bid_fake.evaluations.all()
        for evaluation in evaluations:
            total_score += evaluation.score

        BidScore.objects.create(bid=bid_fake, total_score=total_score)
        bid_score = bid_fake.score.total_score

        assert bid_score == 170

    def test_notify_vendor_bid_submission(self, bid_fake):
        notify_vendor_bid_submission(bid_fake.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Bid Submission Confirmation"
        assert bid_fake.vendor.user.email in mail.outbox[0].to

    def test_notify_procurement_bid_evaluation(self, tender_fake):
        notify_procurement_bid_evaluation(tender_fake.id)
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Bid Evaluation Completed"
