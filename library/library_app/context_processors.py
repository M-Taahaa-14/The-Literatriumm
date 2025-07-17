from .models import UserProfile

def profile_context(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return {'profile': profile}
        except UserProfile.DoesNotExist:
            return {}
    return {}

from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        return {
            'notifications': Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
        }
    return {'notifications': []}

def notifications_filter(request):
    if request.user.is_authenticated:
        all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        unread_count = all_notifications.filter(is_read=False).count()
        return {
            'notifications': all_notifications,
            'unread_count': unread_count
        }
    return {}