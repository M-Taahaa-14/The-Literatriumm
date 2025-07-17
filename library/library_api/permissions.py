from rest_framework import permissions
from library_app.models import UserProfile

class IsAdminUserProfile(permissions.BasePermission):
    """
    Allows access only to users with is_admin = True (from UserProfile).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.userprofile.is_admin
        except UserProfile.DoesNotExist:
            return False
