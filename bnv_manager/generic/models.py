from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Domain(models.Model):
    domain = models.CharField(default="", max_length=255, unique=True)


class Club(models.Model):
    abbreviation = models.CharField(
        default="",
        max_length=16,
        unique=True,
        validators=[RegexValidator(regex=r"^[a-zA-Z0-9]+$")]
    )
    name = models.CharField(default="", max_length=1024, unique=True)
    associated_domains = models.ManyToManyField(Domain, blank=True)
