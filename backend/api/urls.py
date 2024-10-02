import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.views.static import serve
from .views import *
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register(r'tenders', TenderViewSet, basename='tender')
router.register(r'tender-amendments', TenderAmendmentViewSet, basename='tenderamendment')
router.register(r'bids', BidViewSet, basename = 'bid')
router.register(r'evaluation-criteria', EvaluationCriteriaViewSet, basename = 'evaluationcriteria')
router.register(r'bid-evaluations', BidEvaluationViewSet, basename = 'bidevaluation')
router.register(r'bid-scores', BidScoreViewSet, basename = 'bidscore')
router.register(r'contracts', ContractViewSet, basename = 'contracts')
router.register(r'contract-milestones', ContractMilestoneViewSet, basename = 'contractmilestone')
router.register(r'contract-amendments', ContractAmendmentViewSet, basename = 'contractammendment')
router.register(r'vendor-performance', VendorContractPerformanceViewSet, basename = 'vendorcontractperformance')
router.register(r'approval-stages', ApprovalStageViewSet, basename = 'approvalstage')
router.register(r'approval-workflows', ApprovalWorkflowViewSet, basename = 'approvalworkflow')
router.register(r'approval-logs', ApprovalLogViewSet, basename = 'approvallog')
router.register(r'tender-reports', TenderReportViewSet, basename = 'tenderreport')
router.register(r'notifications', NotificationViewSet, basename = 'notifications')
router.register(r'notification-preferences', NotificationPreferencesViewSet, basename = 'notificationpreferences')
router.register(r'vendor-performance', VendorPerformanceViewSet, basename = 'vendorperformance')
router.register(r'spend-analytics', SpendAnalyticsViewSet, basename = 'spendanalytics')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlogs')

doc_path = os.path.join(os.path.dirname(__file__), 'docs/_build/html')


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/docs/$', serve, {'path': 'index.html', 'document_root': doc_path}),    
    # Serve other Sphinx documentation files
    re_path(r'^api/docs/(?P<path>.*)$', serve, {'document_root': doc_path}),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('email-verify/', EmailVerificationView.as_view(), name='email-verification'),
    path('email-verify/<uidb64>/<token>/', EmailVerificationConfirmView.as_view(), name='email-verify'),
    path('roles/create/', RoleCreateView.as_view(), name='role-create'),  # Optional
    path('assign-role/', AssignRoleView.as_view(), name='assign-role'),
    path('user/<int:user_id>/roles/', UserRolesListView.as_view(), name='user-roles'),
    path('vendor/register/', VendorRegistrationView.as_view(), name='vendor-register'),
    path('<int:pk>/approve/', VendorApprovalView.as_view(), name='vendor-approve'),
    path('', include(router.urls)),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)