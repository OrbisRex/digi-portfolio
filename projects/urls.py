from django.urls import path

from . import views
from .views import AssignmentIndexView
from .views import AssignmentNewEditView
from .views import AssignmentDetailView
from .views import AssignmentAddCriteriaView
from .views import CriterionNewEditView
from .views import DescriptorNewEditView

app_name = 'projects'
urlpatterns = [
    path("assignment/", AssignmentIndexView.as_view(), name="assignment-index"),
    path("assignment/subject_id=<int:subject_id>", AssignmentIndexView.as_view(), name="assignment-subject"),
    path("assignment/topic_id=<int:topic_id>", AssignmentIndexView.as_view(), name="assignment-topic"),
    path("assignment/new", AssignmentNewEditView.as_view(), name="assignment-new"),
    path("assignment/edit/<int:assignment_id>", AssignmentNewEditView.as_view(), name="assignment-edit"),
    path("assignment/detail/<int:assignment_id>", AssignmentDetailView.as_view(), name="assignment-detail"),
    path("assignment/add/<int:assignment_id>", AssignmentAddCriteriaView.as_view(), name="criteria-add"),
    path("criterion/new", CriterionNewEditView.as_view(), name="criterion-new"),
    path("criterion/edit/<int:criterion_id>", CriterionNewEditView.as_view(), name="criterion-edit"),
    path("descriptor/new", DescriptorNewEditView.as_view(), name="descriptor-new"),
    path("descriptor/edit/<int:descriptor_id>", DescriptorNewEditView.as_view(), name="descriptor-edit"),
]