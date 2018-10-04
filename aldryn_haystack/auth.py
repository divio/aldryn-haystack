# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from requests_aws4auth import AWS4Auth


class AWS4AuthNotUnicode(AWS4Auth):
    """
    This is a workaround for
    https://github.com/sam-washington/requests-aws4auth/issues/24

    These are similar issues:
    https://github.com/shazow/urllib3/issues/855
    https://github.com/kennethreitz/requests/issues/3177
    """
    def __call__(self, req):
        req = super(AWS4AuthNotUnicode, self).__call__(req)
        req.headers = {
            name if isinstance(name, bytes) else name.encode('ascii'):
            value if isinstance(value, bytes) else value.encode('ascii')
            for name, value in req.headers.items()
        }

        # Some layer down the stack (probably requests or urllib3 when running
        # under python3) does something differently based on the presence of
        # the content-length header, but only checks against one of the text or
        # bytes types, failing to follow the right path when the header is
        # already encoded (everything works when the header is left as `str`).
        #
        # Some versions of AWS ElasticSearch service started to raise a 400
        # HTTP error in such cases (first observed after the modification of a
        # working 2.3 cluster, which might indicate that the change has been
        # introduced in a patch release).
        #
        # The workaround is to remove the header when the content-length is 0.
        if req.headers.get(b'Content-Length') == b'0':
            req.headers.pop(b'Content-Length')
        return req
