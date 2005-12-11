from zope.interface import implements
import os, errno, sha, time, datetime
from twisted.python import log
from delicate import ibookshelf, bookmark

class FileBookshelf(object):
    implements(ibookshelf.IBookmarkShelf)

    path = None

    def __init__(self, path, *a, **kw):
        super(FileBookshelf, self).__init__(*a, **kw)
        self.path = path

    def _hash(self, url):
        return sha.new(url).hexdigest()

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
            'description': self._write,
            'tags': self._writelist,
            'created': self._writetime,
            'modified': self._writetime,
            }
        for field, writer in writers.items():
            value = getattr(bookmark, field, None)
            if value is not None:
                fp = file(os.path.join(tmp, field), 'w')
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

    def _try_open(self, path):
        try:
            return file(path)
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
        return list(fp.xreadlines())
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
