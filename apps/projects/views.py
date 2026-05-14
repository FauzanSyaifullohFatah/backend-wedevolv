from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Projects
from .serializers import ProjectsSerializer

User = get_user_model()

class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Projects.objects.filter(user=request.user).order_by("-created_at")
        serializer = ProjectsSerializer(projects, many=True)
        return Response({
            "status": "success",
            "message": "Projects retrieved successfully",
            "payload": serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProjectsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "status": "success",
                "message": "Project created",
                "payload": serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Failed to create project",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Projects.objects.get(pk=pk, user=user)
        except Projects.DoesNotExist:
            return None

    def get(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response({
                "status": "error",
                "message": "Project not found",
                "errors": None,
            }, status.HTTP_404_NOT_FOUND)

        serializer = ProjectsSerializer(project)
        return Response({
            "status": "success",
            "message": "Project retrieved successfully",
            "payload": serializer.data,
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response({
                "status": "error",
                "message": "Project not found",
                "errors": None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectsSerializer(
            project,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Project updated successfully",
                "payload": serializer.data,
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Failed to update project",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response({
                "status": "error",
                "message": "Project not found",
                "errors": None,
            }, status=status.HTTP_404_NOT_FOUND)

        project.delete()
        return Response({
            "status": "success",
            "message": "Project delete",
            "payload": None,
        }, status=status.HTTP_204_NO_CONTENT)
