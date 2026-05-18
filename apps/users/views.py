import uuid

import os
import requests
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, authenticate
from django.template.loader import render_to_string

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import make_password

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, UsersSerializer
from apps.projects.serializers import ProjectsSerializer
from apps.certificates.serializers import CertificatesSerializer

User = get_user_model()

def get_react_template():
    target = settings.REACT_INDEX_PATH

    if isinstance(target, str) and target.startswith("http"):
        try:
            response = requests.get(target, timeout=5)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            pass
    else:
        target_path = os.fspath(target)
        if os.path.exists(target_path):
            with open(target_path, 'r', encoding='utf-8') as file:
                return file.read()

    return None

def static_page_seo_view(request):
    path = request.path.strip('/')

    seo_data = {
        '': {
            'title': 'Wedevolv - Developer Portfolio Builder',
            'description': 'Build your professional developer portfolio on Wedevolv. The easiest way to showcase your projects, skills, and work experience to the world.'
        },
        'login': {
            'title': 'Login | Wedevolv',
            'description': 'Log in to your Wedevolv account to manage your developer portfolio.'
        },
        'register': {
            'title': 'Register | Wedevolv',
            'description': 'Start your journey on Wedevolv. Build your digital portfolio, showcase your best projects, and let others see the skills you have.'
        },
        'about': {
            'title': 'About Us | Wedevolv',
            'description': 'Learn more about Wedevolv, the platform designed to help developers build and showcase professional portfolios easily.'
        }
    }

    current_seo = seo_data.get(path, seo_data[''])
    title = current_seo['title']
    description = current_seo['description']

    frontend_url = settings.FRONTEND_URL.rstrip('/')
    image_url = f"{frontend_url}/og-image.png"

    html_content = get_react_template()
    if not html_content:
        return HttpResponse("Template Frontend Not Found", status=500)

    old_title = "<title>Wedevolv - Developer Portfolio Builder</title>"
    new_seo_tags = f"""<title>{title}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:url" content="{request.build_absolute_uri()}">
    <meta property="og:type" content="website">"""

    html_content = html_content.replace(old_title, new_seo_tags)

    html_content = html_content.replace("{{ frontend_url }}", frontend_url)

    return HttpResponse(html_content, content_type='text/html')

def portfolio_seo_view(request, username):
    user_obj = get_object_or_404(User, username=username)
    user_data = UsersSerializer(user_obj).data

    fullname = user_data.get('fullname')
    description = user_data.get('bio')

    raw_image = user_data.get('image')
    clean_image_path = raw_image.strip('/')
    backend_url = settings.BACKEND_URL.rstrip('/')
    image_url = f"{backend_url}/{clean_image_path}"

    title = f"{fullname} - Portfolio"
    html_content = get_react_template()
    if not html_content:
        return HttpResponse("Template Frontend Not Found", status=500)

    old_title = "<title>Wedevolv - Developer Portfolio Builder</title>"
    new_seo_tags = f"""<title>{title}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:url" content="{request.build_absolute_uri()}">
    <meta property="og:type" content="profile">"""

    html_content = html_content.replace(old_title, new_seo_tags)

    frontend_url = settings.FRONTEND_URL.rstrip('/')
    html_content = html_content.replace("{{ frontend_url }}", frontend_url)

    return HttpResponse(html_content, content_type='text/html')

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {
                    "status": "error",
                    "message": "invalid_credentials",
                    "errors": None,
                }, status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "status": "success",
                "message": "Login success",
                "payload": None
            }, status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite = settings.COOKIE_SAMESITE,
            max_age=15 * 60,
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=24 * 60 * 60,
            path="/",
        )

        return response

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {
                    "status": "error",
                    "message": "Refresh failed",
                    "errors": "No refresh token"
                }, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            old_token = RefreshToken(refresh_token)

            user_id = old_token["user_id"]
            user = User.objects.get(id=user_id)

            new_refresh = RefreshToken.for_user(user)
            new_access = new_refresh.access_token

            response = Response(
                {
                    "status": "success",
                    "message": "Token refreshed",
                    "payload": None,
                }, status=status.HTTP_200_OK
            )

            response.set_cookie(
                key="access_token",
                value=str(new_access),
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
                max_age=15 * 60,
                path="/",
            )

            response.set_cookie(
                key="refresh_token",
                value=str(new_refresh),
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
                max_age=7 * 24 * 60 * 60,
                path="/",
            )

            return response

        except TokenError:
            return Response(
                {
                    "status": "error",
                    "message": "Refresh failed",
                    "error": "Invalid or expired refresh token"
                }, status=status.HTTP_401_UNAUTHORIZED
            )

