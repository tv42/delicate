"""Parse bookmarks exported as HTML from del.icio.us."""

from zope.interface import implements
import datetime, sets, itertools
from twisted.web import microdom

from delicate import ibookshelf, bookmark

class DeliciousBookmarkShelf(object):
    implements(ibookshelf.IBookmarkShelf)

    def __init__(self, filename):
        self.filename = filename

    def _timestamp(self, seconds):
        return datetime.datetime.fromtimestamp(int(seconds))

    def _getText_2(self, nodes):
        for node in nodes:
            if isinstance(node, microdom.Text):
                yield node.value.decode('utf-8')
            elif isinstance(node, microdom.EntityReference):
                found = None
                for char, xml in microdom.REV_HTML_ESCAPE_CHARS:
                    if xml == ('&%s;' % node.eref):
                        found = char
                        break

                if found is not None:
                    yield found.decode('utf-8')
                else:
                    raise RuntimeError('Unknown entity reference: %s' % node.eref)
            else:
                raise RuntimeError('Not a text node: %r' % node)

    def _getText(self, nodes):
        return u''.join(self._getText_2(nodes))

    def _nodeToBookmark(self, dt):
        assert dt.nodeName == 'dt'
        i = dt.parentNode.childNodes.index(dt)
        try:
            dd = dt.parentNode.childNodes[i+1]
        except IndexError:
            dd = None
        else:
            assert dd.nodeName == 'dd'

        links = dt.getElementsByTagName('a')
        assert len(links) == 1
        a = links[0]

        assert len(a.childNodes) >= 1
        bm = bookmark.Bookmark(
            url=a.getAttribute('href', '').decode('utf-8'),
            title=self._getText(a.childNodes),
            created=self._timestamp(a.getAttribute('add_date')),
            modified=self._timestamp(a.getAttribute('last_modified')),
            tags=a.getAttribute('tags', '').decode('utf-8').split(None))

        if dd is None:
            desc = None
        else:
            desc = self._getText(dd.childNodes)

            suffixes = [
                u' (tags:  %s)\n' % u' '.join(bm.tags),
                u'\n(tags: %s)\n' % u' '.join(bm.tags),
                ]
            for suffix in suffixes:
                if desc.endswith(suffix):
                    desc = desc[:-len(suffix)]
                    break
            if desc == '':
                desc = None
        bm.description = desc
        return bm

    def get(self, url):
        tree = microdom.parse(self.filename, beExtremelyLenient=True)
        for dl in tree.getElementsByTagName('dl'):
            for a in dl.getElementsByTagName('a'):
                if a.getAttribute('href') == url:
                    if a.parentNode.nodeName == 'dt':
                        return self._nodeToBookmark(a.parentNode)

    def _getAllBookmarks(self):
        # workaround for http://twistedmatrix.com/bugs/issue1358
        laterClosers = {}
        laterClosers.update(microdom.MicroDOMParser.laterClosers)
        laterClosers['p'] = microdom.MicroDOMParser.laterClosers.get('p', []) + ['DT']
        laterClosers['dt'] = microdom.MicroDOMParser.laterClosers.get('dt', []) + ['DD']
        laterClosers['dd'] = microdom.MicroDOMParser.laterClosers.get('dd', []) + ['DT']

        tree = microdom.parse(self.filename, beExtremelyLenient=True, laterClosers=laterClosers)
        for dl in tree.getElementsByTagName('dl'):
            for dt in dl.getElementsByTagName('dt'):
                yield self._nodeToBookmark(dt)

    def getBookmarks(self, tags=None, count=None):
        r = self._getAllBookmarks()
        if tags is not None:
            musthave = sets.ImmutableSet(tags)
            r = itertools.ifilter(
                lambda b: musthave <= sets.ImmutableSet(b.tags), r)
        if count is not None:
            r = itertools.islice(r, count)
        return r

    def getTags(self):
        tags = sets.Set()
        for bookmark in self.getBookmarks():
            tags.update(sets.ImmutableSet(bookmark.tags))
        return tags
