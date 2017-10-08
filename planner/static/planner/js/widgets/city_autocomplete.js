var autocomplete_options = {
    source: '/city-autocomplete',
    dataType: 'json',
    minLength: 1,
    select: function (event, ui) {
        // Cut "_auto" from ID
        document.getElementById(event.target.id.slice(0, -5)).value = ui.item.id;

    },
};

function add_autocomplete(obj) {
    obj.find("input.city-autocomplete").autocomplete(autocomplete_options);
}

$(document).ready(function () {
    $("input.city-autocomplete").autocomplete(autocomplete_options);
});