// import Nevow.Athena
// import Divmod
// import Delicate.Visual

if (typeof Delicate == 'undefined') {
  Delicate = {};
}

if (typeof Delicate.BookmarkList == 'undefined') {
  Delicate.BookmarkList = {};
}

Delicate.BookmarkList._showImage = function(img){
  return (function(){ img.style.display='inline'; });
}

Delicate.BookmarkList.domifyBookmark = function(bookmark) {
  start = new Date();
  var scheme = bookmark.url.split(':')[0];
  if (scheme == 'http'
      || scheme == 'https') {
    favicon = IMG({'alt': '',
		     'style': 'width: 16px; height: 16px; border: none; float: left; margin-left: -20px;',
		     'src': bookmark.url.split('/').splice(0,3).join('/')+'/favicon.ico',
		     'class': 'delicate-invisible'});
    updateNodeAttributes(favicon, {'onload': Delicate.BookmarkList._showImage(favicon)});
  } else {
    favicon = '';
  }

  dom = DIV({'class': 'delicate-bookmark',
	       'id': 'delicate-bookmarkList-url-'+bookmark.id},
	    A({'href': bookmark.url},
	      favicon,
	      bookmark.title));
  if (bookmark.description) {
    appendChildNodes(dom, P(null, bookmark.description));
  }
  meta = DIV({'class': 'delicate-metadata'});
  appendChildNodes(dom, meta);
  if (bookmark.tags) {
    appendChildNodes(meta, 'to ' + bookmark.tags.join(' '));
  }

  var created = isoTimestamp(bookmark.created);
  appendChildNodes(meta, ' on ', toISODate(created));
  if (bookmark.modified != null) {
    var modified = isoTimestamp(bookmark.modified);
    if (compare(bookmark.modified, bookmark.created)) {
      appendChildNodes(meta, ', updated ', toISODate(modified));
    }
  }
  return dom;
}

Delicate.BookmarkList.isBookmarkLike = function (/* ... */) {
  for (var i = 0; i < arguments.length; i++) {
    var o = arguments[i];
    if (typeof(o) != "object" || typeof(o.url) != 'string') {
      return false;
    }
  }
  return true;
}

registerDOMConverter('bookmarkLike',
		     Delicate.BookmarkList.isBookmarkLike,
		     Delicate.BookmarkList.domifyBookmark);

Delicate.BookmarkList.BookmarkList = Nevow.Athena.Widget.subclass();

Delicate.BookmarkList.BookmarkList.prototype.__init__ = function(widgetNode) {
  this.currentTags = [];
  Delicate.BookmarkList.BookmarkList.upcall(this, "__init__", widgetNode);
};

Delicate.BookmarkList.BookmarkList.prototype.addBookmark = function(bookmark) {
  exist = getElement('delicate-bookmarkList-url-'+bookmark.id);
  //TODO registerDOMConverter does not seem to work, do it explicitly
  bookmark = Delicate.BookmarkList.domifyBookmark(bookmark);
  if (exist == null) {
    node = getElement('delicate-bookmarkList-bookmarks');
    appendChildNodes(node, bookmark);
  } else {
    swapDOM(exist, bookmark);
  }
}

Delicate.BookmarkList.BookmarkList.prototype._haveBookmarks = function(bookmarks) {
  node = getElement('delicate-bookmarkList-bookmarks');
  children = getElementsByTagAndClassName(null, 'delicate-bookmark', node);
  for (i in children) {
    child = children[i];
    addElementClass(child, 'delicate-bookmarkList-bookmark-old');
  }

  for (i in bookmarks) {
    b = bookmarks[i];
    this.addBookmark(b);
  }

  children = getElementsByTagAndClassName(null, 'delicate-bookmarkList-bookmark-old', node);
  for (i in children) {
    child = children[i];
    swapDOM(child, null);
  }

  node = getElement('delicate-bookmarkList-loading');
  Delicate.Visual.makeInvisible(node);
}

Delicate.BookmarkList.BookmarkList.prototype.fetchBookmarks = function() {
  var self = this;
  node = getElement('delicate-bookmarkList-loading');
  Delicate.Visual.makeVisible(node);

  var d = this.callRemoteKw('getBookmarks',
    {'tags': self.currentTags,
     'count':  100});
  d.addCallback(function (result) { return self._haveBookmarks(result); });
  d.addErrback(function (fail) {Divmod.log('FAIL', fail)});
}

Delicate.BookmarkList.BookmarkList.prototype.notifyTagSelect = function(tag) {
  var self = this;
  self.currentTags.push(tag);
  self.fetchBookmarks();
}

Delicate.BookmarkList.BookmarkList.prototype.notifyTagUnselect = function(tag) {
  var self = this;
  for (var i = 0; i < this.currentTags.length; i++) {
    if (this.currentTags[i] == tag) {
      this.currentTags.splice(i, 1);
      break;
    }
  }
  self.fetchBookmarks();
}

Delicate.BookmarkList.BookmarkList.prototype.loaded = function() {
  var self = this;
  var children = DIV(null,
		 UL({'id': 'delicate-bookmarkList-bookmarks'}),
		 SPAN({'id': 'delicate-bookmarkList-loading',
			 'class': 'delicate-invisible'},
		      'Loading...'));

  replaceChildNodes(this.node, children);

  var node = getElement('delicate-tagchooser');
  var tagchooser = Delicate.BookmarkList.BookmarkList.get(node);
  addToCallStack(tagchooser.tagChooserNotifiers, 'onTagSelect',
		 bind(this.notifyTagSelect, this));
  addToCallStack(tagchooser.tagChooserNotifiers, 'onTagUnselect',
		 bind(this.notifyTagUnselect, this));
}
