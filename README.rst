###############
Aldryn Haystack
###############

A simple django haystack setup bundled as an Aldryn Addon.
To be used together with aldryn-django. This Addon configures a default
index for haystack using ElasticSearch.


============
Installation
============

**Aldryn Platform Users** ask support to provision ElasticSeearch for you.

Local docker setup
==================

For local development add a ElasticSearch service to ``docker-compose.yml``::

    es:
        image: elasticsearch:2.3

and add a link to it from the web service::

    web:
        links:
          - "es:es"

Then add the environment variable to configure the connection (on the default
aldryn setup: add to ``.env-local``)::

    DEFAULT_HAYSTACK_URL=es+http://es:9200/local-*

Test the connection::

    docker-compose run --rm web python manage.py shell
    >>> from haystack.query import SearchQuerySet
    >>> list(SearchQuerySet())
    []

There won't be any results yet, since nothing was indexed. But you will get an
error if the connection does not work.

Indexing on aldryn
==================

To index pages setup a cronjob::

    python manage.py rebuild_index --noinput


========================
Usage with aldryn-search
========================

The full instructions are available
_here:https://github.com/aldryn/aldryn-search , but are not necessary as all
steps are discribed below.

* Add ``aldryn-search`` to ``requirements.in``
* Add ``aldryn_search``, ``standard_form`` and ``spurl`` to ``INSTALLED_APPS``
  in ``settings.py``
* in ``settings.py`` add the following code to configure an index per language:

::
    from aldryn_haystack import haystack_url
    HAYSTACK_CONNECTIONS = haystack_url.parse_i18n(
        url=DEFAULT_HAYSTACK_URL,
        language_codes=[lang[0] for lang in LANGUAGES],
        default_language_code=LANGUAGE_CODE,
    )
    HAYSTACK_ROUTERS = ['aldryn_search.router.LanguageRouter']

Start the webserver and create a new CMS Page called ``search``. Then attach
the "aldryn search" App Hook and publish the page.

At the time of writing search is broken in aldryn-jobs and aldryn-people.
Deactivate the respective indexes with the following settings:

::
    # incompatible with Haystack
    # https://github.com/aldryn/aldryn-people/issues/141
    # https://github.com/aldryn/aldryn-jobs/issues/175
    ALDRYN_JOBS_SEARCH = False
    ALDRYN_PEOPLE_SEARCH = False


===========
Other Stuff
===========

``DEFAULT_HAYSTACK_URL`` environment variable
=============================================

Set an environment variable (currently only ElasticSearch is supported)::

    DEFAULT_HAYSTACK_URL=es+http://hostname:9200/my-index-name

There is also native support for AWS ElasticSearch style connections::

    DEFAULT_HAYSTACK_URL=es+https+aws://AWS_ACCESS_KEY:AWS_SECRET_KEY@cluster-name.us-east-1.amazonaws.com/my-index-name

There is also support to define the index name with a wildcard ``*`` that can
be used for things like easy multilingual index setup.


Debugging
=========

Set the ``ALDRYN_HAYSTACK_DEBUG`` environment variable to True to get detailed
logs from haystack.
