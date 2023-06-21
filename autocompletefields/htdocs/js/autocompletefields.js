(function ($) {
  var methods = {};
  methods._create = function () {
    $.ui.autocomplete.prototype._create.apply(this, arguments);
    this.widget().addClass("tracautocompletefields");
  };
  var itemData = function (item) {
    item = { field_type: item[0] };
    var label = item.field_type;
    item.label = label;
    item.value = item.field_type;
    return item;
  };
  var renderItem = function (ul, item) {
    var li = $(document.createElement("li"));
    var anchor = $(document.createElement("a"));
    anchor.text(item.label);
    li.append(anchor);
    ul.append(li);
    return li;
  };
  if ("_renderItemData" in $.ui.autocomplete.prototype) {
    methods._renderItemData = function (ul, item) {
      item = itemData(item);
      var li = renderItem(ul, item);
      li.data("ui-autocomplete-item", item);
      return li;
    };
  } else {
    methods._renderItem = function (ul, item) {
      item = itemData(item);
      var li = renderItem(ul, item);
      li.data("item.autocomplete", item);
      return li;
    };
  }
  $.widget(
    "tracautocompletefields.tracautocompletefields",
    $.ui.autocomplete,
    methods
  );
})(jQuery);

jQuery(function ($) {
  var settings = window.autocompletefields;
  if (settings === undefined) return;

  var ticket_fields = function (fields) {
    fields = $.map(fields, function (val) {
      return "input#field-" + val;
    });
    return fields.join(", ");
  };
  var multi_source = function (url) {
    return function (request, response) {
      var terms = request.term.split(/,\s*/);
      var term = terms.length === 0 ? "" : terms[terms.length - 1];
      $.getJSON(url, { term: term }, response);
    };
  };
  var single_select = function (event, ui) {
    this.value = ui.item.value;
    return false;
  };
  var multi_select = function (event, ui) {
    var terms = this.value.split(/,\s*/);
    terms.pop();
    terms.push(ui.item.value);
    terms.push("");
    this.value = terms.join(", ");
    return false;
  };
  var activate = function (target) {
    if (!target.selector) return;
    var options = { minLength: 0, autoFocus: true };
    var args = [];
    var url = settings.url;
    if (target.multiple) {
      options.source = multi_source(url);
      options.select = multi_select;
    } else {
      options.source = url;
      options.select = single_select;
    }
    options.focus = function () {
      return false;
    };
    $(target.selector).tracautocompletefields(options);
  };

  var single_fields = ["Keywords", "Supplier", "Customer", "Sizes"];
  activate({ selector: ticket_fields(single_fields), multiple: false });
});
