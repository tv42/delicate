if (typeof Delicate == 'undefined') {
  var Delicate = {};
};

if (typeof Delicate.Visual == 'undefined') {
  Delicate.Visual = {};
};

Delicate.Visual.makeVisible = function(elem) {
  removeElementClass(elem, "delicate-invisible");
};

Delicate.Visual.makeInvisible = function(elem) {
  addElementClass(elem, "delicate-invisible");
};
