from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Certificates
from .serializers import CertificatesSerializer

User = get_user_model()

class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        certificates = Certificates.objects.filter(user=request.user).order_by("-created_at")
        serializer = CertificatesSerializer(certificates, many=True)

        return  Response({
            "status": "success",
            "message": "Certificates retrieved successfully",
            "payload": serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CertificatesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "status": "success",
                "message": "Certificate created",
                "payload": serializer.data ,
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Failed to create certificate",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CertificateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Certificates.objects.get(pk=pk, user=user)
        except Certificates.DoesNotExist:
            return None

    def get(self, request, pk):
        certificate = self.get_object(pk, request.user)
        if not certificate:
            return Response({
                "status": "error",
                "message": "Certificate not found",
                "errors": None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CertificatesSerializer(certificate)
        return Response({
            "status": "success",
            "message": "Certificates retrieved successfully",
            "payload": serializer.data,
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        certificate = self.get_object(pk, request.user)
        if not certificate:
            return Response({
                "status": "error",
                "message": "Certificate not found",
                "errors": None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CertificatesSerializer(
            certificate,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Certificate update successfully",
                "payload": serializer.data,
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Failed to update certificate",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        certificate = self.get_object(pk, request.user)
        if not certificate:
            return Response({
                "status": "error",
                "message": "Certificate not found",
                "errors": None,
            }, status=status.HTTP_404_NOT_FOUND)

        certificate.delete()
        return Response({
            "status": "success",
            "message": "Certificate delete",
            "payload": None,
        }, status=status.HTTP_204_NO_CONTENT)