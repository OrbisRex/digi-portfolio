from django.urls import path

from .views import IndexView
from .views import DashboardView

app_name = 'core'
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]