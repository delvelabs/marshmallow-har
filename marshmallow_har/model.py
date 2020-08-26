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

from datetime import datetime

from marshmallow import Schema as BaseSchema
from marshmallow import post_dump, post_load

from marshmallow_autoschema import schema_metafactory, sc_to_cc, One, Many, Raw


class Schema(BaseSchema):

    @post_load(pass_original=True, pass_many=True)
    def load_extended(self, data, original_data, many, partial):
        if many:
            return [self.load_extended(single, original, False, partial) for single, original in zip(data, original_data)]
        else:
            if isinstance(original_data, dict):
                extended_arguments = {k: v for k, v in original_data.items() if k.startswith('_')}

                if isinstance(data, dict):
                    data["extended_arguments"] = extended_arguments

            return self.__model__(**data)

        return self.__model__(**data)

    @post_dump
    def dump_extended(self, data, many):
        extended = data.pop("extendedArguments", {})
        data.update(extended)
        return data


HAR_SCHEMA_FACTORY = schema_metafactory(
    field_namer=sc_to_cc,
    schema_base_class=Schema,
)


@HAR_SCHEMA_FACTORY
class Model():

    def __init__(
        self, *,
        extended_arguments: Raw=None,
        comment: str="") -> None: pass

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError()

        return getattr(self.log, name)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.__dict__))


@HAR_SCHEMA_FACTORY
class Cookie(Model):

    def __init__(
        self, *,
        name: str,
        value: str,
        path: str=None,
        domain: str=None,
        expires: datetime=None,
        http_only: bool=False,
        secure: bool=False) -> None: pass


@HAR_SCHEMA_FACTORY
class CacheState(Model):

    def __init__(
        self, *,
        expires: datetime=None,
        last_access: datetime=None,
        e_tag: str=None,
        hit_count: int=0,
        **kwargs) -> None: pass


@HAR_SCHEMA_FACTORY
class Cache(Model):

    def __init__(
        self, *,
        before_request: One[CacheState]=None,
        after_request: One[CacheState]=None) -> None: pass


@HAR_SCHEMA_FACTORY
class Content(Model):

    def __init__(
        self, *,
        size: int=-1,
        mime_type: str=None,
        text: str="",
        encoding: str=None) -> None: pass


@HAR_SCHEMA_FACTORY
class Timings(Model):

    def __init__(
        self, *,
        blocked: int=-1,
        dns: int=-1,
        connect: int=-1,
        send: int=-1,
        wait: int=-1,
        receive: int=-1,
        ssl: int=-1) -> None: pass


@HAR_SCHEMA_FACTORY
class Header(Model):

    def __init__(self, *, name: str, value: str) -> None: pass


@HAR_SCHEMA_FACTORY
class PostParam(Model):

    def __init__(
        self, *,
        name: str,
        value: str,
        file_name: str=None,
        content_type: str=None) -> None: pass


@HAR_SCHEMA_FACTORY
class PostData(Model):

    def __init__(
        self, *,
        mime_type: str=None,
        params: Many[PostParam]=None,
        text: str="") -> None: pass


@HAR_SCHEMA_FACTORY
class Param(Model):

    def __init__(self, *, name: str, value: str) -> None: pass


@HAR_SCHEMA_FACTORY
class Request(Model):

    def __init__(  # type: ignore
            self, *,
            method: str,
            url: str,
            http_version: str="HTTP/1.0",
            cookies: Many[Cookie]=None,
            headers: Many[Header]=None,
            query_string: Many[Param]=None,
            post_data: One[PostData]=None,
            header_size: int=-1,
            body_size: int=-1,
            **kwargs) -> None:
        self.post_data = post_data or PostData()


@HAR_SCHEMA_FACTORY
class Response(Model):
    irregular_names = {'redirect_url': 'redirectURL'}

    def __init__(
        self, *,
        status: int,
        status_text: str,
        http_version: str="HTTP/1.0",
        cookies: Many[Cookie]=None,
        headers: Many[Header]=None,
        content: One[Content]=None,
        redirect_url: str="",
        header_size: int=-1,
        body_size: int=-1) -> None: pass


@HAR_SCHEMA_FACTORY
class Creator(Model):

    def __init__(self, *, name: str, version: str) -> None: pass


@HAR_SCHEMA_FACTORY
class PageTimings(Model):

    def __init__(
        self, *,
        on_content_load: int=-1, on_load: int=-1) -> None: pass


@HAR_SCHEMA_FACTORY
class Page(Model):

    def __init__(
        self, *,
        id: str,
        title: str,
        started_date_time: datetime=None,
        page_timings: One[PageTimings]=None) -> None: pass


@HAR_SCHEMA_FACTORY
class Browser(Model):

    def __init__(self, *, name: str, version: str) -> None: pass


@HAR_SCHEMA_FACTORY
class Entry(Model):
    irregular_names = {
        'server_ip_address': 'serverIPAddress',
    }

    def __init__(
        self, *,
        pageref: str=None,
        started_date_time: datetime=None,
        time: int=-1,
        request: One[Request]=None,
        response: One[Response]=None,
        cache: One[Cache]=None,
        timings: One[Timings]=None,
        server_ip_address: str=None,
        connection: str=None) -> None: pass


@HAR_SCHEMA_FACTORY
class Log(Model):

    def __init__(
        self, *,
        version: str="1.1",
        creator: One[Creator]=None,
        browser: One[Browser]=None,
        pages: Many[Page]=None,
        entries: Many[Entry]=None) -> None: pass


@HAR_SCHEMA_FACTORY
class HAR(Model):

    def __init__(self, *, log: One[Log]=None, **kwargs) -> None:
        self.log = log or Log(**kwargs)
