$(function () {
    $(".inline." + formset_prefix).formset({
        prefix: formset_prefix, // The form prefix for your django formset
        addCssClass: "btn btn-block btn-primary bordered inline-form-add", // CSS class applied to the add link
        deleteCssClass: "btn btn-block btn-primary bordered", // CSS class applied to the delete link
        addText: 'Add another question', // Text for the add link
        deleteText: 'Remove question above', // Text for the delete link
        formCssClass: 'inline-form', // CSS class applied to each form in a formset
        added: function (row) {
            add_autocomplete(row);
        }
    })
});