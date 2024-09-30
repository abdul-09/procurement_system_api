from rest_framework import permissions
from .models import UserRole

class IsProcurementOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the 'procurement_officer' role
        return UserRole.objects.filter(user=request.user, role__name='procurement_officer').exists()

class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the 'vendor' role
        return UserRole.objects.filter(user=request.user, role__name='vendor').exists()

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the 'admin' role
        return UserRole.objects.filter(user=request.user, role__name='admin').exists()
