import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestApprovalWorkflow:

    def test_create_approval_stage(self):
        client = APIClient()
        url = reverse('approvalstage-list')
        payload = {
            'name': 'initial',
            'order': 1
        }
        response = client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_approval_workflow(self, tender_fake, approval_stage_demo):
        
        client = APIClient()
        url = reverse('approvalworkflow-list')
        payload = {
            'approval_type': 'bid',
            'reference_id': tender_fake.id,
            'current_stage': approval_stage_demo.order
        }
        response = client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_approval_log(self, workflow_demo, approval_stage_demo, create_procurement_officer):
        user = create_procurement_officer
        client = APIClient()
        url = reverse('approvallog-list')
        payload = {
            'workflow': workflow_demo.id,
            'approved_by': user.id,
            'stage': approval_stage_demo.id,
            'comment': 'Approval given.'
        }
        response = client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
