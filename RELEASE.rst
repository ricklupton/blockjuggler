Release process
===============

* Tests: ``tox``

* Update CHANGELOG.rst, removing "(in development)" and adding date

* Update the version number in ``blockjuggler/__init__.py``

* Commit

* Release to PyPI::

    ./release.sh

* Tag the release e.g.::

    git tag v0.5

* Update the version numbers again, moving to the next release, and adding "-dev"

* Add new section to CHANGELOG.rst

* ``git push --tags``
