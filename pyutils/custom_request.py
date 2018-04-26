#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""docstring"""

import requests

__author__ = "chiachi"


class RetriesException(Exception):
    def __init__(self, err):
        self.err = err

    def __str__(self):
        return repr(self.err)


class CustomRequest(object):
    def __init__(self, session=requests, retries=3):
        self.session = session
        self.retries = retries
        self.timeout = 20

    def get(self, url, params=None, retries=None, **kwargs):
        if retries is None:
            retries = self.retries
        try:
            r = self.session.get(url, params=params, timeout=self.timeout, **kwargs)
            if r.ok:
                return r
            else:
                raise RetriesException
        except (RetriesException, Exception):
            return self.get(url, params=params, retries=retries-1, **kwargs) if retries > 1 else None

    def post(self, url, data=None, json=None, retries=None, **kwargs):
        if retries is None:
            retries = self.retries
        try:
            r = self.session.post(url, data, json, timeout=self.timeout, **kwargs)
            if r.ok:
                return r
            else:
                raise RetriesException
        except (RetriesException, Exception):
            return self.post(url, data=data, json=json, retries=retries, **kwargs) if retries > 1 else None


if __name__ == "__main__":
    resp = CustomRequest().get("http://apps.bdimg.com/libs/accounting.js/0.3.2/accounting.min.js")
    print resp.content
