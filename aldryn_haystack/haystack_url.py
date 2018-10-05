# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from furl import furl
from aldryn_addons.utils import boolean_ish
from django.utils.module_loading import import_string


def parse(url, suffix='default'):
    url = furl(url)
    connection = {
        'ENGINE': '',
        'URL': '',
        'INDEX_NAME': '',
        'KWARGS': {},
    }
    engine, protocol, platform = None, None, None
    scheme_parts = url.scheme.split('+')
    if len(scheme_parts) == 2:
        engine, protocol = scheme_parts
    elif len(scheme_parts) == 3:
        engine, protocol, platform = scheme_parts
    else:
        error_url = furl(url.url)
        error_url.password = '----'
        raise Exception(
            (
                'The scheme in the haystack url {} is not supported. It must '
                'have a scheme in the form of backend+protocol+platform:// or '
                'backend+protocol://.'
                'Examples: es+https+aws:// es+http://'
            ).format(error_url))
    url.scheme = protocol
    if engine == 'es':
        connection['ENGINE'] = 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'
    else:
        connection['ENGINE'] = engine

    if '*' in url.path.segments[0]:
        # If the index contains the wildcard, replace it with the suffix
        url.path.segments[0] = url.path.segments[0].replace('*', suffix)

    # extract the index name and remove the path from the original url
    index_name = '{}'.format(url.path.segments[0])
    url.path.segments = []
    connection['INDEX_NAME'] = index_name

    if platform == 'aws':
        aws_access_key_id = url.username
        aws_secret_key = url.password
        url.username = None
        url.password = None

        connection['URL'] = url.url
        region = url.host.split('.')[1]
        verify_certs = boolean_ish(url.query.params.get('verify_certs', True))
        ConnectionClass = import_string(url.query.params.get(
            'connection_class',
            'elasticsearch.RequestsHttpConnection'
        ))
        Serializer = import_string(url.query.params.get(
            'serializer',
            'elasticsearch.serializer.JSONSerializer'
        ))
        if sys.version_info.major >= 3:
            # The workaround for the large payload issue below is causing
            # the underling Python `http` module to send the Content-Length
            # header twice when running on Python 3, which fails with a
            # 400 Bad Request on recent AWS ElasticSearch service endpoints.
            # Just drop the workaround as we were not able to reproduce the
            # issue anymore with any combination of recent dependencies and
            # we suppose that the issue does not exist anymore on Python 3
            # because of its explicit handling of `bytes` and `str` as
            # different types.
            default_auth_class = 'requests_aws4auth.AWS4Auth'
        else:
            # The unicode handling of urllib3/pyopenssl combined with
            # AWS4Auth causes requests with large bodies (> 2MB) to fail.
            # For more details see the workaround referenced below.
            default_auth_class = 'aldryn_haystack.auth.AWS4AuthNotUnicode'
        AWS4Auth = import_string(url.query.params.get(
            'aws_auth',
            default_auth_class,
        ))
        connection['KWARGS'] = {
            'port': url.port,
            'http_auth': AWS4Auth(
                aws_access_key_id,
                aws_secret_key,
                region,
                'es',
            ),
            'use_ssl': protocol == 'https',
            'verify_certs': verify_certs,
            'connection_class': ConnectionClass,
            'serializer': Serializer(),
        }
    else:
        connection['URL'] = url.url
        connection['INDEX_NAME'] = index_name
    return connection


def parse_i18n(
        url,
        language_codes,
        default_language_code=None,
):
    """
    Takes an url containing a "*" character and creates an index per language
    replacing the "*" with the language code, except for the default language.
    :param url:
    :return:
    """
    if '*' not in furl(url).path.segments[0]:
        index_name = furl(url).path.segments[0]
        raise Exception(
            (
                'The index name in the haystack url {} is not supported. Must '
                'have a * in its name for multilingual index support'
            ).format(index_name)
        )
    connections = {}
    for language_code in language_codes:
        if default_language_code and language_code == default_language_code:
            connections['default'] = parse(url, suffix='default')
        else:
            connections[language_code] = parse(url, suffix=language_code)
    return connections
