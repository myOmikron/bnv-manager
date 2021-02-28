from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import OneToOneField, ManyToManyField, CharField


class Domain(models.Model):
    name = CharField(max_length=255, default="")


class AdvancedUser(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)


class AdvancedGroup(models.Model):
    model = OneToOneField(Group, on_delete=models.CASCADE)
    associated_domains = ManyToManyField(Domain)
