from django.db import models
from django.conf import settings

USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


# Create your models here.
class Chat(models.Model):
    id = models.IntegerField(primary_key=True, serialize=True)
    user = models.ForeignKey(USER_MODEL, null=True, on_delete=models.DO_NOTHING)
    pdf_url = models.TextField()
    pdf_name = models.CharField(max_length=1024)

    file_key = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True, serialize=True)
    chat = models.ForeignKey(Chat, on_delete=models.DO_NOTHING)
    message = models.TextField()
    role = models.TextField()
