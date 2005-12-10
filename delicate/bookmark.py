import datetime

class Bookmark(object):
    url = None
    title = None
    description = None
    tags = None
    created = None
    modified = None

    def __init__(self, **kwargs):
        # set defaults for optional fields
        kwargs.setdefault('title', None)
        kwargs.setdefault('description', None)
        kwargs.setdefault('tags', [])
        now = datetime.datetime.now()
        kwargs.setdefault('created', now)
        kwargs.setdefault('modified', now)

        for field in ['url',
                      'title',
                      'description',
                      'tags',
                      'created',
                      'modified']:
            try:
                value = kwargs.pop(field)
            except KeyError:
                raise TypeError, '%s() missing keyword argument %r' % (
                    self.__class__.__name__,
                    field,
                    )
            setattr(self, field, value)

        super(Bookmark, self).__init__(**kwargs)

    def __repr__(self):
        args = [
            'url=%r' % self.url,
            'title=%r' % self.title,
            'description=%r' % self.description,
            'tags=%r' % (self.tags,),
            'created=%r' % self.created,
            'modified=%r' % self.modified,
            ]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(args))

    def __eq__(self, other):
        # TODO use interfaces and adaptation
        if not isinstance(other, Bookmark):
            return NotImplemented
        return (self.url == other.url
                and self.title == other.title
                and self.description == other.description
                and self.tags == other.tags
                and self.created == other.created
                and self.modified == other.modified)

    def __ne__(self, other):
        # TODO use interfaces and adaptation
        if not isinstance(other, Bookmark):
            return NotImplemented
        return not (self == other)
