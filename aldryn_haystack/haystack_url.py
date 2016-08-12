# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from furl import furl
from requests_aws4auth import AWS4Auth
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
            'aldryn_haystack.serializers.AldrynJSONSerializer'
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


def parse_multi(
        url,
        language_codes,
        default_language_code,
):
    """
    Takes an url containing a "*" character and replaces the "*" with the
    language code.
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
        if language_code == default_language_code:
            connections['default'] = parse(url, suffix='default')
        else:
            connections[language_code] = parse(url, suffix=language_code)
    return connections
