from django.urls import path

from Notifications.views import NotificationView, mark_all_read, mark_read, unread_count

urlpatterns = [
    path("", NotificationView.as_view(), name="notification-list"),
    path("unread-count/", unread_count, name="notification-unread-count"),
    path("<int:pk>/read/", mark_read, name="notification-mark-read"),
    path("read-all/", mark_all_read, name="notification-mark-all-read"),
]
