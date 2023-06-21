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
    item.value = label; // TODO: use a better value
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
  console.log(settings);
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
      var field_type = this.id.replace("field-", "");

      // Get the corresponding data for the field_type from the settings object
      var field_data = settings.multi_fields[field_type.toLowerCase()];

      // Filter the data based on the user's input (term)
      var filtered_data = $.grep(field_data, function (item) {
        return item.toLowerCase().indexOf(term.toLowerCase()) === 0;
      });

      // Transform the filtered data to be used with the autocomplete widget
      var transformedData = $.map(filtered_data, function (item) {
        return {
          label: item,
          value: item,
        };
      });

      // Return the transformed data as the response
      response(transformedData);
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
    console.log(target);

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

  $(document).ready(function () {
    var multi_fields = ["keywords", "customer", "supplier", "sizes"];
    activate({ selector: ticket_fields(multi_fields), multiple: true });
  });
});
