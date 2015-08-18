from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=255)


class Question(models.Model):
    body = models.CharField(max_length=255)
    kind = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey)

    def __str__(self):
        return str(self.id)


class QuestionResponse(models.Model):
    response = models.CharField(max_length=255)
    call_sid = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    question = models.ForeignKey(Question)
