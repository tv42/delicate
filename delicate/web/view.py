from twisted.internet import defer
from twisted.python import log
from nevow import athena, loaders, util, tags, static
from delicate import ibookmark

class TagChooser(athena.LiveFragment):
    jsClass = u"Delicate.TagChooser.TagChooser"

    docFactory = loaders.stan(tags.div(
        id='delicate-tagchooser',
        render=tags.directive('liveFragment'),
        onload='Delicate.TagChooser.TagChooser.get(this).start()'))

    allowedMethods =  { 'getTags' : True }


    def _logError(self, fail):
        log.err(fail)
        return fail

    def getTags(self):
        d = defer.maybeDeferred(self.page.rootObject.getTags)
        d.addCallback(list)
        return d

class BookmarkList(athena.LiveFragment):
    jsClass = u"Delicate.BookmarkList.BookmarkList"

    docFactory = loaders.stan(tags.div(id='delicate-bookmarkList',
                                       render=tags.directive('liveFragment')))
    allowedMethods =  { 'getBookmarks' : True }

    def _logError(self, fail):
        log.err(fail)
        return fail

    def getBookmarks(self, tags=None, count=None):
        d = defer.maybeDeferred(self._getBookmarks,
                                tags=tags,
                                count=count)
        d.addErrback(self._logError)
        return d

    def _getBookmarks_2(self, iterable):
        for bookmark in iterable:
            data = {}
            for attr in ibookmark.IBookmark:
                val = getattr(bookmark, attr)
                if attr in ['created', 'modified']:
                    val = unicode(val.isoformat())
                data[unicode(attr)] = val
            data[u'id'] = bookmark.url
            yield data

    def _getBookmarks(self, tags, count):
        if tags is not None:
            tags = [str(tag) for tag in tags]
        bookmarks = self.page.rootObject.getBookmarks(tags=tags, count=count)

        l = list(self._getBookmarks_2(bookmarks))
        l.sort()
        return l

class ViewResource(athena.LivePage):
    addSlash = True
    docFactory = loaders.xmlfile(
        util.resource_filename('delicate.web', 'templates/view.html'))

    def __init__(self, *a, **kw):
        super(ViewResource, self).__init__(*a, **kw)
        self.jsModules.mapping.update({
            u'Delicate.TagChooser':
            util.resource_filename('delicate.web',
                                   'javascript/tagchooser.js'),
            u'Delicate.BookmarkList':
            util.resource_filename('delicate.web',
                                   'javascript/bookmarklist.js'),
            u'Delicate.Visual':
            util.resource_filename('delicate.web',
                                   'javascript/visual.js'),
            })

    child_style = static.File(util.resource_filename('delicate.web',
                                                     'style'));

    def render_tagChooser(self, ctx, data):
        frag = TagChooser()
        frag.page = self
        return ctx.tag.clear()[frag]

    def render_bookmarkList(self, ctx, data):
        frag = BookmarkList()
        frag.page = self
        return ctx.tag.clear()[frag]
