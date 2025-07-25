from django.urls import path

from . import views
from .views import IndexView
from .views import NewEditView
from .views import DetailView

app_name = 'projects'
urlpatterns = [
    path("assignment/", IndexView.as_view(), name="assignment-index"),
    path("assignment/subject_id=<int:subject_id>", IndexView.as_view(), name="assignment-index"),
    path("assignment/new", NewEditView.as_view(), name="assignment-new"),
    path("assignment/edit/<int:assignment_id>", NewEditView.as_view(), name="assignment-edit"),
    path("assignment/detail/<int:assignment_id>", DetailView.as_view(), name="assignment-detail"),
]