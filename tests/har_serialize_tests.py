# MIT License
#
# Copyright (c) 2017- Delve Labs Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import unittest.mock
from marshmallow_har.schema import HARSchema, RequestSchema
from marshmallow_har.model import (
    Browser, Cache, Cookie, Creator, Header, Page, Param, Request, Response,
    PostData, Entry, HAR, Timings, PostParam,
)


class RequestSerializeTest(unittest.TestCase):

    def test_minimal_request(self):
        request = Request(method="GET",
                          url="http://example.com/",
                          http_version="HTTP/1.0")
        self.assertEqual(request.dump(), {
            "method": "GET",
            "url": "http://example.com/",
            "httpVersion": "HTTP/1.0",
            "headerSize": -1,
            "bodySize": -1,
            "cookies": [],
            "headers": [],
            "queryString": [],
            "postData": {"comment": "", "mimeType": None, "text": "", "params": []},
            "comment": "",
        })

    def test_request_with_cookie(self):
        request = Request(method="GET",
                          url="http://example.com/",
                          http_version="HTTP/1.0",
                          cookies=[Cookie(name="PHPSESSID", value="12341234")])
        self.assertEqual(request.dump()["cookies"][0], {
            "name": "PHPSESSID",
            "value": "12341234",
            "path": None,
            "domain": None,
            "expires": None,
            "httpOnly": False,
            "secure": False,
            "comment": "",
        })

    def test_request_with_headers(self):
        request = Request(method="GET",
                          url="http://example.com/",
                          http_version="HTTP/1.0",
                          headers=[Header(name="Accept-Language", value="en-US; *")])
        self.assertEqual(request.dump()["headers"][0], {
            "name": "Accept-Language",
            "value": "en-US; *",
            "comment": "",
        })

    def test_request_without_post_data_initializes_object(self):
        request = Request(
            method="POST",
            url="http://example.com/form",
            http_version="HTTP/1.0"
        )
        self.assertEqual(request.post_data.text, "")

    def test_request_with_post_data(self):
        request = Request(
            method="POST",
            url="http://example.com/form",
            http_version="HTTP/1.0",
            post_data=PostData(
                mime_type="multipart/form-data",
                params=[
                    PostParam(name="user", value="anonymous1"),
                ]
            )
        )

        self.assertEqual(request.dump()["postData"], {
            "mimeType": "multipart/form-data",
            "params": [{
                "name": "user",
                "value": "anonymous1",
                "fileName": None,
                "contentType": None, "comment": ""},
            ],
            "text": "",
            "comment": "",
        })

    def test_preserve_extended_attributes(self):
        input = {
            "method": "GET",
            "url": "http://example.com/",
            "httpVersion": "HTTP/1.0",
            "headerSize": -1,
            "bodySize": -1,
            "cookies": [],
            "headers": [],
            "queryString": [],
            "postData": {},
            "comment": "",
            "_extended": "Hello",
            "_anything": {"test": "Hello World!"},
        }
        intermediate = Request.load(input)
        out = intermediate.dump()

        self.assertEqual({"test": "Hello World!"}, out["_anything"])

    def test_preserve_extended_attributes_when_nexted(self):
        input = {
            "method": "GET",
            "url": "http://example.com/",
            "httpVersion": "HTTP/1.0",
            "headerSize": -1,
            "bodySize": -1,
            "cookies": [
                {"name": "a", "value": "1", "_test": "123"},
                {"name": "b", "value": "2", "_test": "234"},
            ],
            "headers": [],
            "queryString": [],
            "postData": {},
            "comment": "",
        }
        intermediate = RequestSchema().load(input)
        out = RequestSchema().dump(intermediate)

        self.assertEqual("123", out["cookies"][0]["_test"])
        self.assertEqual("234", out["cookies"][1]["_test"])


class CookieSerializeTest(unittest.TestCase):

    def test_complete_cookie(self):
        from datetime import datetime
        current = datetime.now()

        cookie = Cookie(name="TEST",
                        value="123",
                        path="/test",
                        domain="example.com",
                        expires=current,
                        http_only=True,
                        secure=True,
                        comment="")
        out = cookie.dump()
        self.assertEqual(out, {
            "name": "TEST",
            "value": "123",
            "path": "/test",
            "domain": "example.com",
            "expires": unittest.mock.ANY,
            "httpOnly": True,
            "secure": True,
            "comment": "",
        })
        self.assertEqual(current.strftime("%Y-%m-%d"), out["expires"][0:10])


class HeaderSerializeTest(unittest.TestCase):

    def test_complete_header(self):
        input = {"name": "X", "value": "Y", "comment": ""}
        obj = Header(name="X", value="Y")

        self.assertEqual(Header.load(input), obj)
        self.assertEqual(obj.dump(), input)


class QueryStringSerializeTest(unittest.TestCase):

    def test_complete_header(self):
        input = {"name": "q", "value": "test", "comment": ""}
        obj = Param(name="q", value="test")

        self.assertEqual(Param.load(input), obj)
        self.assertEqual(obj.dump(), input)

    def test_query_string_in_request(self):
        input = {
            "method": "GET",
            "url": "http://example.com/",
            "httpVersion": "HTTP/1.0",
            "headerSize": -1,
            "bodySize": -1,
            "queryString": [
                {"name": "a", "value": "1"},
            ],
            "headers": [],
            "postData": {},
            "comment": "",
        }
        obj = Request.load(input)
        self.assertEqual(obj.query_string[0], Param(name="a", value="1"))


