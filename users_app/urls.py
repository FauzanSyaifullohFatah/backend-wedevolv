from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    ProfileView,
    ProjectView,
    ProjectDetailView,
    CertificateView,
    CertificateDetailView,
    PublicPortfolioView,
    SendVerificationLinkView,
    VerifyEmailView,
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("register/", RegisterView.as_view()),
    path("send-verification-link/", SendVerificationLinkView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),

    path("profile/", ProfileView.as_view()),

    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("projects/", ProjectView.as_view(), name="project-list-create"),

    path("certificates/<int:pk>/", CertificateDetailView.as_view(), name="certificate-detail"),
    path("certificates/", CertificateView.as_view(), name="certificate-list-create"),

    path("portfolio/<str:username>/", PublicPortfolioView.as_view()),
]