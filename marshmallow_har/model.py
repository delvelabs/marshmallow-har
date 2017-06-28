

class HAR:

    def __init__(self, *, log=None, **kwargs):
        self.log = log or Log(**kwargs)

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError()

        return getattr(self.log, name)


class Model:

    def __init__(self, extended_arguments=None, comment=""):
        self.extended_arguments = extended_arguments or {}
        self.comment = comment

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.__dict__))


class Request(Model):

    def __init__(self, *,
                 method,
                 url,
                 http_version="HTTP/1.0",
                 cookies=None,
                 headers=None,
                 query_string=None,
                 post_data=None,
                 header_size=-1,
                 body_size=-1,
                 **kwargs):

        super().__init__(**kwargs)
        self.method = method
        self.url = url
        self.http_version = http_version
        self.cookies = cookies or []
        self.headers = headers or []
        self.query_string = query_string or []
        self.post_data = post_data or PostData()
        self.header_size = header_size
        self.body_size = body_size


class Response(Model):

    def __init__(self, *,
                 status,
                 status_text,
                 http_version="HTTP/1.0",
                 cookies=None,
                 headers=None,
                 content=None,
                 redirect_url=None,
                 header_size=-1,
                 body_size=-1,
                 **kwargs):

        super().__init__(**kwargs)
        self.status = status
        self.status_text = status_text
        self.http_version = http_version
        self.cookies = cookies or []
        self.headers = headers or []
        self.content = content
        self.redirect_url = redirect_url
        self.header_size = header_size
        self.body_size = body_size


class Cache(Model):

    def __init__(self, *,
                 before_request=None,
                 after_request=None,
                 **kwargs):

        super().__init__(**kwargs)
        self.before_request = before_request
        self.after_request = after_request


class CacheState(Model):

    def __init__(self, *,
                 expires=None,
                 last_access=None,
                 e_tag=None,
                 hit_count=0,
                 **kwargs):

        self.expires = expires
        self.last_access = last_access
        self.e_tag = e_tag
        self.hit_count = hit_count


class Content(Model):

    def __init__(self, *,
                 size=-1,
                 mime_type=None,
                 text="",
                 encoding=None,
                 **kwargs):

        super().__init__(**kwargs)
        self.size = size
        self.mime_type = mime_type
        self.text = text
        self.encoding = encoding


class Timings(Model):

    def __init__(self, *,
                 blocked=-1,
                 dns=-1,
                 connect=-1,
                 send=-1,
                 wait=-1,
                 receive=-1,
                 ssl=-1,
                 **kwargs):

        super().__init__(**kwargs)
        self.blocked = blocked
        self.dns = dns
        self.connect = connect
        self.send = send
        self.wait = wait
        self.receive = receive
        self.ssl = ssl


class Entry(Model):

    def __init__(self, *,
                 pageref=None,
                 started_date_time=None,
                 time=-1,
                 request=None,
                 response=None,
                 cache=None,
                 timings=None,
                 server_ip_address=None,
                 connection=None,
                 **kwargs):

        super().__init__(**kwargs)
        self.pageref = pageref
        self.started_date_time = started_date_time
        self.time = time
        self.request = request
        self.response = response
        self.cache = cache
        self.timings = timings
        self.server_ip_address = server_ip_address
        self.connection = connection


class Header(Model):

    def __init__(self, *, name, value, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.value = value


class Cookie(Model):
    def __init__(self, *,
                 name,
                 value,
                 path=None,
                 domain=None,
                 expires=None,
                 http_only=False,
                 secure=False,
                 **kwargs):

        super().__init__(**kwargs)
        self.name = name
        self.value = value
        self.path = path
        self.domain = domain
        self.expires = expires
        self.http_only = http_only
        self.secure = secure


class PostData(Model):

    def __init__(self, *,
                 mime_type=None,
                 params=None,
                 text="",
                 **kwargs):
        super().__init__(**kwargs)
        self.mime_type = mime_type
        self.params = params or []
        self.text = text


class Param(Model):

    def __init__(self, *,
                 name,
                 value,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.value = value


class PostParam(Model):

    def __init__(self, *,
                 name,
                 value,
                 file_name=None,
                 content_type=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.value = value
        self.file_name = file_name
        self.content_type = content_type


class Creator(Model):

    def __init__(self, *,
                 name,
                 version,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.version = version


class Page(Model):

    def __init__(self, *,
                 id,
                 title,
                 started_date_time=None,
                 page_timings=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.title = title
        self.started_date_time = started_date_time
        self.page_timings = page_timings


class PageTimings(Model):

    def __init__(self, *,
                 on_content_load=-1,
                 on_load=-1,
                 **kwargs):
        super().__init__(**kwargs)
        self.on_content_load = on_content_load
        self.on_load = on_load


class Browser(Model):

    def __init__(self, *,
                 name,
                 version,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.version = version


class Log(Model):

    def __init__(self, *,
                 version="1.1",
                 creator=None,
                 browser=None,
                 pages=None,
                 entries=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.version = version
        self.creator = creator
        self.browser = browser
        self.pages = pages or []
        self.entries = entries or []
