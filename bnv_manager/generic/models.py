from django.contrib.auth.models import User
from django.db import models


class Club(models.Model):
    name = models.CharField(default="", max_length=1024)
    associated_managers = models.ManyToManyField(User, blank=True)
