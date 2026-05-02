from django.urls import path
from .views import ProjectView, ProjectDetailView

urlpatterns = [
    path("<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("", ProjectView.as_view(), name="project-list-create"),
]