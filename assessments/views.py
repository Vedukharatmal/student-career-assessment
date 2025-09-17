from django.shortcuts import render,redirect,get_object_or_404
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
    return redirect("questions_view", session_id=session.id, field=first_field)

@login_required
def question_view(request, session_id, field):
    session = AssessmentSession.objects.get(id=session_id)
    questions = Question.objects.filter(field=field)

    if request.method == "POST":
        qid = request.POST.get("question_id")
        selected_id = request.POST.get("option_id")
        question = Question.objects.get(id=qid)
        option = Option.objects.get(id=selected_id)
        Response.objects.create(
            session=session,
            question=question,
            selected=option,
            points=option.points,
            field=field,
        )
        # move to next question
        next_q = questions.exclude(
            id__in=session.responses.filter(field=field).values_list("question_id", flat=True)
        ).first()
        if next_q:
            return render(request, "assessments/question.html", {"session": session, "question": next_q})
        else:
            # all questions done → next field
            all_fields = [f[0] for f in Field.choices]
            current_index = all_fields.index(field)
            if current_index + 1 < len(all_fields):
                next_field = all_fields[current_index + 1]
                return redirect("question_view", session_id=session.id, field=next_field)
            else:
                # assessment finished
                suggested, scores = calculate_result(session)
                return redirect("results", session_id=session.id)

    # show first unanswered question of field
    answered_ids = session.responses.filter(field=field).values_list("question_id", flat=True)
    question = questions.exclude(id__in=answered_ids).first()
    return render(request, "assessments/question.html", {"session": session, "question": question})

@login_required
def results(request, session_id):
    session = AssessmentSession.objects.get(id=session_id)
    result = session.result  # already created in calculate_result
    return render(request, "assessments/results.html", {"result": result})


