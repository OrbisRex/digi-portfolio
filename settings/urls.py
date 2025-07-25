from django.urls import path

from .views import IndexView
from .views import SubjectView
from .views import TopicView
from .views import GroupView

app_name = 'settings'
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("subject/new", SubjectView.as_view(), name="new-subject"),
    path("subject/<int:subject_id>", SubjectView.as_view(), name="subject"),
    path("topic/new", TopicView.as_view(), name="new-topic"),
    path("topic/<int:topic_id>", TopicView.as_view(), name="topic"),
    path("group/<int:group_id>", GroupView.as_view(), name="group"),
]