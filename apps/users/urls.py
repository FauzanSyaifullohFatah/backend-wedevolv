from django.urls import path
from .views import (
    LoginView,
    RefreshTokenView,
    LogoutView,
    RegisterView,
    ProfileView,
    PublicPortfolioView,
    SendVerificationLinkView,
    VerifyEmailView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshTokenView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("register/", RegisterView.as_view()),
    path("send-verification-link/", SendVerificationLinkView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path("profile/", ProfileView.as_view()),
    path("portfolio/<str:username>/", PublicPortfolioView.as_view()),
]