class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except:
                pass

        response = Response(
            {
                "status": "success",
                "message": "Logout successful",
                "payload": None,
            }, status=status.HTTP_200_OK
        )

        response.delete_cookie(
            "access_token",
            path="/",
            samesite=settings.COOKIE_SAMESITE,
        )

        response.delete_cookie(
            "refresh_token",
            path="/",
            samesite=settings.COOKIE_SAMESITE,
        )

        return response

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class SendVerificationLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user

            token = str(uuid.uuid4())
            user.verification_token = token
            user.save()

            lang = request.data.get("language")
            verify_url = f"{settings.BACKEND_URL}/api/auth/verify-email/?token={token}"
            subject = (
                "Verifikasi Email - Wedevolv"
                if lang == "id"
                else "Email Verification - Wedevolv"
            )
            message = (
                f"Klik link berikut untuk verifikasi email: {verify_url}"
                if lang == "id"
                else f"Click the following link to verify your email: {verify_url}")

            html_content = render_to_string(
                "emails/verification_email.html",
                {
                    "username": user.username,
                    "verify_url": verify_url,
                    "lang": lang,
                 },
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False,
            )

            return Response(
                {
                    "status": "success",
                    "message": "email_verification_success",
                    "payload:": None,
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({
                "status": "error",
                "message": "email_verification_not_sent",
                "errors": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return Response({
                "status": "error",
                "message": "Token not found",
                "errors": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(verification_token=token)
            user.is_verified = True
            user.verification_token = None
            user.save()

            return redirect(settings.FRONTEND_URL)

        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Token not valid",
                "errors": None,
            }, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsersSerializer(request.user)
        return Response({
            "status": "success",
            "message": "User authenticated",
            "payload": serializer.data,
        }, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UsersSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "profile_updated",
                "payload": serializer.data,
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Validation failed",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

class PublicPortfolioView(APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "User not found",
                    "errors": "Username does not match",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        projects = user.projects.all().order_by("-created_at")
        certificates = user.certificates.all().order_by("-created_at")
        return Response(
            {
                "status": "success",
                "message": "Portfolio found",
                "payload": {
                    "user": UsersSerializer(user).data,
                    "projects": ProjectsSerializer(projects, many=True).data,
                    "certificates": CertificatesSerializer(certificates, many=True).data,
                },
        }, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        lang = request.data.get("lang")

        try:
            user = User.objects.get(email=email)

            reset_token = uuid.uuid4()
            user.verification_token = reset_token
            user.save()

            reset_url = f"{settings.FRONTEND_URL}/confirm-password/{reset_token}"
            subject = (
                "Atur Ulang Kata Sandi - Wedevolv"
                if lang == "id"
                else "Reset Your Password - Wedevolv"
            )
            message = (
                f"Klik link berikut untuk reset password: {reset_url}"
                if lang == "id"
                else f"Click the following link to reset your password: {reset_url}"
            )
            html_content = render_to_string(
                "emails/password_reset.html",
                {
                    "username": user.username,
                    "reset_url": reset_url,
                    "lang": lang,
                }
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False,
            )
            return Response({
                "status": "success",
                "message": "email_reset_password_success",
                "payload": None,
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                "status": "error",
                "message": "email_reset_password_failed",
                "errors": None,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")

        # if not token or not new_password:
        #     return Response({"error": "Data tidak lengkap"}, status=400)

        if not token:
            return Response({
                "status": "error",
                "message": "Data tidak lengkap",
                "errors": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(verification_token=token)

            user.password = make_password(new_password)
            user.verification_token = None
            user.save()

            return Response({
                "status": "success",
                "message": "password_changed_success",
                "payload": None,
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                "status": "error",
                "message": "password_changed_failed",
                "errors": None,
            }, status=status.HTTP_400_BAD_REQUEST)

class AllUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = UsersSerializer(users, many=True)
        return Response(
            {
                "status": "success",
                "message": "Users retrieved successfully",
                "payload": serializer.data,
            }, status=status.HTTP_200_OK
        )