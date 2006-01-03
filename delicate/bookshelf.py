from zope.interface import implements
import os, errno, sha, datetime, codecs, sets, re, itertools
from twisted.internet import defer
from twisted.python import log
from delicate import ibookshelf, bookmark

class FileBookshelf(object):
    implements(ibookshelf.IWritableBookmarkShelf)

    path = None

    def __init__(self, path, *a, **kw):
        super(FileBookshelf, self).__init__(*a, **kw)
        self.path = path

    def _hash(self, url):
        return sha.new(url.encode('utf-8')).hexdigest()

    def _hash_safe(self, url):
        """
        Get hash for this url, also check for collisions.
        Bookmark for URL must exist for this to work.
        Returns None on collisions or if no such URL is found.
        """
        h = self._hash(url)
        path = os.path.join(self.path, h)

        fp = self._try_open(os.path.join(path, 'url'))
        if fp is None:
            return None

        url2 = self._readline(fp)
        fp.close()

        if url != url2:
            log.msg('Hash collision between %r and %r.' % (url, url2))
            return None

        return h

    def _write(self, fp, data):
        print >>fp, data
    def _writeall(self, fp, data):
        fp.write(data)
    def _writelist(self, fp, data):
        for item in data:
            print >>fp, item
    def _writetime(self, fp, data):
        seconds = float(data.strftime('%s')) + (data.microsecond/1000000.0)
        self._write(fp, repr(seconds))

    def add(self, bookmark):
        h = self._hash(bookmark.url)
        tmp = os.path.join(self.path, '%s.tmp' % h)
        os.mkdir(tmp) #TODO handle errors
        writers = {
            'url': self._write,
            'title': self._write,
            'description': self._writeall,
            'tags': self._writelist,
            'created': self._writetime,
            'modified': self._writetime,
            }
        for field, writer in writers.items():
            value = getattr(bookmark, field, None)
            if value is not None:
                fp = codecs.open(os.path.join(tmp, field),
                                 mode='w',
                                 encoding='utf-8')
                writer(fp, value)
                os.fsync(fp)
                fp.close()
        while True:
            try:
                os.rename(tmp, os.path.join(self.path, h))
            except OSError, e:
                if e.errno in (errno.ENOTEMPTY, errno.EEXIST):
                    # need to clean up old directory first
                    self.remove(bookmark.url)
                else:
                    raise
            else:
                break

    def _try_mkdir(self, path):
        try:
            os.mkdir(path)
        except OSError, e:
            if e.errno == errno.EEXIST:
                return None
            else:
                raise

    def _try_open(self, path):
        try:
            return codecs.open(path, encoding='utf-8')
        except IOError, e:
            if e.errno == errno.ENOENT:
                return None
            else:
                raise

    def _readline(self, fp):
        line = fp.readline()
        while (line.endswith('\n')
               or line.endswith('\r')):
            line = line[:-1]
        return line
    def _readall(self, fp):
        return fp.read()
    def _readlist(self, fp):
        return [line.rstrip('\n') for line in fp]
    def _readtime(self, fp):
        line = self._readline(fp)
        seconds = float(line)
        return datetime.datetime.fromtimestamp(seconds)

    def get(self, url):
        h = self._hash_safe(url)
        if h is None:
            return None
        path = os.path.join(self.path, h)

        readers = {
            'title': self._readline,
            'description': self._readall,
            'tags': self._readlist,
            'created': self._readtime,
            'modified': self._readtime,
            }
        data = {
            'url': url,
            }
        for field, reader in readers.items():
            fp = self._try_open(os.path.join(path, field))
            if fp is not None:
                value = reader(fp)
                fp.close()
                data[field] = value
        return bookmark.Bookmark(**data)

    def remove(self, url):
        h = self._hash_safe(url)
        if h is None:
            # TODO raise to complain about nonexisting bookmark?
            return None

        # rename for atomicity
        tmppath = os.path.join(self.path, '%s.remove' % h)
        os.rename(os.path.join(self.path, h), tmppath)
        for filename in ['url',
                         'title',
                         'description',
                         'tags',
                         'created',
                         'modified',
                         ]:
            try:
                os.unlink(os.path.join(tmppath, filename))
            except OSError, e:
                if e.errno == errno.ENOENT:
                    pass
                else:
                    raise
        os.rmdir(tmppath)

    def _getAllBookmarks(self):
        for dirname in os.listdir(self.path):
            if '.' in dirname:
                continue
            else:
                path = os.path.join(self.path,
                                    dirname,
                                    'url')
                fp = self._try_open(path)
                if fp is None:
                    continue
                url = self._readline(fp)
                fp.close()
                bookmark = self.get(url)
                if bookmark is not None:
                    yield bookmark

    _SAFE_TAG = re.compile('^[a-z0-9][a-z0-9:_-]*$')

    def _getTagCache(self, tag):
        # TODO enforce tag sanity better and in one place
        if not self._SAFE_TAG.search(tag):
            log.msg('Not caching unsafe tag: %r' % tag)
            return

        fp = self._try_open(os.path.join(self.path,
                                         '.cache',
                                         'by-tag',
                                         tag))
        if fp is None:
            return None
        urls = self._readlist(fp)
        fp.close()
        return sets.ImmutableSet(urls)

    def _saveTagCache(self, tag, urls):
        # TODO enforce tag sanity better and in one place
        if not self._SAFE_TAG.search(tag):
            log.msg('Not caching unsafe tag: %r' % tag)
            return

        cache = os.path.join(self.path, '.cache')
        self._try_mkdir(cache)
        by_tag = os.path.join(cache, 'by-tag')
        self._try_mkdir(by_tag)
        path = os.path.join(by_tag, '%s.%d.tmp' % (tag, os.getpid()))
        fp = file(path, 'w')
        self._writelist(fp, urls)
        fp.close()
        os.rename(path, os.path.join(by_tag, tag))

    def _intersect(self, a, b):
        """
        Return intersection of sets a and b, with the exception that
        for a, None is taken to mean an infinite set.
        """
        if a is None:
            return b
        else:
            return a & b

    def _refreshTagCache(self, tags):
        added = {}
        for bookmark in self._getAllBookmarks():
            wanted = tags & sets.ImmutableSet(bookmark.tags)
            for tag in wanted:
                added.setdefault(tag, sets.Set()).add(bookmark.url)

        for tag, urls in added.items():
            self._saveTagCache(tag, urls)

        tags = sets.ImmutableSet(added.keys())
        urls = None
        for l in added.values():
            urls = self._intersect(urls, l)
        return tags, urls

    def _getTaggedBookmarks(self, tags):
        tags = sets.Set(tags)
        missing = sets.Set()

        matches = None
        while tags:
            tag = tags.pop()
            urls = self._getTagCache(tag)
            if urls is not None:
                matches = self._intersect(matches, urls)
            else:
                missing.add(tag)

        if missing:
            # missing or stale by-tag caches, (re)create
            addedTags, urls = self._refreshTagCache(missing)
            missing -= addedTags
            matches = self._intersect(matches, urls)

        if missing:
            # some tags requested never matched any bookmark, so
            # return empty set
            return

        if matches is None:
            return

        for url in matches:
            yield self.get(url)

    def getBookmarks(self, tags=None, count=None):
        if tags:
            r = iter(self._getTaggedBookmarks(tags))
        else:
            r = iter(self._getAllBookmarks())
        if count is not None:
            r = itertools.islice(r, count)
        return r

    def _getTags(self):
        tags = sets.Set()
        for bookmark in self.getBookmarks():
            tags.update(sets.ImmutableSet(bookmark.tags))
        return tags

    def _getTags_cached(self):
        fp = self._try_open(os.path.join(self.path,
                                         '.cache',
                                         'taglist.txt'))
        if fp is None:
            return None

        tags = sets.ImmutableSet(self._readlist(fp))
        fp.close()
        return tags

    def _cacheTags(self, tags):
        cache = os.path.join(self.path, '.cache')
        self._try_mkdir(cache)
        path = os.path.join(cache,
                            'taglist.%d.tmp' % os.getpid())
        fp = file(path, 'w')
        self._writelist(fp, tags)
        fp.close()
        os.rename(path, os.path.join(cache, 'taglist.txt'))
        return tags

    def getTags(self):
        d = defer.maybeDeferred(self._getTags_cached)

        def loadIfNeeded(tags):
            if tags is not None:
                # read from cache
                return tags
            else:
                d = defer.maybeDeferred(self._getTags)
                d.addCallback(self._cacheTags)
                return d
        d.addCallback(loadIfNeeded)

        return d
