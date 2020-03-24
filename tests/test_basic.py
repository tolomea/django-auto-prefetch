import pytest

from . import models


@pytest.mark.parametrize("Model,queries", [(models.Vanilla, 4), (models.Prefetch, 2)])
@pytest.mark.django_db
def test_basic(django_assert_num_queries, Model, queries):
    friend = models.Friend.objects.create()
    [Model.objects.create(friend=friend) for i in range(3)]

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
    Model.objects.create()

    with django_assert_num_queries(queries):
        for obj in Model.objects.all():
            print(obj.pk, obj.friend)


@pytest.mark.parametrize("Model,queries", [(models.Vanilla, 1), (models.Prefetch, 1)])
@pytest.mark.django_db
def test_values(django_assert_num_queries, Model, queries):
    friend = models.Friend.objects.create()
    [Model.objects.create(friend=friend) for i in range(3)]

    with django_assert_num_queries(queries):
        for obj_pk, friend_pk in Model.objects.values_list("pk", "friend__pk"):
            print(obj_pk, friend_pk)


# duplicate objects
# garbage collected stuff
# cascades
# mixing parts of the system?
# mixed nulls?
