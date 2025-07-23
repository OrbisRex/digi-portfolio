from django.urls import path

from . import views
from .views import IndexView
from .views import NewEditView
from .views import DetailView

app_name = 'assignment'
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("subject_id=<int:subject_id>", IndexView.as_view(), name="index"),
    path("new", NewEditView.as_view(), name="new"),
    path("edit/<int:assignment_id>", NewEditView.as_view(), name="edit"),
    path("detail/<int:assignment_id>", DetailView.as_view(), name="detail"),
]