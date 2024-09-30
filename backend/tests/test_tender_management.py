import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Tender, TenderAmendment, User, VendorProfile

@pytest.fixture
def create_procurement_officer():
    """Fixture to create a procurement officer for testing."""
    return User.objects.create_user(
        email='officer@example.com',
        password='password123',
        role='procurement_officer',
        is_staff=True
    )

@pytest.mark.django_db
def test_create_tender(api_client, create_procurement_officer):
    officer = create_procurement_officer
    api_client.force_authenticate(user=officer)

    tender_data = {
        "title": "Office Supplies",
        "description": "Procurement of office supplies for Q3.",
        "tender_type": "open",
        "deadline": "2030-12-31T23:59:59Z"
    }

    response = api_client.post(reverse('tender-list'), tender_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == "Office Supplies"
    assert response.data['is_published'] is False
    assert response.data['is_closed'] is False

@pytest.mark.django_db
def test_publish_tender(api_client, create_procurement_officer):
    officer = create_procurement_officer
    api_client.force_authenticate(user=officer)

    tender = Tender.objects.create(
        title="Office Supplies",
        description="Procurement of office supplies for Q3.",
        tender_type="open",
        created_by=officer,
        deadline="2030-12-31T23:59:59Z"
    )

    publish_url = reverse('tender-publish', args=[tender.id])
    response = api_client.post(publish_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == "Tender published successfully."
    tender.refresh_from_db()
    assert tender.is_published is True

@pytest.mark.django_db
def test_amend_tender(api_client, create_procurement_officer):
    officer = create_procurement_officer
    api_client.force_authenticate(user=officer)

    tender = Tender.objects.create(
        title="Office Supplies",
        description="Procurement of office supplies for Q3.",
        tender_type="open",
        created_by=officer,
        deadline="2030-12-31T23:59:59Z"
    )

    amendment_data = {
        "tender": tender.id,
        "amendment_details": "Extended the deadline by one week."
    }

    response = api_client.post(reverse('tenderamendment-list'), amendment_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['amendment_details'] == "Extended the deadline by one week."
    assert response.data['amended_by'] == officer.id

@pytest.mark.django_db
def test_close_tender(api_client, create_procurement_officer):
    officer = create_procurement_officer
    api_client.force_authenticate(user=officer)

    tender = Tender.objects.create(
        title="Office Supplies",
        description="Procurement of office supplies for Q3.",
        tender_type="open",
        created_by=officer,
        deadline="2030-12-31T23:59:59Z"
    )

    close_url = reverse('tender-close', args=[tender.id])
    response = api_client.post(close_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == "Tender closed successfully."
    tender.refresh_from_db()
    assert tender.is_closed is True
