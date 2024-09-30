import pytest
from rest_framework import status
from rest_framework.test import APIClient
from api.models import AuditLog, User


@pytest.mark.django_db
class TestAuditLogAPI:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(email='test1@example.com', password='testpass')

    @pytest.fixture
    def audit_log(self, user):
        return AuditLog.objects.create(action='Created tender', model_name='Tender', object_id=1, user=user)

    def test_create_audit_log(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/audit-logs/', {
            'action': 'Created contract',
            'model_name': 'Contract',
            'object_id': 1,
            'user': user.id,
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert AuditLog.objects.count() == 1
        assert AuditLog.objects.get().action == 'Created contract'

    def test_list_audit_logs(self, audit_log):
        client = APIClient()
        response = client.get('/audit-logs/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_audit_logs_by_user(self, audit_log, user):
        client = APIClient()
        response = client.get(f'/audit-logs/?user_id={user.id}')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
