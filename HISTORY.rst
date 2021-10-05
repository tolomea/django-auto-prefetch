=======
History
=======

1.0.0 (2021-10-05)
------------------

* Support Python 3.10.

0.1.1 (2021-09-28)
------------------

* Fix versions advertised in README.

0.1.0 (2021-09-28)
------------------

* Support Django 4.0.

* Support Django 3.2.

* Add system check that the ``Meta`` class is inherited in all subclasses.

0.0.6 (2020-07-29)
------------------

* Fix model subclasses’ default manager back to ``objects`` rather than
  ``prefetch_manager``.

0.0.5 (2020-04-05)
------------------

* Remove tests from built package.

0.0.4 (2020-03-26)
------------------

* Fix pickled model instances. Instances loaded from pickle remove their peer
  tracking so will be subject to 1+N queries for any foreign key access.

0.0.3 (2020-03-26)
------------------

* Declare Python 3.5 support.

0.0.2 (2020-03-25)
------------------

* Fix packaging issues.

0.0.1 (2020-03-24)
------------------

* Initial release.
