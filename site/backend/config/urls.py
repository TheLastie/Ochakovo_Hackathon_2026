from django.urls import path
from career.admin import site
from career.views import Applications, index

urlpatterns = [
    path('', index),
    path('admin102/', site.urls),
    path('api/v1/applications/', Applications.as_view()),
]
