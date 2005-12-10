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
