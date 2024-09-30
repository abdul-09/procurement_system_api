from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, Bid, BidEvaluation, TenderAmendment
from .tasks import send_real_time_notification, notify_vendors_of_amendment, notify_vendor_bid_submission, notify_procurement_bid_evaluation

@receiver(post_save, sender=Notification)
def new_tender_notification(sender, instance, **kwargs):
    if not instance.delivered:
        send_real_time_notification.delay(instance.user.id, instance.message)

@receiver(post_save, sender=Bid)
def bid_notification(sender, instance, created, **kwargs):
    if created:  # Trigger only when a new bid is created
        notify_vendor_bid_submission.delay(instance.id)

@receiver(post_save, sender=BidEvaluation)
def bid_evaluation_notification(sender, instance, **kwargs):
    # Use correct notification task
    notify_procurement_bid_evaluation.delay(instance.tender.id)

@receiver(post_save, sender=TenderAmendment)
def tender_amendment_notification(sender, instance, **kwargs):
    if not kwargs.get('created', False):  # Trigger only on updates
        notify_vendors_of_amendment.delay(instance.tender.id)
