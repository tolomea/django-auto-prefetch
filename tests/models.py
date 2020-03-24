import auto_prefetch
from django.db import models


class Friend(models.Model):
    pass


class Associate(models.Model):
    number = models.IntegerField()


class Vanilla(models.Model):
    friend = models.ForeignKey(Friend, null=True, on_delete=models.CASCADE)
    associates = models.ManyToManyField(Associate)


class Prefetch(auto_prefetch.Model):
    friend = auto_prefetch.ForeignKey(Friend, null=True, on_delete=models.CASCADE)
    associates = models.ManyToManyField(Associate)