class HARSerializeTest(unittest.TestCase):

    def test_basic_har(self):
        har = HAR(version="1.2")

        self.assertEqual(har.dump(), {
            'comment': '',
            "log": {
                "version": "1.2",
                "creator": None,
                "browser": None,
                "pages": [],
                "entries": [],
                "comment": "",
            },
        })

    def test_with_page(self):
        har = HAR(version="1.2", pages=[
            Page(id="page_0", title="Hello World"),
        ])
        self.assertEqual(har.dump()["log"]["pages"][0], {
            "startedDateTime": None,
            "id": "page_0",
            "title": "Hello World",
            "pageTimings": None,
            "comment": "",
        })


class CreatorSerializeTest(unittest.TestCase):

    def test_creator(self):
        input = {"name": "Firebug", "version": "1.5", "comment": ""}
        obj = Creator(name="Firebug", version="1.5", comment="")

        self.assertEqual(Creator.load(input), obj)
        self.assertEqual(obj.dump(), input)


class BrowserSerializeTest(unittest.TestCase):

    def test_creator(self):
        input = {"name": "Firefox", "version": "3.5", "comment": ""}
        obj = Browser(name="Firefox", version="3.5", comment="")

        self.assertEqual(Browser.load(input), obj)
        self.assertEqual(obj.dump(), input)


class EntrySerializeTest(unittest.TestCase):

    def test_base_entry(self):
        self.maxDiff = 5000
        entry = Entry(request=Request(method="GET", url="http://example.com/"))
        out = entry.dump()

        self.assertEqual(out, {
            "pageref": None,
            "startedDateTime": None,
            "time": -1,
            "request": {
                "method": "GET",
                "url": "http://example.com/",
                "httpVersion": "HTTP/1.0",
                "headerSize": -1,
                "bodySize": -1,
                "cookies": [],
                "headers": [],
                "queryString": [],
                "postData": unittest.mock.ANY,
                "comment": "",
            },
            "response": None,
            "cache": None,
            "timings": None,
            "serverIPAddress": None,
            "connection": None,
            "comment": "",
        })

    def test_response(self):
        entry = Entry(response=Response(status=200,
                                        status_text="OK",
                                        http_version="HTTP/1.0"))
        out = entry.dump()

        self.assertEqual(out["response"], {
            "status": 200,
            "statusText": "OK",
            "httpVersion": "HTTP/1.0",
            "cookies": [],
            "headers": [],
            "content": unittest.mock.ANY,
            "redirectURL": "",
            "headerSize": -1,
            "bodySize": -1,
            "comment": "",
        })

    def test_cache(self):
        entry = Entry(cache=Cache())
        out = entry.dump()

        self.assertEqual(out["cache"], {
            "beforeRequest": None,
            "afterRequest": None,
            "comment": "",
        })

    def test_timings(self):
        entry = Entry(timings=Timings(blocked=12,
                                      dns=3,
                                      connect=15,
                                      send=20,
                                      wait=38,
                                      receive=12))
        out = entry.dump()

        self.assertEqual(out["timings"], {
            "blocked": 12,
            "dns": 3,
            "connect": 15,
            "send": 20,
            "wait": 38,
            "receive": 12,
            "ssl": -1,
            "comment": "",
        })


class ResponseSerializeTest(unittest.TestCase):

    def test_response(self):
        input = {
            "status": 301,
            "statusText": "Moved Permanently",
            "httpVersion": "HTTP/1.1",
            "cookies": [{
                "name": "auth",
                "value": "1",
                "path": None,
                "domain": None,
                "expires": None,
                "httpOnly": False,
                "secure": False,
                "comment": "",
            }],
            "headers": [
                {"name": "Location", "value": "http://example.com/test", "comment": ""},
                {"name": "Host", "value": "example.com", "comment": ""},
            ],
            "content": {
                "size": 45,
                "mimeType": "text/html",
                "text": "<html><body>Redirect</body></html>",
                "encoding": None,
                "comment": "",
            },
            "redirectURL": "http://example.com/test",
            "headerSize": -1,
            "bodySize": 45,
            "comment": "Expected.",
        }
        intermediate = Response.load(input)
        output = intermediate.dump()

        self.maxDiff = None
        self.assertEqual(input, output)

    def test_empty_redirect_url(self):
        input = {
            "status": 200,
            "statusText": "OK",
            "httpVersion": "HTTP/1.0",
            "cookies": [],
            "headers": [],
            "content": None,
            "redirectURL": "",
            "headerSize": -1,
            "bodySize": -1,
            "comment": "",
        }
        intermediate = Response.load(input)
        output = intermediate.dump()
        self.assertEqual(input, output)


class CacheSerializeTest(unittest.TestCase):

    def test_cache_entry(self):
        cache = {
            "beforeRequest": {
                "eTag": "1234",
                "hitCount": 12,
            },
        }
        cache = Cache.load(cache)
        self.assertEqual(cache.before_request.e_tag, "1234")
        self.assertEqual(cache.before_request.hit_count, 12)


class PageSerializeTest(unittest.TestCase):

    def test_page_with_timings(self):
        page = {
            "id": "page_1",
            "title": "Test",
            "pageTimings": {
                "onContentLoad": 123,
                "onLoad": 234,
            },
        }
        page = Page.load(page)
        self.assertEqual(page.id, "page_1")
        self.assertEqual(page.page_timings.on_content_load, 123)
        self.assertEqual(page.page_timings.on_load, 234)


class PickleTest(unittest.TestCase):

    def test_har_pickle(self):

        har = HAR(version="1.2", pages=[
            Page(id="page_0", title="Hello World"),
        ])

        import pickle

        dumped = pickle.dumps(har)
        loaded_har = pickle.loads(dumped)

        self.assertEqual(
            HARSchema().dump(har),
            HARSchema().dump(loaded_har),
        )
