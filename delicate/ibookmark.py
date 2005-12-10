import zope.interface as zi

class URLMissingError(zi.Invalid):
    """Bookmark is missing mandatory attribute url"""

    def __str__(self):
        return '%s: %s' % (self.__doc__, ', '.join([repr(x) for x in self.args]))

def _url_is_mandatory(bookmark):
    if getattr(bookmark, 'url', None) is None:
        raise URLMissingError, bookmark

class TagsMustBeSequenceError(zi.Invalid):
    """Tags must be a sequence"""
    def __str__(self):
        return '%s: %s' % (self.__doc__, ', '.join([str(x) for x in self.args]))

def _tags_is_sequence(bookmark):
    tags = bookmark.tags
    if tags is None:
        return
    try:
        list(tags)
    except TypeError, e:
        raise TagsMustBeSequenceError, e

# TODO invariants for:
# url
# title
# description
# created

# TODO maybe this much z.i is insane

class IBookmark(zi.Interface):
    """A bookmark."""

    url = zi.Attribute("The bookmarked URL")

    title = zi.Attribute("Title of the bookmarked resource")

    description = zi.Attribute("Longer description of the bookmarked resource")

    tags = zi.Attribute("List of tags")

    created = zi.Attribute("When the bookmark was created")

    modified = zi.Attribute("When the bookmark was modified")

    zi.invariant(_url_is_mandatory)
    zi.invariant(_tags_is_sequence)
