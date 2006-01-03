import zope.interface as zi

class IBookmarkShelf(zi.Interface):
    """
    Storage for many bookmarks.

    There is no guaranteed order for the bookmarks, consider this
    to be like a dict mapping URLs to IBookmarks.
    """

    def add(bookmark):
        """Add a bookmark to the shelf."""

    def remove(url):
        """
        Remove bookmark identified by url from the shelf.

        @todo: Removes are final and not undoable. The plan is to
        build an undelete-capable layer on top of this by making
        delete tag bookmarks with system:deleted, and periodically
        purge all bookmarks tagged with system:deleted that have
        last modification time sufficiently far in the past.
        """

    def get(url):
        """Get a bookmark matching the url, or None."""

    def getBookmarks(tags=None, count=None):
        """
        Return an iterable that will give all the bookmarks stored.

        If tags is given, only bookmarks with all those tags are
        returned.

        If count is given, at most that many bookmarks are returned.
        """

    def getTags():
        """
        Return a Deferred iterable containing all the tags used in
        this bookshelf.

        Set refresh to True if cached results are unacceptable. This
        may be extremely slow.
        """
