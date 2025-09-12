from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = {
    path("signup/", views.signup_view, name="signup"),
    path("", views.dashboard, name="dashboard"),
}