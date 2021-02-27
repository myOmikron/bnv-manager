from django.contrib.auth.models import User
from django.db import models
from django.db.models import OneToOneField


class AdvancedUser(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)