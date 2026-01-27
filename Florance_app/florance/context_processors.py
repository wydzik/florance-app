def unread_notifications(request):
    if request.user.is_authenticated:
        return {
            "unread_notifications_count":
                request.user.powiadomienia.filter(is_read=False).count()
        }
    return {}
