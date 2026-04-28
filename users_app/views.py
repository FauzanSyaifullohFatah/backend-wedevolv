import uuid
from http.client import responses

from django.conf import settings
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Project, Certificate
from .serializers import RegisterSerializer, ProjectSerializer, CertificateSerializer, UserSerializer

# Create your views here.

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.filter(username=username).first()
        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })

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

        verify_url = f"http://localhost:8000/api/verify-email/?token={token}"

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
        serializer = UserSerializer(request.user)

        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.filter(user=request.user).order_by("-created_at")
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Project.objects.get(pk=pk, user=user)
        except Project.DoesNotExist:
            return None

    def get(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response(
                {"detail": "Project tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response(
                {"detail": "Project tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectSerializer(
            project,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response(
                {"detail": "Project tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        project.delete()
        return Response(
            {"detail": "Project berhasil dihapus"},
            status=status.HTTP_204_NO_CONTENT
        )

class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        certificates = Certificate.objects.filter(user=request.user).order_by("-created_at")
        serializer = CertificateSerializer(certificates, many=True)

        return  Response(serializer.data)

    def post(self, request):
        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CertificateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Certificate.objects.get(pk=pk, user=user)
        except Certificate.DoesNotExist:
            return None

    def get(self, request, pk):
        certificate = self.get_object(pk, request.user)
        if not certificate:
            return Response(
                {"detail": "Certificate tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)

    def patch(self, request, pk):
        certificate = self.get_object(pk, request.user)
        if not certificate:
            return Response(
                {"detail": "Certificate tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CertificateSerializer(
            certificate,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        certificate = self.get_object(pk, request.user)
        if not certificate:
            return Response(
                {"detail": "Certificate tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        certificate.delete()
        return Response(
            {"detail": "Certificate berhasil dihapus"},
            status=status.HTTP_204_NO_CONTENT
        )

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
            "user": UserSerializer(user).data,
            "projects": ProjectSerializer(projects, many=True).data,
            "certificates": CertificateSerializer(certificates, many=True).data,
        })
