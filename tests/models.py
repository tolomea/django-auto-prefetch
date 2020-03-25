import auto_prefetch
from django.db import models


class Friend(models.Model):
    pass


class Associate(models.Model):
    number = models.IntegerField()


class Vanilla(models.Model):
    friend = models.ForeignKey(Friend, null=True, on_delete=models.CASCADE)
    associates = models.ManyToManyField(Associate)


class Vanilla2(models.Model):
    other = models.ForeignKey(Vanilla, null=True, on_delete=models.CASCADE)


class Prefetch(auto_prefetch.Model):
    friend = auto_prefetch.ForeignKey(Friend, null=True, on_delete=models.CASCADE)
    associates = models.ManyToManyField(Associate)


class Prefetch2(auto_prefetch.Model):
    other = auto_prefetch.ForeignKey(Prefetch, null=True, on_delete=models.CASCADE)


class MixedField(models.Model):
    friend = auto_prefetch.ForeignKey(Friend, null=True, on_delete=models.CASCADE)
    associates = models.ManyToManyField(Associate)


class MixedModel(auto_prefetch.Model):
    friend = models.ForeignKey(Friend, null=True, on_delete=models.CASCADE)
    associates = models.ManyToManyField(Associate)


class VanillaReverse(models.Model):
    pass


class VanillaForward(models.Model):
    friend = models.OneToOneField(
        VanillaReverse, on_delete=models.CASCADE, related_name="friend", null=True
    )


class PrefetchReverse(auto_prefetch.Model):
    pass


class PrefetchForward(auto_prefetch.Model):
    friend = auto_prefetch.OneToOneField(
        PrefetchReverse, on_delete=models.CASCADE, related_name="friend", null=True
    )
