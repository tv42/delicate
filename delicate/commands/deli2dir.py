import os
from twisted.python import usage
from zope.interface import implements
from delicate import bookshelf
from delicate.delicious import fromdelicious
from delicate.usage import ICommand

class Deli2Dir(usage.Options):
    """
    Convert delicious export.html to a directory tree.

    The export.html file must be UTF-8 encoded.
    """
    implements(ICommand)

    def parseArgs(self, export, path):
	self['export'] = export
	self['path'] = path

    def postOptions(self):
        os.mkdir(self['path'])
        src = fromdelicious.DeliciousBookmarkShelf(self['export'])
        dst = bookshelf.FileBookshelf(self['path'])
        for bookmark in src:
            dst.add(bookmark)

x = Deli2Dir()
