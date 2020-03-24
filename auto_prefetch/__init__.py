from weakref import WeakValueDictionary

from django.db import models
from django.db.models.fields import related_descriptors


class ForwardManyToOneDescriptor(related_descriptors.ForwardManyToOneDescriptor):
    def _should_prefetch(self, instance):
        if instance is None:  # getattr on the model class passes None to the descriptor
            return False
        if self.is_cached(instance):  # already loaded
            return False
        if None in self.field.get_local_related_value(instance):  # field is null
            return False
        if len(getattr(instance, "_peers", [])) < 2:  # no peers no prefetch
            return False
        return True

    def __get__(self, instance, instance_type=None):
        if self._should_prefetch(instance):
            prefetch = models.query.Prefetch(self.field.name)
            peers = [p for p in instance._peers.values() if not self.is_cached(p)]
            models.query.prefetch_related_objects(peers, prefetch)
        return super().__get__(instance, instance_type)


class ForeignKey(models.ForeignKey):
    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, ForwardManyToOneDescriptor(self))


class QuerySet(models.QuerySet):
    def _fetch_all(self):
        set_peers = self._result_cache is None
        super()._fetch_all()
        # ModelIterable tests for query sets returning model instances vs values or value lists etc
        if set_peers and issubclass(self._iterable_class, models.query.ModelIterable):
            peers = WeakValueDictionary((id(o), o) for o in self._result_cache)
            for peer in peers.values():
                peer._peers = peers


Manager = models.Manager.from_queryset(QuerySet)


class Model(models.Model):
    class Meta:
        abstract = True

    objects = Manager()
    base_manager = Manager()
