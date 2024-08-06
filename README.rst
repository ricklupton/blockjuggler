blockjuggler
============

This script converts an ical calendar (for instance, as exported from Google
Calendar or Outlook) into TaskJuggler ``leaves`` statements, which make a
particular resource available only during the events in the calendar.

This allows you to mark out arbitrary periods in a calendar when you (or others)
are available to work on projects, then use TaskJuggler to schedule projects to
fit within those times.

Installation
============

The command ``blockjuggler`` is provided by means of python package ``blockjuggler``.

You can install with ``pip`` (preferably into its own into virtualenv)::

    $ pip install blockjuggler

Installation with `pipx <https://github.com/pypa/pipx>`_ is recommended because
this will manage the virtualenv for you.

Usage
=====
Simply use the ``blockjuggler`` command::

    $ blockjuggler --help

The script requires two files, the input ics and the output TaskJuggler file.
Usually, ``blockjuggler`` is called within a script that grabs the ical file from
some source (e.g. Google Calendar), and generates the appropriate TaskJuggler file.
Such an script would have the following shape::

    #!/bin/bash

    ICSFILE=$(mktemp)
    AVAILABILITYFILE=<path to availability.tji>
    URL=<url to your private calendar>

    # no customization needed below

    wget -O $ICSFILE $URL
    blockjuggler $ICSFILE $AVAILABILITYFILE
    rm -f $ICSFILE

Then, you can ``include`` the file ``availability.tji`` (or whatever you want to
call it) in your TaskJuggler project.

Development
===========

Clone the repository and cd into it.

Create a virtualenv and install dependencies::

    $ pip install .
    $ pip install -r test_requirements.txt

Run tests to check everything is working::

    $ pytest

You can also use tox to create the virtualenv e.g.::

    $ tox -e py39

Then activate the virtualenv::

    $ source .tox/py39/bin/activate
    (py39)$

And use the package.

Acknowledgements
================

The starting point for this script was https://github.com/ical2org-py/ical2org.py -- thanks!
