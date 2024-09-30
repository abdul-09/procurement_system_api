import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from api.models import User, VendorProfile

@pytest.mark.django_db
def test_vendor_registration():
    client = APIClient()
    
    # Data for vendor registration
    vendor_data = {
        "email": "vendor@example.com",
        "password": "password123",
        "vendor_profile": {
            "business_name": "Vendor Business",
            "contact_person": "John Doe",
            "phone_number": "1234567890",
            "address": "123 Vendor St",
            "tax_id": "AB123456",
            "business_license": None,  # Add file field if testing file upload
            "certification": None
        }
    }

    # POST request to register a vendor
    response = client.post(reverse('vendor-register'), vendor_data, format='json')

    # Check response status and data
    assert response.status_code == 201
    assert response.data["message"] == "Vendor registered successfully!"

    # Ensure the vendor was created
    user = User.objects.get(email="vendor@example.com")
    assert user is not None
    assert user.role == "vendor"

    vendor_profile = VendorProfile.objects.get(user=user)
    assert vendor_profile.business_name == "Vendor Business"
    assert vendor_profile.contact_person == "John Doe"
    assert vendor_profile.phone_number == "1234567890"
    assert vendor_profile.status == "pending"  # Vendor should be pending after registration
