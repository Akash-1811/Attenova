from django.urls import path
from Organization.views import OrganizationView

urlpatterns = [
    path("", OrganizationView.as_view(), name="organization-list-create"),
    path("<int:pk>/", OrganizationView.as_view(), name="organization-detail"),
]
