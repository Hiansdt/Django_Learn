from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Question(models.Model):
    question_text: models.CharField(max_length=250)
    pub_date: models.DateField('Date Published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

class Choice(models.Model):
    choice_text = models.CharField(max_length=250)
    votes = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    def __str__(self):
        return self.choice_text