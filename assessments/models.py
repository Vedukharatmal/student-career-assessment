from django.conf import settings
from django.db import models


class Field(models.Textchoices):
    ARTS = "ART", "Arts"
    SCIENCE = "SCI", "Science"
    COMMERCE = "COM", "Commerce"
    CIVIL = "CIV", "Civil Engineering"
    ELECTRICAL = "ELE", "Electrical Engineering"
    COMPUTER = "CSE", "Computer Engineering"
    MECHANICAL = "MEC", "Mechanical Engineering"
    ELECTRONICS = "ECE", "Electronics Engineering"

class Question(models.Model):
    field = models.CharField(max_length=3, choices=Field.choices)
    text = models.TextField()

class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    points = models.IntegerField(default=0)

class AssessmentSession(models.MOdel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class Response(models.Model):
    session = models.ForeignKey(AssessmentSession, related_name="responses", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected = models.ForeignKey(Option, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    field = models.CharField(max_length=3, choices=Field.choices)

class Result(models.Model):
    session = models.OneToOneField(AssessmentSession, on_delete=models.CASCADE, related_name="result")
    suggested_field = models.CharField(max_length=3, choices=Field.choices)
    scores = models.JSONField(default=dict)

