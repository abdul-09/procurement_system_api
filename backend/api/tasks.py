from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from .notifications import send_sms_notification, send_email_notification
from .models import Notification, Tender, VendorProfile, User, TenderVendorNotification, Bid, Contract, ContractMilestone

@shared_task
def notify_supplier_about_inventory(supplier_email, message):
    send_mail(
        'Inventory Alert',
        message,
        'from@example.com',
        [supplier_email],
        fail_silently=False,
    )

@shared_task
def notify_vendors_of_new_tender(tender_id):
    try:
        tender = Tender.objects.get(id=tender_id)
    except Tender.DoesNotExist:
        return

    vendors = VendorProfile.objects.filter(user__is_active=True, status='approved')
    notifications = []
    tender_notifications = []
    
    for vendor in vendors:
        message = f"New Tender Published: {tender.title}. Check your dashboard for details."
        # send_sms_notification(vendor.phone_number, message)
        send_email_notification(vendor.user.email, "New Tender Published", message)
        
        notifications.append(
            Notification(
                user=vendor.user,
                message=message,
                notification_type='in_app'
            )
        )
        
        tender_notifications.append(
            TenderVendorNotification(
                tender=tender,
                vendor=vendor,
                notification_type='new_tender'
            )
        )

    Notification.objects.bulk_create(notifications)  # Bulk create notifications
    TenderVendorNotification.objects.bulk_create(tender_notifications)

@shared_task
def notify_vendors_of_amendment(tender_id):
    try:
        tender = Tender.objects.get(id=tender_id)
    except Tender.DoesNotExist:
        return

    vendors = VendorProfile.objects.filter(user__is_active=True, status='approved')
    notifications = []
    tender_notifications = []
    
    for vendor in vendors:
        message = f"Tender Amendment: {tender.title}. Check your dashboard for updates."
        # send_sms_notification(vendor.phone_number, message)
        send_email_notification(vendor.user.email, "Tender Amendment", message)
        
        notifications.append(
            Notification(
                user=vendor.user,
                message=message,
                notification_type='in_app'
            )
        )
        
        tender_notifications.append(
            TenderVendorNotification(
                tender=tender,
                vendor=vendor,
                notification_type='amendment'
            )
        )

    Notification.objects.bulk_create(notifications)
    TenderVendorNotification.objects.bulk_create(tender_notifications)
@shared_task
def close_expired_tenders():
    now = timezone.now()
    expired_tenders = Tender.objects.filter(is_closed=False, deadline__lt=now)
    for tender in expired_tenders:
        tender.close_tender()
        # Optionally notify vendors about closure
        # notify_vendors_of_tender_closure.delay(tender.id)

@shared_task
def notify_vendor_bid_submission(bid_id):
    bid = Bid.objects.get(id=bid_id)
    vendor_email = bid.vendor.user.email
    tender_title = bid.tender.title
    message = f"Your bid for the tender '{tender_title}' has been successfully submitted."
    
    send_mail(
        subject="Bid Submission Confirmation",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor_email]
    )
    Notification.objects.create(
            user = bid.vendor.user,
            message = message,
            notification_type = 'in_app'
        )

@shared_task
def notify_procurement_bid_evaluation(tender_id):
    try:
        tender = Tender.objects.get(id=tender_id)
    except Tender.DoesNotExist:
        return

    procurement_officers = User.objects.filter(role='procurement_officer')
    
    if not procurement_officers.exists():
        return  # No procurement officers to notify

    email_list = [officer.email for officer in procurement_officers]
    
    message = f"The bids for tender '{tender.title}' have been evaluated. Please review the results."
    
    # Send email to all procurement officers
    send_mail(
        subject="Bid Evaluation Completed",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=email_list
    )

    # Create notifications for each procurement officer
    notifications = [
        Notification(
            user=officer,
            message=message,
            notification_type='in_app'
        )
        for officer in procurement_officers
    ]
    
    Notification.objects.bulk_create(notifications)  # Bulk create notifications


@shared_task
def notify_expiring_contracts():
    contracts = Contract.objects.filter(end_date__lte=timezone.now() + timezone.timedelta(days=30))
    for contract in contracts:
        vendor_email = contract.bid.vendor.user.email
        send_mail(
            subject="Contract Expiring Soon",
            message=f"Your contract for bid {contract.bid.id} is expiring soon on {contract.end_date}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[vendor_email]
        )
        Notification.objects.create(
            user = contract.bid.vendor.user,
            message = f"Your contract for bid {contract.bid.id} is expiring soon on {contract.end_date}.",
            notification_type = 'in_app'
        )

@shared_task
def notify_upcoming_milestones():
    milestones = ContractMilestone.objects.filter(due_date__lte=timezone.now() + timezone.timedelta(days=7), completed=False)
    for milestone in milestones:
        vendor_email = milestone.contract.bid.vendor.user.email
        send_mail(
            subject="Upcoming Milestone Due",
            message=f"Your milestone '{milestone.description}' for contract {milestone.contract.id} is due on {milestone.due_date}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[vendor_email]
        )
        Notification.objects.create(
            user = milestone.contract.bid.vendor.user,
            message = f"Your milestone '{milestone.description}' for contract {milestone.contract.id} is due on {milestone.due_date}.",
            notification_type = 'in_app'
        )

@shared_task
def send_real_time_notification(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            'type': 'notify',
            'message': message
        }
    )
