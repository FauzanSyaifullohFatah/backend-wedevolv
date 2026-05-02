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
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            return Response(
                {"detail": "Project tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectsSerializer(project)
        return Response(serializer.data)

    def patch(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response(
                {"detail": "Project tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectsSerializer(
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
