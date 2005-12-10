from twisted.trial import unittest
from twisted.trial.assertions import *
from delicate import bookmark, bookshelf
import os, datetime

class Operations(unittest.TestCase):
    def test_notFound(self):
        """Return None when no bookmark found."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        s = bookshelf.FileBookshelf(tmp)
        result = s.get('http://example.com/not-found')
        assertIdentical(result, None)

    def test_add_found(self):
        """After adding a bookmark, it can be found."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        url = 'http://example.com/foo'
        s = bookshelf.FileBookshelf(tmp)
        b = bookmark.Bookmark(url=url, title='foo')
        s.add(b)
        result = s.get(url)
        assertNotIdentical(result, None,
                           'Must find %r in %r' % (url, s))
        # it need not be identical, but it must be equal
        assertEqual(result, b)

    def test_persistent_add(self):
        """Bookmarks persist in the filesystem."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        url = 'http://example.com/foo'

        s1 = bookshelf.FileBookshelf(tmp)
        b = bookmark.Bookmark(url=url, title='foo')
        s1.add(b)

        s2 = bookshelf.FileBookshelf(tmp)
        result = s2.get(url)
        assertNotIdentical(result, None,
                           'Must find %r in %r' % (url, s2))
        # it need not be identical, but it must be equal
        assertEqual(result, b)

    def test_removed_not_found(self):
        """Removed bookmarks are no longer found."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        s = bookshelf.FileBookshelf(tmp)
        b = bookmark.Bookmark(url='http://example.com/not-found')
        s.add(b)
        s.remove('http://example.com/not-found')
        result = s.get('http://example.com/not-found')
        assertIdentical(result, None)

    def test_double_add(self):
        """Adding two bookmarks with same url preserves latter one."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        url = 'http://example.com/foo'
        s = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url=url, title='foo')
        s.add(b1)
        b2 = bookmark.Bookmark(url=url, title='bar')
        s.add(b2)
        result = s.get(url)
        assertNotIdentical(result, None,
                           'Must find %r in %r' % (url, s))
        assertNotEqual(result, b1)
        # it need not be identical, but it must be equal
        assertEqual(result, b2)
