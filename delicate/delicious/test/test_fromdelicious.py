from twisted.trial import unittest
from twisted.python import util
import datetime
from delicate.delicious import fromdelicious

class FromDelicious(unittest.TestCase):
    def test_simple(self):
        # export.html is hand-crafted based on a page save
        # mangled by Firefox
        filename = util.sibpath(__file__, 'export.html')
        shelf = fromdelicious.DeliciousBookmarkShelf(filename)

        self.assertEquals(len(list(iter(shelf))), 3)

        notfound = shelf.get('http://not-there/')
        self.assertIdentical(notfound, None)

        a = shelf.get('http://www.example.com/url1')
        self.assertEquals(a.url, 'http://www.example.com/url1')
        self.assertEquals(a.title, 'Title one is pretty vague')
        self.assertIdentical(a.description, None)
        self.assertEquals(a.created,
                          datetime.datetime(2005, 12, 10, 19, 41, 38))
        self.assertEquals(a.modified,
                          datetime.datetime(2005, 12, 10, 19, 41, 38))
        self.assertEquals(a.tags, ['foo', 'bar'])

        b = shelf.get('http://example.org/')
        self.assertEquals(b.url, 'http://example.org/')
        self.assertEquals(b.title, 'Second link title & more here')
        self.assertIdentical(b.description, None)
        self.assertEquals(b.created,
                          datetime.datetime(2005, 12, 7, 18, 12, 16))
        self.assertEquals(b.modified,
                          datetime.datetime(2005, 12, 7, 18, 12, 16))
        self.assertEquals(b.tags, ['system:unfiled'])

        c = shelf.get('http://third.one.invalid/')
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

    def test_dialtone(self):
        # export.html received from dialtone, apparently without
        # any browser mangling
        filename = util.sibpath(__file__, 'export-dialtone.html')
        shelf = fromdelicious.DeliciousBookmarkShelf(filename)

        self.assertEquals(len(list(iter(shelf))), 45)

        notfound = shelf.get('http://not-there/')
        self.assertIdentical(notfound, None)
