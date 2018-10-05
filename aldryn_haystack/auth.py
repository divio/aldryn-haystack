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
        return req
