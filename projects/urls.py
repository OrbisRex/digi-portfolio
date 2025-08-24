from django.urls import path

from . import views
from .views import AssignmentIndexView
from .views import AssignmentNewEditView
from .views import AssignmentDetailView
from .views import AssignmentAddCriteriaView
from .views import CriterionNewEditView
from .views import DescriptorNewEditView
from .views import SubmissionIndexView
from .views import SubmissionDetailView
from .views import SubmissionNewFilesView
from .views import SubmissionNewEditView

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
    path("submission/", SubmissionIndexView.as_view(), name="submission-index"),
    path("submission/subject_id=<int:subject_id>", SubmissionIndexView.as_view(), name="submission-subject"),
    path("submission/topic_id=<int:topic_id>", SubmissionIndexView.as_view(), name="submission-topic"),
    path("submission/detail/<int:submission_id>", SubmissionDetailView.as_view(), name="submission-detail"),
    path("submission/file", SubmissionNewFilesView.as_view(), name="submission-file"),
    path("submission/new", SubmissionNewEditView.as_view(), name="submission-new"),
    path("submission/edit/<int:submission_id>", SubmissionNewEditView.as_view(), name="submission-edit"),
]