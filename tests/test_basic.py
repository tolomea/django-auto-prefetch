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


# duplicate objects
# garbage collected stuff
# cascades
# mixing parts of the system?
