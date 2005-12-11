# -*- coding: utf-8 -*-
from twisted.trial import unittest
from delicate import bookmark, bookshelf
import os, datetime, sha, sets

class Operations(unittest.TestCase):
    def test_notFound(self):
        """Return None when no bookmark found."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        s = bookshelf.FileBookshelf(tmp)
        result = s.get('http://example.com/not-found')
        self.assertIdentical(result, None)

    def test_add_found(self):
        """After adding a bookmark, it can be found."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        url = 'http://example.com/foo'
        s = bookshelf.FileBookshelf(tmp)
        b = bookmark.Bookmark(url=url, title='foo')
        s.add(b)
        result = s.get(url)
        self.assertNotIdentical(result, None,
                                'Must find %r in %r' % (url, s))
        # it need not be identical, but it must be equal
        self.assertEqual(result, b)

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
        self.assertNotIdentical(result, None,
                                'Must find %r in %r' % (url, s2))
        # it need not be identical, but it must be equal
        self.assertEqual(result, b)

    def test_removed_not_found(self):
        """Removed bookmarks are no longer found."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        s = bookshelf.FileBookshelf(tmp)
        b = bookmark.Bookmark(url='http://example.com/not-found')
        s.add(b)
        s.remove('http://example.com/not-found')
        result = s.get('http://example.com/not-found')
        self.assertIdentical(result, None)

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
        self.assertNotIdentical(result, None,
                                'Must find %r in %r' % (url, s))
        self.assertNotEqual(result, b1)
        # it need not be identical, but it must be equal
        self.assertEqual(result, b2)

    def assertFileEquals(self, path, want):
        f = file(path)
        got = f.read()
        f.close()
        self.assertEquals(got, want)

    def test_encoding(self):
        """Files are saved as UTF-8."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        s = bookshelf.FileBookshelf(tmp)
        url = u'http://example.com/foo/bläh'
        title = u'titlöh'
        description = u'deskriipsöni'
        tags = [u'föö', u'bär']
        b = bookmark.Bookmark(url=url,
                              title=title,
                              description=description,
                              tags=tags,
                              )
        s.add(b)
        hashed = sha.new(url.encode('utf-8')).hexdigest()
        self.assertEquals(os.listdir(tmp), [hashed])
        path = os.path.join(tmp, hashed)
        got = sets.Set(os.listdir(path))
        want = sets.Set(['url', 'title', 'description', 'tags',
                         'created', 'modified'])
        self.assertEquals(got, want)
        self.assertFileEquals(os.path.join(path, 'url'),
                              url.encode('utf-8')+'\n')
        self.assertFileEquals(os.path.join(path, 'title'),
                              title.encode('utf-8')+'\n')
        self.assertFileEquals(os.path.join(path, 'description'),
                              description.encode('utf-8')+'\n')
        self.assertFileEquals(os.path.join(path, 'tags'),
                              u'\n'.join(tags).encode('utf-8')+'\n')
