import sys
from twisted.python import usage
from zope.interface import implements
from delicate.usage import ICommand

class Del(usage.Options):
    """Remove a bookmark."""
    implements(ICommand)

    def parseArgs(self, url):
	self['url'] = url

    def postOptions(self):
        self.parent['bookshelf'].remove(self['url'])

x = Del()
