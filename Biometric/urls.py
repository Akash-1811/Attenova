from django.urls import path

from Biometric import views

urlpatterns = [
    path("devices/", views.BiometricDeviceView.as_view(), name="biometric-device-list-create"),
    path("devices/<int:pk>/", views.BiometricDeviceView.as_view(), name="biometric-device-detail"),
    path("essl-logs/", views.essl_device_logs, name="essl-device-logs"),
]
