from django.urls import path
from Shifts.views import ShiftView

urlpatterns = [
    path("", ShiftView.as_view(), name="shift-list-create"),
    path("<int:pk>/", ShiftView.as_view(), name="shift-detail"),
]
