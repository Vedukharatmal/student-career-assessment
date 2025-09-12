from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Question,Response,Result,AssessmentSession,Field
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "assessments/signup.html", {"form":form})

@login_required
def dashboard(request):
    return render(request, "assessments/dashboard.html  ")