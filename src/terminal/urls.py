from django.urls import path
from . import views


app_name = "terminal"


urlpatterns = [path("", views.index, name="index")]
