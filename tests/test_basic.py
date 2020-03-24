import gc

import pytest

from . import models


@pytest.mark.parametrize("Model,queries", [(models.Vanilla, 4), (models.Prefetch, 2)])
@pytest.mark.django_db
def test_basic(django_assert_num_queries, Model, queries):
    friend = models.Friend.objects.create()
    [Model.objects.create(friend=friend) for _ in range(3)]

    with django_assert_num_queries(queries):
        for obj in Model.objects.all():
            print(obj.pk, obj.friend.pk)


@pytest.mark.parametrize("Model,queries", [(models.Vanilla, 2), (models.Prefetch, 2)])
@pytest.mark.django_db
def test_no_peers(django_assert_num_queries, Model, queries):
    friend = models.Friend.objects.create()
    Model.objects.create(friend=friend)

    with django_assert_num_queries(queries):
        for obj in Model.objects.all():
            print(obj.pk, obj.friend.pk)


@pytest.mark.parametrize("Model,queries", [(models.Vanilla, 1), (models.Prefetch, 1)])
@pytest.mark.django_db
def test_null(django_assert_num_queries, Model, queries):
    [Model.objects.create() for _ in range(3)]

    with django_assert_num_queries(queries):
        for obj in Model.objects.all():
            print(obj.pk, obj.friend)


@pytest.mark.parametrize("Model,queries", [(models.Vanilla, 1), (models.Prefetch, 1)])
@pytest.mark.django_db
def test_values(django_assert_num_queries, Model, queries):
    friend = models.Friend.objects.create()
    [Model.objects.create(friend=friend) for _ in range(3)]

    with django_assert_num_queries(queries):
        for obj_pk, friend_pk in Model.objects.values_list("pk", "friend__pk"):
            print(obj_pk, friend_pk)


@pytest.mark.parametrize("Model,queries", [(models.Vanilla, 7), (models.Prefetch, 2)])
@pytest.mark.django_db
def test_multiples(django_assert_num_queries, Model, queries):
    friend = models.Friend.objects.create()
    associates = [models.Associate.objects.create(number=6) for _ in range(2)]
    for _ in range(3):
        obj = Model.objects.create(friend=friend)
        obj.associates.set(associates)

    with django_assert_num_queries(queries):
        objs = list(Model.objects.filter(associates__number__gt=1))
        assert len(objs) == 6
        for obj in objs:
            print(obj.pk, obj.friend)


@pytest.mark.django_db
def test_garbage_collection():
    def check_instances(num):
        gc.collect()
        objs = [o for o in gc.get_objects() if isinstance(o, models.Prefetch)]
        assert len(objs) == num

    friend = models.Friend.objects.create()
    [models.Prefetch.objects.create(friend=friend) for _ in range(3)]
    del friend

    check_instances(0)

    objs = list(models.Prefetch.objects.all())

    check_instances(3)

    obj = objs[0]
    del objs

    check_instances(1)

    print(obj.pk, obj.friend)


@pytest.mark.parametrize(
    "Model,Model2,queries",
    [(models.Vanilla, models.Vanilla2, 7), (models.Prefetch, models.Prefetch2, 3)],
)
@pytest.mark.django_db
def test_cascading(django_assert_num_queries, Model, Model2, queries):
    friend = models.Friend.objects.create()
    for _ in range(3):
        obj = Model.objects.create(friend=friend)
        Model2.objects.create(other=obj)

    with django_assert_num_queries(queries):
        for obj in Model2.objects.all():
            print(obj.pk, obj.other.pk, obj.other.friend.pk)


# mixing parts of the system?
# mixed nulls?
# one 2 one
# reverse one2one
