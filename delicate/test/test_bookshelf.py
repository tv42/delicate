# -*- coding: utf-8 -*-
from twisted.trial import unittest
from delicate import bookmark, bookshelf
import os, sha, sets

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
        b = bookmark.Bookmark(url=url, title='foo',
                              description=u'blah blah\nblah blah',
                              tags=['bar', 'thud'])
        s1.add(b)

        s2 = bookshelf.FileBookshelf(tmp)
        result = s2.get(url)
        self.assertNotIdentical(result, None,
                                'Must find %r in %r' % (url, s2))
        # it need not be identical, but it must be equal
        self.assertEqual(result, b)

    def test_description_trailingNewLine(self):
        """Bookmarks persist in the filesystem."""
        tmp = self.mktemp()
        os.mkdir(tmp)
        url = 'http://example.com/foo'

        s1 = bookshelf.FileBookshelf(tmp)
        b = bookmark.Bookmark(url=url, title='foo',
                              description=u'blah blah\nblah blah\n')
        s1.add(b)

        s2 = bookshelf.FileBookshelf(tmp)
        result = s2.get(url)
        self.assertEqual(result, b)
        self.assertEqual(result.description, u'blah blah\nblah blah\n')

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
                              description.encode('utf-8'))
        self.assertFileEquals(os.path.join(path, 'tags'),
                              u'\n'.join(tags).encode('utf-8')+'\n')

    def test_getBookmarks_empty(self):
        """getBookmarks() returns no bookmarks for empty shelves."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        i = s1.getBookmarks()
        l = list(i)
        self.assertEquals(l, [])

    def test_getBookmarks_simple(self):
        """getBookmarks() returns stored bookmarks."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        url = 'http://example.com/foo'
        b = bookmark.Bookmark(url=url, title='foo')
        s1.add(b)

        s1 = bookshelf.FileBookshelf(tmp)
        i = s1.getBookmarks()
        l = list(i)
        self.assertEquals(l, [b])

    def test_getBookmarks_tags(self):
        """getBookmarks() return exactly the bookmarks that match all tags."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url='http://example.com/foo', title='foo')
        b2 = bookmark.Bookmark(url='http://example.com/bar', title='bar',
                               tags=['xyzzy'])
        b3 = bookmark.Bookmark(url='http://example.com/baz', title='baz',
                               tags=['thud', 'quux'])
        s1.add(b1)
        s1.add(b2)
        s1.add(b3)

        i = s1.getBookmarks(['thud'])
        l = list(i)
        self.assertEquals(l, [b3])

    def test_getBookmarks_tags_neverMatch(self):
        """getBookmarks() return nothing if given a tag no bookmark has."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url='http://example.com/foo', title='foo')
        b2 = bookmark.Bookmark(url='http://example.com/bar', title='bar',
                               tags=['xyzzy'])
        b3 = bookmark.Bookmark(url='http://example.com/baz', title='baz',
                               tags=['thud', 'quux'])
        s1.add(b1)
        s1.add(b2)
        s1.add(b3)

        i = s1.getBookmarks(['impossible'])
        l = list(i)
        self.assertEquals(l, [])

    def test_getBookmarks_tags_emptyIntersection(self):
        """getBookmarks() return nothing if given a tag no bookmark has."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url='http://example.com/foo', title='foo')
        b2 = bookmark.Bookmark(url='http://example.com/bar', title='bar',
                               tags=['xyzzy'])
        b3 = bookmark.Bookmark(url='http://example.com/baz', title='baz',
                               tags=['thud', 'quux'])
        s1.add(b1)
        s1.add(b2)
        s1.add(b3)

        i = s1.getBookmarks(['thud', 'xyzzy'])
        l = list(i)
        self.assertEquals(l, [])

    def test_getBookmarks_cache_format(self):
        """getBookmarks() caches results on disk."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url='http://example.com/foo', title='foo')
        b2 = bookmark.Bookmark(url='http://example.com/bar', title='bar',
                               tags=['xyzzy'])
        b3 = bookmark.Bookmark(url='http://example.com/baz', title='baz',
                               tags=['thud', 'quux'])
        s1.add(b1)
        s1.add(b2)
        s1.add(b3)

        cache = os.path.join(tmp, '.cache')
        self.failIf(os.path.exists(cache))

        self.assertEquals(list(s1.getBookmarks(['thud'])), [b3])
        self.failUnless(os.path.isdir(cache))
        self.assertEquals(os.listdir(cache), ['by-tag'])
        self.assertEquals(os.listdir(os.path.join(cache, 'by-tag')),
                          ['thud'])
        self.assertFileEquals(os.path.join(cache, 'by-tag', 'thud'),
                              b3.url+'\n')

        self.assertEquals(list(s1.getBookmarks(['xyzzy'])), [b2])
        self.failUnless(os.path.isdir(cache))
        self.assertEquals(os.listdir(cache), ['by-tag'])
        self.assertEquals(sets.Set(os.listdir(os.path.join(cache, 'by-tag'))),
                          sets.Set(['thud', 'xyzzy']))
        self.assertFileEquals(os.path.join(cache, 'by-tag', 'thud'),
                              b3.url+'\n')
        self.assertFileEquals(os.path.join(cache, 'by-tag', 'xyzzy'),
                              b2.url+'\n')

    def test_getBookmarks_cache_is_used(self):
        """getBookmarks() really uses the cache."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url='http://example.com/foo', title='foo')
        b2 = bookmark.Bookmark(url='http://example.com/bar', title='bar',
                               tags=['xyzzy'])
        b3 = bookmark.Bookmark(url='http://example.com/baz', title='baz',
                               tags=['thud', 'quux'])
        s1.add(b1)
        s1.add(b2)
        s1.add(b3)

        self.assertEquals(list(s1.getBookmarks(['thud'])), [b3])
        s1._getAllBookmarks = lambda *a, **kw: self.fail('getBookmarks() must use cache')
        self.assertEquals(list(s1.getBookmarks(['thud'])), [b3])

    def test_getTags_empty(self):
        """getTags() returns no tags for empty shelves."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        d = s1.getTags()
        d.addCallback(self.assertEquals, sets.Set())
        return d

    def test_getTags_noTags(self):
        """getTags() returns no tags for bookmarks with no tags."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b = bookmark.Bookmark(url='http://example.com/foo', title='foo')
        s1.add(b)

        d = s1.getTags()
        d.addCallback(self.assertEquals, sets.Set())
        return d

    def test_getTags_simple(self):
        """getTags() returns stored tags."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url='http://example.com/foo', title='foo',
                               tags=['quux'])
        b2 = bookmark.Bookmark(url='http://example.com/bar', title='bar')
        b3 = bookmark.Bookmark(url='http://example.com/baz', title='baz',
                               tags=['thud', 'xyzzy'])
        s1.add(b1)
        s1.add(b2)
        s1.add(b3)

        s1 = bookshelf.FileBookshelf(tmp)
        def test(shelf):
            d = shelf.getTags()
            d.addCallback(self.assertEquals, sets.Set([u'quux', u'thud', u'xyzzy']))
            return d

        # repeat a bit to flush out bugs in caching
        d = test(s1)
        d.addCallback(lambda dummy: test(s1))
        d.addCallback(lambda dummy: test(s1))
        return d

    def test_getTags_cache_format(self):
        """getTags() caches results on disk."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url='http://example.com/foo', title='foo')
        b2 = bookmark.Bookmark(url='http://example.com/bar', title='bar',
                               tags=['xyzzy'])
        b3 = bookmark.Bookmark(url='http://example.com/baz', title='baz',
                               tags=['thud', 'quux'])
        s1.add(b1)
        s1.add(b2)
        s1.add(b3)

        cache = os.path.join(tmp, '.cache')
        self.failIf(os.path.exists(cache))

        d = s1.getTags()
        d.addCallback(self.assertEquals, sets.Set(['xyzzy', 'thud', 'quux']))

        def cb(dummy):
            self.failUnless(os.path.isdir(cache))
            self.assertEquals(os.listdir(cache), ['taglist.txt'])
            path = os.path.join(cache, 'taglist.txt')
            f = file(path)
            data = f.read()
            f.close()
            got = sets.Set(data.splitlines())
            want = sets.Set(['xyzzy', 'thud', 'quux'])
            self.assertEquals(got, want)

        d.addCallback(cb)
        return d

    def test_getTags_cache_is_used(self):
        """getTags() really uses the cache."""
        tmp = self.mktemp()
        os.mkdir(tmp)

        s1 = bookshelf.FileBookshelf(tmp)
        b1 = bookmark.Bookmark(url='http://example.com/foo', title='foo')
        b2 = bookmark.Bookmark(url='http://example.com/bar', title='bar',
                               tags=['xyzzy'])
        b3 = bookmark.Bookmark(url='http://example.com/baz', title='baz',
                               tags=['thud', 'quux'])
        s1.add(b1)
        s1.add(b2)
        s1.add(b3)

        d = s1.getTags()
        d.addCallback(self.assertEquals, sets.Set(['xyzzy', 'thud', 'quux']))

        def cb(dummy):
            s1.getBookmarks = lambda *a, **kw: self.fail('getTags() must use cache')
            d = s1.getTags()
            d.addCallback(self.assertEquals, sets.Set(['xyzzy', 'thud', 'quux']))

        d.addCallback(cb)
        return d
