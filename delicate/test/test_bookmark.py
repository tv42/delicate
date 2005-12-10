from twisted.trial import unittest
from twisted.trial.assertions import *
from delicate import bookmark, ibookmark
import datetime

class Instantiate(unittest.TestCase):
    def test_missingURL(self):
        """Missing url argument raises TypeError."""
        e = failUnlessRaises(TypeError, bookmark.Bookmark)
        failUnlessEqual(str(e), "Bookmark() missing keyword argument 'url'")

    def test_minimal(self):
        """Arguments url and title are the only mandatory arguments."""
        b = bookmark.Bookmark(url='foo')
        failUnlessEqual(b.url, 'foo')
        failUnlessEqual(b.title, None)
        failUnlessEqual(b.description, None)
        failUnlessEqual(b.tags, [])
        failIfEqual(b.created, None)
        failIfEqual(b.modified, None)
        ibookmark.IBookmark.validateInvariants(b)

    def test_full(self):
        """Bookmark creation understands wanted things and assigns to self."""
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b = bookmark.Bookmark(url='foo', title='bar',
                              description='longer description',
                              tags=['thud', 'quux'],
                              created=created,
                              modified=modified)
        failUnlessEqual(b.url, 'foo')
        failUnlessEqual(b.title, 'bar')
        failUnlessEqual(b.description, 'longer description')
        failUnlessEqual(b.tags, ['thud', 'quux'])
        failUnlessEqual(b.created, created)
        failUnlessEqual(b.modified, modified)
        ibookmark.IBookmark.validateInvariants(b)

class Compare(unittest.TestCase):
    def test_self(self):
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b = bookmark.Bookmark(url='foo', title='bar',
                              description='longer description',
                              tags=['thud', 'quux'],
                              created=created,
                              modified=modified)
        assertEqual(b, b)

    def test_equal(self):
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b1 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b2 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        assertEqual(b1, b2)

    def test_different_url(self):
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b1 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b2 = bookmark.Bookmark(url='notfoo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        assertNotEqual(b1, b2)

    def test_different_title(self):
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b1 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b2 = bookmark.Bookmark(url='foo', title='notbar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        assertNotEqual(b1, b2)

    def test_different_description(self):
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b1 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b2 = bookmark.Bookmark(url='foo', title='bar',
                               description='not longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        assertNotEqual(b1, b2)

    def test_different_tags(self):
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b1 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b2 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['not', 'thud', 'quux'],
                               created=created,
                               modified=modified)
        assertNotEqual(b1, b2)

    def test_different_created(self):
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b1 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        created = datetime.datetime(2005, 1, 1, 10, 15, 01)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b2 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        assertNotEqual(b1, b2)

    def test_different_modified(self):
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 00)
        b1 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        created = datetime.datetime(2005, 1, 1, 10, 15, 00)
        modified = datetime.datetime(2005, 1, 2, 10, 25, 01)
        b2 = bookmark.Bookmark(url='foo', title='bar',
                               description='longer description',
                               tags=['thud', 'quux'],
                               created=created,
                               modified=modified)
        assertNotEqual(b1, b2)
