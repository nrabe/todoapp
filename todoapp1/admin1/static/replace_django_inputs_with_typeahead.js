$(function() {
    
    // find the named elements here, and replace them with an advanced select
    $('select#id_created_by, select#id_last_updated_by, select#id_todolist').each(function(idx, elt) {
        $(elt).select2({width: '300', containerCss : {"display":"inline-block"}});
    });
});
