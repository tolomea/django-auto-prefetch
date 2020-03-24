# django-auto-prefetch
Automatically prefetch foreign key values as needed.

## Purpose

When accessing a foreign key on a model instance, if the field's value has not yet been loaded then auto-prefetch will prefetch the field for all model instances loaded by the same queryset as the current model instance.
This is enabled at the model level and totally automatic and transparent for users of the model.

## Usage

Everywhere you use Model, QuerySet, Manager or ForeignKey from django.db.models instead use them from auto_prefetch. No other changes are required.

## Background & Rationale

Currently when accessing an uncached foreign key field, Django will automatically fetch the missing value from the Database. When this occurs in a loop it creates 1+N query problems. Consider the following snippet:
```python
for choice in Choice.objects.all():
    print(choice.question.question_text, ':', choice.choice_text)
```
This will do one query for the choices and then one query per choice to get that choice's question.
This behavior can be avoided with correct application of prefetch_related like this:
```python
for choice in Choice.objects.prefetch_related('question'):
    print(choice.question.question_text, ':', choice.choice_text)
```
This has several usability issues, notably:
- Less experienced users are generally not aware that it's necessary.
- Cosmetic seeming changes to things like templates can change the fields that should be prefetched.
- Related to that the code that requires the prefetch_related (template for example) may be quite removed from where the prefetch_related needs to be applied (view for example).
- Subsequently finding where prefetch_related calls are missing is non trivial and needs to be done on an ongoing basis.
- Excess fields in prefetch_related calls are even harder to find and result in unnecessary database queries.
- It is very difficult for libraries like the admin and Django Rest Framework to automatically generate correct prefetch_related clauses.

On the first iteration of the loop in the example above, when we first access a choice's question field, instead of fetching the question for just that choice, auto-prefetch will speculatively fetch the questions for all the choices returned by the queryset.
This change results in the first snippet having the same database behavior as the second while reducing or eliminating all of the noted usability issues.

Some important points:
- Many2Many and One2One fields are not changed at all.
- Because these are foreign key fields the generated queries can't have more result rows than the original query and may have less. This eliminates any concern about a multiplicative query size explosion.
- This feature will never result in more database queries as a prefetch will only be issued where the ORM was already going to fetch a related object.
- Because it is triggered by fetching missing related objects it will not at all change the DB behavior of code which is fully covered by prefetch_related and/or select_related calls.
- This will inherently chain across relations like choice.question.author, the conditions above still hold under such chaining.
- In some rare situations it may result in larger data transfer between the database and Django (see below).
An example of that last point is:
```python
qs = Choice.objects.all()
list(qs)[0].question
```
Such examples generally seem to be rarer and more likely to be visible during code inspection (vs {{choice.question}} in a template). And larger queries are usually a better failure mode than producing hundreds of queries.
For this to actually produce inferior behavior in practice you need to:
- fetch a large number of choices
- filter out basically all of them
- in a way that prevents garbage collection of the unfiltered ones

If any of those aren't true then automatic prefetching will still produce equivalent or better database behavior than without.

p.s. if you have concerns go look at the code, it's all in `auto-prefetch/__init__.py` and is fairly short.
