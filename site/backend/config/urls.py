from django.urls import path
from career.admin import site
from career.views import index, Applications, Events
urlpatterns = [
    path(
        '',
        index),
    path(
        'admin102/',
        site.urls),
    path(
        'api/v1/applications/',
        Applications.as_view()),
    path(
        'api/v1/events/',
        Events.as_view())]
