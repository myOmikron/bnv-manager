from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import OneToOneField, ManyToManyField, CharField


class Domain(models.Model):
    name = CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class AdvancedUser(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class AdvancedGroup(models.Model):
    group = OneToOneField(Group, on_delete=models.CASCADE)
    associated_domains = ManyToManyField(Domain)

    def __str__(self):
        return self.group.name
