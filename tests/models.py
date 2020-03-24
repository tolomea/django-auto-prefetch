import auto_prefetch
from django.db import models


class Friend(models.Model):
    pass


class Vanilla(models.Model):
    friend = models.ForeignKey(Friend, on_delete=models.CASCADE)


class Prefetch(auto_prefetch.Model):
    friend = auto_prefetch.ForeignKey(Friend, on_delete=models.CASCADE)
