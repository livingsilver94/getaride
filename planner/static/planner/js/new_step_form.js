function set_correct_origin(prev, last) {
    $(last).find("input[id*='origin_auto']").prop("disabled", true).val($(prev).find("input[id*='destination_auto']").val());
    $(last).find("input[type='number'][id*='origin']").val($(prev).find("input[type='number'][id*='destination']").val());
}

$(function () {
    $(".inline." + formset_prefix).formset({
        prefix: formset_prefix, // The form prefix for your django formset
        addCssClass: "btn btn-success btn-block step-add", // CSS class applied to the add link
        deleteCssClass: "btn btn-success btn-block step-delete", // CSS class applied to the delete link
        addText: 'Add another question', // Text for the add link
        deleteText: 'Remove question above', // Text for the delete link
        formCssClass: 'inline-form', // CSS class applied to each form in a formset
        added: function (row) {
            add_autocomplete(row);
            var forms = $(".inline." + formset_prefix);
            var prev_form = forms.get(forms.length - 2);
            set_correct_origin(prev_form, row);
        },
        removed: function (row) {
            var forms = $(".inline." + formset_prefix);
            forms.first().find("input").prop("disabled", false);
            if ($('#id_' + formset_prefix + '-TOTAL_FORMS').val() != 1) {
                set_correct_origin(forms.get(forms.length - 2), forms.get(forms.length - 1));
            }
        }
    })
});