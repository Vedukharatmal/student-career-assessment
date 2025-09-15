from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("start/<int:session_id>/<str:field>/", views.question_view, name="question_view"),
    path("start-assessment/", views.start_assessment, name="start_assessment"),
    path("results/<int:session_id>/", views.results, name="results"),
]
