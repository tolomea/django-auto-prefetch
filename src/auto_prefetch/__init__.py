from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type
from weakref import WeakValueDictionary

from django.core import checks
from django.db import models
from django.db.models.fields import related_descriptors

if TYPE_CHECKING:  # pragma: no cover

    class DescriptorBase:
        field: models.Field

        def is_cached(self, instance: models.Model) -> bool:
            ...

        def __get__(
            self,
            instance: Optional[models.Model],
            instance_type: Optional[Type[models.Model]] = None,
        ) -> Any:
            ...


else:
    DescriptorBase = object


class DescriptorMixin(DescriptorBase):
    def _field_name(self) -> str:
        return self.field.name

    def _is_cached(self, instance: models.Model) -> bool:
        return self.is_cached(instance)

    def _should_prefetch(self, instance: Optional[models.Model]) -> bool:
        return (
            instance is not None  # getattr on the class passes None to the descriptor
            and not self._is_cached(instance)  # already loaded
            and len(getattr(instance, "_peers", [])) >= 2  # no peers no prefetch
        )

    def __get__(
        self,
        instance: Optional[models.Model],
        instance_type: Optional[Type[models.Model]] = None,
    ) -> Any:
        if instance is not None and self._should_prefetch(instance):
            prefetch = models.query.Prefetch(self._field_name())
            peers = [p for p in instance._peers.values() if not self._is_cached(p)]
            models.query.prefetch_related_objects(peers, prefetch)
        return super().__get__(instance, instance_type)


class ForwardDescriptorMixin(DescriptorMixin):
    def _should_prefetch(self, instance: Optional[models.Model]) -> bool:
        return super()._should_prefetch(
            instance
        ) and None not in self.field.get_local_related_value(
            instance
        )  # field is null


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
    def _is_cached(self, instance: models.Model) -> bool:
        return self.related.is_cached(instance)

    def _field_name(self) -> str:
        return self.related.get_accessor_name()


class ForeignKey(models.ForeignKey):
    forward_related_accessor_class = ForwardManyToOneDescriptor


class OneToOneField(models.OneToOneField):
    forward_related_accessor_class = ForwardOneToOneDescriptor
    related_accessor_class = ReverseOneToOneDescriptor


class QuerySet(models.QuerySet):
    def _fetch_all(self) -> None:
        set_peers = self._result_cache is None
        super()._fetch_all()
        # ModelIterable tests for query sets returning model instances vs
        # values or value lists etc
        if set_peers and issubclass(self._iterable_class, models.query.ModelIterable):
            peers = WeakValueDictionary((id(o), o) for o in self._result_cache)
            for peer in peers.values():
                peer._peers = peers


Manager = models.Manager.from_queryset(QuerySet)


class Model(models.Model):
    class Meta:
        abstract = True
        base_manager_name = "prefetch_manager"

    objects = Manager()
    prefetch_manager = Manager()

    def __getstate__(self) -> Dict[str, Any]:
        # drop the peers info when pickling etc
        res = super().__getstate__()
        if "_peers" not in res:  # pragma: no cover
            return res

        res = dict(res)
        del res["_peers"]
        return res

    @classmethod
    def check(cls, **kwargs: Any) -> List[checks.Error]:
        errors: List[checks.Error] = super().check(**kwargs)
        errors.extend(cls._check_meta_inheritance())
        return errors

    @classmethod
    def _check_meta_inheritance(cls) -> List[checks.Error]:
        errors = []
        if not issubclass(cls.Meta, Model.Meta):
            errors.append(
                checks.Error(
                    id="auto_prefetch.E001",
                    obj=cls,
                    msg=(
                        f"{cls.__name__} inherits from auto_prefetch.Model,"
                        + " but its Meta class does not inherit from"
                        + " auto_prefetch.Model.Meta"
                    ),
                )
            )
        return errors
