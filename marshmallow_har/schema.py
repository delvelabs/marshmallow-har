from .model import Cookie, Request, Response, Entry, HAR, Header, Param, PostData, PostParam
from .model import Log, Page, Creator, Browser, Cache, CacheState, Timings, Content, PageTimings


CookieSchema = Cookie.__schema__
HeaderSchema = Header.__schema__
ParamSchema = Param.__schema__
PostParamSchema = PostParam.__schema__
PostDataSchema = PostData.__schema__
RequestSchema = Request.__schema__
ContentSchema = Content.__schema__
ResponseSchema = Response.__schema__
CacheStateSchema = CacheState.__schema__
CacheSchema = Cache.__schema__
TimingsSchema = Timings.__schema__
EntrySchema = Entry.__schema__
CreatorSchema = Creator.__schema__
BrowserSchema = Browser.__schema__
PageTimingsSchema = PageTimings.__schema__
PageSchema = Page.__schema__
LogSchema = Log.__schema__
HARSchema = HAR.__schema__
