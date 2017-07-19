from marshmallow import Schema as BaseSchema, fields, post_dump, post_load
from .model import Cookie, Request, Response, Entry, HAR, Header, Param, PostData, PostParam
from .model import Log, Page, Creator, Browser, Cache, CacheState, Timings, Content, PageTimings


class Schema(BaseSchema):

    extended_arguments = fields.Raw(required=False)
    comment = fields.String(required=False)

    @post_load(pass_original=True, pass_many=True)
    def load_extended(self, data, many, original_data):
        if many:
            return [self.load_extended(single, False, original) for single, original in zip(data, original_data)]
        else:
            if isinstance(original_data, dict):
                extended_arguments = {k: v for k, v in original_data.items() if k.startswith('_')}

                if isinstance(data, dict):
                    data["extended_arguments"] = extended_arguments

            return self.__model__(**data)

    @post_dump
    def dump_extended(self, data):
        extended = data.pop("extended_arguments", {})
        data.update(extended)


class CookieSchema(Schema):

    __model__ = Cookie

    DATE_FORMAT = "iso"

    name = fields.String()
    value = fields.String()
    path = fields.String(required=False, allow_none=True)
    domain = fields.String(required=False, allow_none=True)
    expires = fields.DateTime("iso", required=False, allow_none=True)
    http_only = fields.Boolean(required=False, load_from="httpOnly", dump_to="httpOnly", default=False)
    secure = fields.Boolean(required=False, default=False)


class HeaderSchema(Schema):

    __model__ = Header

    name = fields.String(required=True)
    value = fields.String(required=True)


class ParamSchema(Schema):

    __model__ = Param

    name = fields.String(required=True)
    value = fields.String(required=True)


class PostParamSchema(Schema):

    __model__ = PostParam

    name = fields.String(required=True)
    value = fields.String(required=True)
    file_name = fields.String(required=False, load_from="fileName", dump_to="fileName", allow_none=True)
    content_type = fields.String(required=False, load_from="contentType", dump_to="contentType", allow_none=True)


class PostDataSchema(Schema):

    __model__ = PostData

    mime_type = fields.String(required=False, load_from="mimeType", dump_to="mimeType", allow_none=True)
    params = fields.Nested(PostParamSchema, many=True)
    text = fields.String(required=False)


class RequestSchema(Schema):

    __model__ = Request

    method = fields.String(required=True)
    url = fields.Url(required=True)
    http_version = fields.String(required=False, load_from="httpVersion", dump_to="httpVersion")
    cookies = fields.Nested(CookieSchema, many=True)
    headers = fields.Nested(HeaderSchema, many=True)
    query_string = fields.Nested(ParamSchema, many=True, load_from="queryString", dump_to="queryString")
    post_data = fields.Nested(PostDataSchema, required=False, load_from="postData", dump_to="postData")
    header_size = fields.Integer(required=False, load_from="headerSize", dump_to="headerSize")
    body_size = fields.Integer(required=False, load_from="bodySize", dump_to="bodySize")


class ContentSchema(Schema):

    __model__ = Content

    size = fields.Integer(required=False, default=-1)
    mime_type = fields.String(required=False, allow_none=True, load_from="mimeType", dump_to="mimeType")
    text = fields.String(required=True)
    encoding = fields. String(required=False, allow_none=True)


class ResponseSchema(Schema):

    __model__ = Response

    status = fields.Integer(required=True)
    status_text = fields.String(required=True, load_from="statusText", dump_to="statusText")
    http_version = fields.String(required=False, load_from="httpVersion", dump_to="httpVersion")
    cookies = fields.Nested(CookieSchema, many=True)
    headers = fields.Nested(HeaderSchema, many=True)
    content = fields.Nested(ContentSchema, required=False, allow_none=True)
    redirect_url = fields.String(required=False, allow_none=True, load_from="redirectURL", dump_to="redirectURL")
    header_size = fields.Integer(required=False, default=-1, load_from="headerSize", dump_to="headerSize")
    body_size = fields.Integer(required=False, default=-1, load_from="bodySize", dump_to="bodySize")


class CacheStateSchema(Schema):

    __model__ = CacheState

    expires = fields.DateTime("iso", required=False, allow_none=True)
    last_access = fields.DateTime("iso", required=False, allow_none=True, load_from="lastAccess", dump_to="lastAccess")
    e_tag = fields.String(required=False, allow_none=True, load_from="eTag", dump_to="eTag")
    hit_count = fields.Integer(required=False, load_from="hitCount", dump_to="hitCount")


class CacheSchema(Schema):

    __model__ = Cache

    before_request = fields.Nested(CacheStateSchema, required=False, allow_none=True,
                                   load_from="beforeRequest", dump_to="beforeRequest")
    after_request = fields.Nested(CacheStateSchema, required=False, allow_none=True,
                                  load_from="afterRequest", dump_to="afterRequest")


class TimingsSchema(Schema):

    __model__ = Timings

    blocked = fields.Integer(required=False, default=-1)
    dns = fields.Integer(required=False, default=-1)
    connect = fields.Integer(required=False, default=-1)
    send = fields.Integer(required=False, default=-1)
    wait = fields.Integer(required=False, default=-1)
    receive = fields.Integer(required=False, default=-1)
    ssl = fields.Integer(required=False, default=-1)


class EntrySchema(Schema):

    __model__ = Entry

    pageref = fields.String(required=False, allow_none=True)
    started_date_time = fields.DateTime("iso", required=False, allow_none=True,
                                        load_from="startedDateTime", dump_to="startedDateTime")
    time = fields.Integer(required=False, default=-1)
    request = fields.Nested(RequestSchema, required=False, allow_none=True)
    response = fields.Nested(ResponseSchema, required=False, allow_none=True)
    cache = fields.Nested(CacheSchema, required=False, allow_none=True)
    timings = fields.Nested(TimingsSchema, required=False, allow_none=True)
    server_ip_address = fields.String(required=False, allow_none=True,
                                      load_from="serverIPAddress", dump_to="serverIPAddress")
    connection = fields.String(required=False, allow_none=True)


class CreatorSchema(Schema):

    __model__ = Creator

    name = fields.String(required=True)
    version = fields.String(required=True)


class BrowserSchema(Schema):

    __model__ = Browser

    name = fields.String(required=True)
    version = fields.String(required=True)


class PageTimingsSchema(Schema):

    __model__ = PageTimings

    on_content_load = fields.Integer(required=False, default=-1, load_from="onContentLoad", dump_to="onContentLoad")
    on_load = fields.Integer(required=False, default=-1, load_from="onLoad", dump_to="onLoad")


class PageSchema(Schema):

    __model__ = Page

    id = fields.String(required=True)
    title = fields.String(required=True)
    started_date_time = fields.DateTime("iso", required=False, allow_none=True,
                                        load_from="startedDateTime", dump_to="startedDateTime")
    page_timings = fields.Nested(PageTimingsSchema, required=False, allow_none=True,
                                 load_from="pageTimings", dump_to="pageTimings")


class LogSchema(Schema):

    __model__ = Log

    version = fields.String(required=False)
    creator = fields.Nested(CreatorSchema, required=False, allow_none=True)
    browser = fields.Nested(BrowserSchema, required=False, allow_none=True)
    pages = fields.Nested(PageSchema, many=True)
    entries = fields.Nested(EntrySchema, many=True)


class HARSchema(BaseSchema):

    __model__ = HAR

    log = fields.Nested(LogSchema, required=True)

    @post_load
    def load_extended(self, data):
        return self.__model__(**data)
