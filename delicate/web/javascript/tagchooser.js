// import Nevow.Athena
// import Divmod
// import Delicate.Visual

if (typeof Delicate == 'undefined') {
  var Delicate = {};
};

if (typeof Delicate.TagChooser == 'undefined') {
  Delicate.TagChooser = {};
};

Delicate.TagChooser.TagChooser = Nevow.Athena.Widget.subclass();

Delicate.TagChooser.TagChooser.prototype.__init__ = function(widgetNode) {
  this.currentTags = {};
  this.tagChooserNotifiers = {};
  Delicate.TagChooser.TagChooser.upcall(this, "__init__", widgetNode);
};

Delicate.TagChooser.TagChooser.prototype.selectTag = function(node, tag) {
  this.currentTags[tag] = true;
  addElementClass(node, 'delicate-tagchooser-chosen');
  var callable = this.tagChooserNotifiers.onTagSelect;
  if (callable != undefined) {
    try {
      callable(tag);
    } catch(e) {
      Divmod.log('FAIL', 'onTagSelect notifiers failed: '+repr(e));
    }
  }
};

Delicate.TagChooser.TagChooser.prototype.unselectTag = function(node, tag) {
  this.currentTags[tag] = false;
  removeElementClass(node, 'delicate-tagchooser-chosen');
  var callable = this.tagChooserNotifiers.onTagUnselect;
  if (callable != undefined) {
    try {
      callable(tag);
    } catch(e) {
      Divmod.log('FAIL', 'onTagUnselect notifiers failed: '+repr(e));
    }
  }
};

Delicate.TagChooser.TagChooser.prototype.toggleTag = function(event) {
  var self = this;
  tag = scrapeText(event.target);
  if (this.currentTags[tag]) {
    self.unselectTag(event.target, tag);
  } else {
    self.selectTag(event.target, tag);
  }
};

Delicate.TagChooser.TagChooser.prototype.addTags = function(tags) {
  var self = this;
  tags.sort();
  for (i in tags) {
    tag = tags[i];

    if (!(tag in this.currentTags)) {
      this.currentTags[tag] = false;
    }

    node = getElement('delicate-tagchooser-tag-'+tag);
    if (!node) {
      c = LI(null,
	     A({ 'href': '#',
		   'onclick': function(event) { self.toggleTag(event); return false; } },
	       tag),
	     ' '
	     );
      parent = getElement('delicate-tagchooser-taglist');
      appendChildNodes(parent, c);
    }
  }
};

Delicate.TagChooser.TagChooser.prototype._loadedTags = function() {
  node = getElement('delicate-tagchooser-loading');
  Delicate.Visual.makeInvisible(node);
};

Delicate.TagChooser.TagChooser.prototype.getTags = function() {
  var self = this;
  Delicate.Visual.makeVisible(getElement('delicate-tagchooser-loading'));
  var d = this.callRemote('getTags');
  d.addCallback(function (result) { return self.addTags(result); });
  d.addCallback(function (result) { return self._loadedTags(result); });
  d.addErrback(function (fail) {Divmod.log('FAIL', fail)});
};

Delicate.TagChooser.TagChooser.prototype.addUL = function() {
  var children = DIV(null,
		     UL({'id': 'delicate-tagchooser-taglist'}),
		     SPAN({'id': 'delicate-tagchooser-loading'},
			  'Loading...'));

  replaceChildNodes(this.node, children);
};

Delicate.TagChooser.TagChooser.prototype.loaded = function() {
  this.addUL()
  this.getTags()
};
