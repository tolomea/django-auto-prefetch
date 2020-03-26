from weakref import WeakValueDictionary

from django.db import models
from django.db.models.fields import related_descriptors


class DescriptorMixin:
    def _field_name(self):
        return self.field.name

    def _is_cached(self, instance):
        return self.is_cached(instance)

    def _should_prefetch(self, instance):
        return (
            instance is not None  # getattr on the model class passes None to the descriptor
            and not self._is_cached(instance)  # already loaded
            and len(getattr(instance, "_peers", [])) >= 2  # no peers no prefetch
        )

    def __get__(self, instance, instance_type=None):
        if self._should_prefetch(instance):
            prefetch = models.query.Prefetch(self._field_name())
            peers = [p for p in instance._peers.values() if not self._is_cached(p)]
            models.query.prefetch_related_objects(peers, prefetch)
        return super().__get__(instance, instance_type)


class ForwardDescriptorMixin(DescriptorMixin):
    def _should_prefetch(self, instance):
        return (
            super()._should_prefetch(instance)
            and None not in self.field.get_local_related_value(instance)  # field is null
        )


class ForwardManyToOneDescriptor(
    ForwardDescriptorMixin, related_descriptors.ForwardManyToOneDescriptor
):
    pass


class ForwardOneToOneDescriptor(
    ForwardDescriptorMixin, related_descriptors.ForwardOneToOneDescriptor
):
    pass


class ReverseOneToOneDescriptor(
    DescriptorMixin, related_descriptors.ReverseOneToOneDescriptor
):
    def _is_cached(self, instance):
        return self.related.is_cached(instance)

    def _field_name(self):
        return self.related.get_accessor_name()


class ForeignKey(models.ForeignKey):
    forward_related_accessor_class = ForwardManyToOneDescriptor


class OneToOneField(models.OneToOneField):
    forward_related_accessor_class = ForwardOneToOneDescriptor
    related_accessor_class = ReverseOneToOneDescriptor


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
        base_manager_name = "prefetch_manager"

    prefetch_manager = Manager()
    objects = Manager()
