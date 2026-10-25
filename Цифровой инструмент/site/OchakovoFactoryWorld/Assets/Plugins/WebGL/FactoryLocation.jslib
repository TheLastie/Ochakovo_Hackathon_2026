mergeInto(LibraryManager.library, {
 FactoryLocationState: function (pointer) {
  var detail = JSON.parse(UTF8ToString(pointer));
  window.factoryLocation = detail;
  window.dispatchEvent(new CustomEvent('factory-location-state', {detail: detail}));
 }
});
