import uuid
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, authenticate

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

class LoginView(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {"message": "Login successful!"},
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,   # True kalau HTTPS
            samesite="Lax",
            max_age=15 * 60,
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=24 * 60 * 60,
            path="/",
        )

        return response

class RefreshTokenView(APIView):

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"error": "No refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            old_token = RefreshToken(refresh_token)

            user_id = old_token["user_id"]
            user = User.objects.get(id=user_id)

            new_refresh = RefreshToken.for_user(user)
            new_access = new_refresh.access_token

            response = Response(
                {"message": "Token refreshed"},
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key="access_token",
                value=str(new_access),
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=15 * 60,
                path="/",
            )

            response.set_cookie(
                key="refresh_token",
                value=str(new_refresh),
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,
                path="/",
            )

            return response

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
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
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

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
        user = request.user

        token = str(uuid.uuid4())
        user.verification_token = token
        user.save()

        verify_url = f"http://localhost:8000/api/auth/verify-email/?token={token}"

        send_mail(
            subject="Verifikasi Email",
            message="Silakan buka email ini di browser (HTML support required)",
            from_email="wedevolv@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
            html_message=f"""
                <div style="font-family: Arial, sans-serif; padding: 24px; background:#f9fafb;">
                    <div style="max-width:500px;margin:auto;background:white;padding:24px;border-radius:10px;">

                        <h2 style="color:#4F46E5;">Verifikasi Email Kamu</h2>

                        <p>Halo <b>{user.username}</b>,</p>

                        <p>Klik tombol di bawah untuk verifikasi akun kamu:</p>

                        <a href="{verify_url}"
                           style="
                                display:inline-block;
                                padding:12px 20px;
                                background:#4F46E5;
                                color:white;
                                text-decoration:none;
                                border-radius:8px;
                                margin-top:10px;
                                font-weight:bold;
                           ">
                            Verifikasi Email
                        </a>

                        <p style="margin-top:20px;font-size:12px;color:gray;">
                            Jika kamu tidak merasa membuat akun, abaikan email ini.
                        </p>
                    </div>
                </div>
            """,
        )

        return Response({"message": "Berhasil"})

class VerifyEmailView(APIView):

    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return Response({"error": "Token tidak ada"}, status=400)

        try:
            user = User.objects.get(verification_token=token)
            user.is_verified = True
            user.verification_token = None
            user.save()

            return redirect("http://localhost:5173/")

        except User.DoesNotExist:
            return Response({"error": "Token tidak valid"}, status=400)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsersSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UsersSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

class PublicPortfolioView(APIView):

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"message": "User tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        projects = user.projects.all().order_by("-created_at")
        certificates = user.certificates.all().order_by("-created_at")

        return Response({
            "user": UsersSerializer(user).data,
            "projects": ProjectsSerializer(projects, many=True).data,
            "certificates": CertificatesSerializer(certificates, many=True).data,
        })

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)

            reset_token = uuid.uuid4()
            user.verification_token = reset_token
            user.save()

            reset_url = f"http://localhost:5173/confirm-password/{reset_token}"

            send_mail(
                subject="Atur Ulang Kata Sandi - Wedevolv",
                message=f"Klik link berikut untuk reset password: {reset_url}",
                from_email="wedevolv@gmail.com",
                recipient_list=[user.email],
                html_message=f"""
                    <div style="font-family: sans-serif; max-width: 500px; margin: auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                        <h2 style="color: #4F46E5;">Reset Kata Sandi</h2>
                        <p>Halo <b>{user.username}</b>,</p>
                        <p>Kami menerima permintaan reset password. Silakan klik tombol di bawah:</p>
                        <a href="{reset_url}" style="display: inline-block; padding: 10px 20px; background: #4F46E5; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Atur Ulang Password</a>
                        <p style="margin-top: 20px; font-size: 12px; color: #666;">Abaikan email ini jika Anda tidak merasa melakukan permintaan ini.</p>
                    </div>
                """
            )
            return Response({"message": "Link reset password telah dikirim."})
        except User.DoesNotExist:
            return Response({"message": "Jika email terdaftar, link akan dikirim."})

class PasswordResetConfirmView(APIView):
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not token or not new_password:
            return Response({"error": "Data tidak lengkap"}, status=400)

        try:
            user = User.objects.get(verification_token=token)

            user.password = make_password(new_password)
            user.verification_token = None
            user.save()

            return Response({"message": "Password berhasil diubah. Silakan login."})
        except (User.DoesNotExist, ValueError):
            return Response({"error": "Token tidak valid atau sudah kadaluwarsa"}, status=400)

class AllUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = UsersSerializer(users, many=True)
        return Response({"users": serializer.data})