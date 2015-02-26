$(function() {
/*
    // select2 remote lookup (generic)... all this should be defined as ModelAdmin.raw_id_fields
    $('input#id_created_by, input#id_last_updated_by, input#id_test_foreign_key, input#id_test_foreign_key_null').each(function(idx, elt) {
        $(elt).select2({width: '300', containerCss : {"display":"inline-block"},
            ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
                url: "/admin/generic_userprofile_autocomplete/",
                dataType: 'json',
                data: function (term, page) {
                    return {
                        query: term,
                        page_limit: 10,
                    };
                },
                results: function (data, page) {
                    return {results: data.items};
                }
            },
        });
    });
*/
    // convert comboboxes to select2 elements, no remote lookup.
    $('select#id_todolist').each(function(idx, elt) {
        $(elt).select2({width: '300', containerCss : {"display":"inline-block"}});
    });
});
