from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from .models import Question,Response,Result,AssessmentSession,Field,Option
from django.contrib.auth.decorators import login_required
from .utils import calculate_result



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

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user =  form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "assessments/login.html", {"form":form})

def logout_view(request):
    logout(request)
    return redirect("landing")

def landing(request):
    return render(request, "assessments/landing.html")

def about(request):
    return render(request, "assessments/about.html")

def contact(request):
    if request.method == "POST":
        email =  request.POST.get("email")
        message = request.POST.get("message")
        print(f"Contact Form Submitted: {email} - {message}")
        return render(request, "assessments/contact.html", {"success": True})
    return render(request, "assessments/contact.html")

@login_required
def dashboard(request):
    return render(request, "assessments/dashboard.html")

@login_required
def start_assessment(request):
    session = AssessmentSession.objects.create(user=request.user)
    first_field = Field.ARTS
    return redirect("question_view", session_id=session.id, field=first_field)

@login_required
def question_view(request, session_id, field):
    session = get_object_or_404(AssessmentSession, id=session_id)
    questions = Question.objects.filter(field=field).order_by("id")

    # Get answered question IDs
    answered_ids = session.responses.filter(field=field).values_list("question_id", flat=True)
    question = questions.exclude(id__in=answered_ids).first()

    if not question:
        # No questions left in this field → move on
        all_fields = [f[0] for f in Field.choices]
        current_index = all_fields.index(field)
        if current_index + 1 < len(all_fields):
            next_field = all_fields[current_index + 1]
            return redirect("question_view", session_id=session.id, field=next_field)
        else:
            suggested, scores = calculate_result(session)
            return redirect("results", session_id=session.id)

    if request.method == "POST":
        qid = request.POST.get("question_id")
        selected_id = request.POST.get("option_id")

        # Safety check
        question_obj = get_object_or_404(Question, id=qid, field=field)
        option = get_object_or_404(Option, id=selected_id, question=question_obj)

        Response.objects.create(
            session=session,
            question=question_obj,
            selected=option,
            points=option.points,
            field=field,
        )

        return redirect("question_view", session_id=session.id, field=field)

    # Progress tracking
    total = questions.count()
    answered = len(answered_ids)
    progress = int((answered / total) * 100)
    is_last_question = (answered + 1 == total)

    return render(
        request,
        "assessments/test.html",
        {
            "session": session,
            "question": question,
            "progress": progress,
            "is_last_question": is_last_question,
        },
    )


@login_required
def results(request, session_id):
    session = AssessmentSession.objects.get(id=session_id)
    result = session.result  # already created in calculate_result
    return render(request, "assessments/result.html", {"result": result})


