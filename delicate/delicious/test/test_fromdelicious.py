from twisted.trial import unittest
from zope.interface import verify as ziverify
from twisted.python import util
import datetime, sets
from delicate import ibookshelf, ibookmark
from delicate.delicious import fromdelicious

class FromDelicious(unittest.TestCase):
    def validate(self, iface, thing):
        ziverify.verifyObject(iface, thing)
        iface.validateInvariants(thing)

    def test_simple(self):
        # export.html is hand-crafted based on a page save
        # mangled by Firefox
        filename = util.sibpath(__file__, 'export.html')
        shelf = fromdelicious.DeliciousBookmarkShelf(filename)
        self.validate(ibookshelf.IBookmarkShelf, shelf)

        self.assertEquals(len(list(shelf.getBookmarks())), 3)

        for bookmark in shelf.getBookmarks():
            self.validate(ibookmark.IBookmark, bookmark)

        notfound = shelf.get('http://not-there/')
        self.assertIdentical(notfound, None)

        a = shelf.get('http://www.example.com/url1')
        self.validate(ibookmark.IBookmark, a)
        self.assertEquals(a.url, 'http://www.example.com/url1')
        self.assertEquals(a.title, 'Title one is pretty vague')
        self.assertIdentical(a.description, None)
        self.assertEquals(a.created,
                          datetime.datetime(2005, 12, 10, 19, 41, 38))
        self.assertEquals(a.modified,
                          datetime.datetime(2005, 12, 10, 19, 41, 38))
        self.assertEquals(a.tags, ['foo', 'bar'])

        b = shelf.get('http://example.org/')
        self.validate(ibookmark.IBookmark, b)
        self.assertEquals(b.url, 'http://example.org/')
        self.assertEquals(b.title, 'Second link title & more here')
        self.assertIdentical(b.description, None)
        self.assertEquals(b.created,
                          datetime.datetime(2005, 12, 7, 18, 12, 16))
        self.assertEquals(b.modified,
                          datetime.datetime(2005, 12, 7, 18, 12, 16))
        self.assertEquals(b.tags, ['system:unfiled'])

        c = shelf.get('http://third.one.invalid/')
        self.validate(ibookmark.IBookmark, c)
        self.assertEquals(c.url, 'http://third.one.invalid/')
        self.assertEquals(c.title, 'Third title')
        self.assertEquals(c.description, '''This item has a very very, very, very long description
that goes on and on and on and on and on and on and on & on
but actually del.icio.us seems to truncate them at some point which is really stup ...''')
        self.assertEquals(c.created,
                          datetime.datetime(2005, 12, 5, 18, 29, 29))
        self.assertEquals(c.modified,
                          datetime.datetime(2005, 12, 5, 18, 29, 29))
        self.assertEquals(c.tags, ['xyzzy', 'foo'])

    def test_simple_tags(self):
        filename = util.sibpath(__file__, 'export.html')
        shelf = fromdelicious.DeliciousBookmarkShelf(filename)
        l = shelf.getBookmarks(tags=['foo'])
        l = list(l)
        self.assertEquals(len(l), 2)
        want = sets.ImmutableSet(['http://www.example.com/url1',
                                  'http://third.one.invalid/'])
        got = sets.ImmutableSet([b.url for b in l])
        self.assertEquals(want, got)

    def test_dialtone(self):
        # export.html received from dialtone, apparently without
        # any browser mangling
        filename = util.sibpath(__file__, 'export-dialtone.html')
        shelf = fromdelicious.DeliciousBookmarkShelf(filename)
        self.validate(ibookshelf.IBookmarkShelf, shelf)

        self.assertEquals(len(list(shelf.getBookmarks())), 45)

        for bookmark in shelf.getBookmarks():
            self.validate(ibookmark.IBookmark, bookmark)

        notfound = shelf.get('http://not-there/')
        self.assertIdentical(notfound, None)
