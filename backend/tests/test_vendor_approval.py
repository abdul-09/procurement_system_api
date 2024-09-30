import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from api.models import User, VendorProfile

@pytest.mark.django_db
def create_vendor_for_approval():
    # Helper function to create a vendor for testing approval
    vendor_user = User.objects.create_user(email="vendor@example.com", password="password123", role="vendor")
    vendor_profile = VendorProfile.objects.create(
        user=vendor_user,
        business_name="Vendor Business",
        contact_person="John Doe",
        phone_number="1234567890",
        address="123 Vendor St",
        tax_id="AB123456",
        status="pending"
    )
    return vendor_profile

@pytest.mark.django_db
def test_vendor_approval():
    client = APIClient()

    # Create a procurement officer
    officer_user = User.objects.create_user(email="officer@example.com", password="password123", role="procurement_officer", is_staff=True)
    
    # Create vendor for approval
    vendor_profile = create_vendor_for_approval()

    # Officer logs in
    client.force_authenticate(user=officer_user)

    # Approve the vendor
    response = client.put(reverse('vendor-approve', args=[vendor_profile.id]), {"status": "approved"}, format='json')

    # Check response
    assert response.status_code == 200
    assert response.data["message"] == "Vendor approved successfully!"

    # Ensure vendor status is updated
    vendor_profile.refresh_from_db()
    assert vendor_profile.status == "approved"

@pytest.mark.django_db
def test_invalid_vendor_approval_status():
    client = APIClient()

    # Create a procurement officer
    officer_user = User.objects.create_user(email="officer@example.com", password="password123", role="procurement_officer", is_staff=True)
    
    # Create vendor for approval
    vendor_profile = create_vendor_for_approval()

    # Officer logs in
    client.force_authenticate(user=officer_user)

    # Try to set invalid status
    response = client.put(reverse('vendor-approve', args=[vendor_profile.id]), {"status": "invalid_status"}, format='json')

    # Check response
    assert response.status_code == 400
    assert response.data["error"] == "Invalid status"

@pytest.mark.django_db
def test_vendor_rejection():
    client = APIClient()

    # Create a procurement officer
    officer_user = User.objects.create_user(email="officer@example.com", password="password123", role="procurement_officer", is_staff=True)
    
    # Create vendor for rejection
    vendor_profile = create_vendor_for_approval()

    # Officer logs in
    client.force_authenticate(user=officer_user)

    # Reject the vendor
    response = client.put(reverse('vendor-approve', args=[vendor_profile.id]), {"status": "rejected"}, format='json')

    # Check response
    assert response.status_code == 200
    assert response.data["message"] == "Vendor rejected successfully!"

    # Ensure vendor status is updated
    vendor_profile.refresh_from_db()
    assert vendor_profile.status == "rejected"
