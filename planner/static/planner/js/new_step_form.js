function set_correct_origin(prev, last) {
    var new_orig = $(last).find("select[id*='origin']");
    var old_dest = $(prev).find("select[id*='destination']");
    new_orig.prop("disabled", true);
    new_orig.append($('<option>', {
        value: old_dest.val(),
        text: $("#" + old_dest.attr("id") + " option:selected").html(),
        selected: true
    }));

}

$(function () {
    $(".inline." + formset_prefix).formset({
        prefix: formset_prefix, // The form prefix for your django formset
        addCssClass: "btn btn-block btn-primary bordered inline-form-add", // CSS class applied to the add link
        deleteCssClass: "btn btn-block btn-primary bordered", // CSS class applied to the delete link
        addText: 'Add another question', // Text for the add link
        deleteText: 'Remove question above', // Text for the delete link
        formCssClass: 'inline-form', // CSS class applied to each form in a formset
        added: function (row) {
            var forms = $(".inline." + formset_prefix);
            var prev_form = forms.get(forms.length - 2);
            set_correct_origin(prev_form, row);
        },
        removed: function (row) {
            var forms = $(".inline." + formset_prefix);
            forms.first().find("select").prop("disabled", false);
            if ($('#id_' + formset_prefix + '-TOTAL_FORMS').val() != 1) {
                set_correct_origin(forms.get(forms.length - 2), forms.get(forms.length - 1));
            }
        }
    })
});