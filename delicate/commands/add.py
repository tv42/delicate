import sys
from twisted.python import usage
from zope.interface import implements
from delicate import bookmark
from delicate.usage import ICommand

class Add(usage.Options):
    """Add a bookmark."""
    implements(ICommand)

    optParameters = [
	('title', None, None,
	 "Title of the resource linked to"),
	('description', None, None,
	 "Longer description of the resource linked to"),
	]

    def parseArgs(self, url, *tags):
	self['url'] = url
	self['tags'] = tags

    def postOptions(self):
        b = bookmark.Bookmark(url=self['url'],
                              title=self['title'],
                              description=self['description'],
                              tags=self['tags'])
        self.parent['bookshelf'].add(b)

x = Add()
