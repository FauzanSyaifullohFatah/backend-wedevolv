from django.urls import path
from .views import CertificateView, CertificateDetailView

urlpatterns = [
    path("<int:pk>/", CertificateDetailView.as_view(), name="certificate-detail"),
    path("", CertificateView.as_view(), name="certificate-list-create"),
]