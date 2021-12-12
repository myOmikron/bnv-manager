from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Club(models.Model):
    abbreviation = models.CharField(default="", max_length=16, validators=[RegexValidator(regex=r"^[a-zA-Z0-9]+$")])
    name = models.CharField(default="", max_length=1024)
    associated_managers = models.ManyToManyField(User, blank=True)
