from django.urls import path

from Attendance.views import (
    RegularizationView,
    approve_regularization,
    reject_regularization,
)

urlpatterns = [
    path("regularizations/", RegularizationView.as_view(), name="regularization-list-create"),
    path("regularizations/<int:pk>/", RegularizationView.as_view(), name="regularization-detail"),
    path("regularizations/<int:pk>/approve/", approve_regularization, name="regularization-approve"),
    path("regularizations/<int:pk>/reject/", reject_regularization, name="regularization-reject"),
]
