
Hotgrid.handsontable_instance = null;
Hotgrid.table_column_no_by_name_idx = {}; // index to quickly lookup column index by property name
Hotgrid.table_columns_foreignkey_idx = {} // map of columns to lookup ( foreign keys )
Hotgrid.table_columns_lookup_idx = {} // map of columns to lookup ( fields with "choices" )
Hotgrid.table_headers = [];
Hotgrid.flag_is_readonly = true;
Hotgrid.list_of_unsaved_changes = [];
Hotgrid.list_of_unsaved_changes_idx = {}; // maps list_of_unsaved_changes by pk, for quick access

// Disable auto scroll up when pasting into a cell
// http://stackoverflow.com/questions/24593357/handsontable-disable-auto-scroll-up-when-pasting-into-a-cell
$(function() {
    var position_Y_before = null;
    /*
    $(".handsontable").handsontable({
        //some code here for initializing the table and its functions
        //Then I added this callback function
        beforeKeyDown: function(e) {
            position_Y_before = window.pageYOffset || 0;
        }
    });
    */
    //Here we prevent from scrolling to top of page after pasting to handsontable with cmd+v or ctrl+v
    $(window).scroll(function(){
        if(position_Y_before != null){
            window.scrollTo(0, position_Y_before);
            position_Y_before = null;
        }
    });
    // hide the boostrap header, because it interferes with the fixed handsontable columns header
    $(window).scroll(function(){
        var aTop = $(this).scrollTop();
        window.clearTimeout(window.headerHiderTimeout);
        window.headerHiderTimeout = window.setTimeout(function() {
            $('.navbar-fixed-top').css('display', (aTop>80)?'none':'block');
        }, 100);
      });
});

// django/jquery setup (csrf protection)
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

window.onbeforeunload = function(){
    if(Hotgrid.list_of_unsaved_changes.length) {
        return 'You have unsaved changes';
    }
};

function change_record_field(rowno, field, val, flag_remove) {
    // add the change to an existing (or new) record in "list_of_unsaved_changes"
    var rec_id = Hotgrid.table_data[rowno] && Hotgrid.table_data[rowno].pk || (Hotgrid.TEMP_ID_PREFIX+rowno);
    var rec = Hotgrid.list_of_unsaved_changes_idx[rec_id];

    if(!rec) { // CREATE
        rec = {'pk': rec_id};
        Hotgrid.list_of_unsaved_changes_idx[rec_id] = rec;
        Hotgrid.list_of_unsaved_changes.push(rec);
    }

    var def = Hotgrid.table_columns_lookup_idx[field] || Hotgrid.table_columns_lookup_idx[field.replace('.l','')];
    if(flag_remove) { // DELETE
        rec[Hotgrid.SPECIAL_PREFIX+'_flag_delete_record__'] = true;
    }else if(def){
        def.save_change(rec, val);
    }else{
        rec[field] = val;
    }
    rec[Hotgrid.SPECIAL_PREFIX+'rowno'] = rowno; // save the grid position, so errors sent from the server can be rendered.

    // UI feedback, coloring the changed rows and displaying messages to the user
    console.log('HOT-Grid record changed... rec =', rec_id, field,'=', val, rec);
    $('#change_counter').text(''+Hotgrid.list_of_unsaved_changes.length+' unsaved record(s)');
}

// post_process the freshly loaded data in Hotgrid.table_data
function load_save_postprocess() {
    // each foreign key result may contain items not already stored in the cache, so we have to check.
    $.each(Hotgrid.table_columns_foreignkey_idx, function (fname, coldef) {
        $.each(Hotgrid.table_data, function(rowno, item) {
            coldef.lookup_choices[item[coldef.fieldname]] = item[coldef.data];
            coldef.lookup_choices_text_idx[item[coldef.data]] = item[coldef.fieldname];
        });
    });
    Hotgrid.handsontable_instance.loadData(Hotgrid.table_data);
    // discard the already saved changes
    Hotgrid.list_of_unsaved_changes = [];
    Hotgrid.list_of_unsaved_changes_idx = {};
    // UI
    var msg = ''+Hotgrid.table_data.length+' row(s).';
    if(Hotgrid.table_data.length >= Hotgrid.MAX_ROWS)
        var msg = ''+Hotgrid.table_data.length+'+ row(s). You should filter/search the results to reduce the list.';
    $('#list_notification').text(msg);
}


// sends the changes (if any) to the server and load the new data
function load_save(discard_changes) {
    $('#list_notification').text('Loading...');
    console.log('HOT-Grid request... url=', Hotgrid.url_load_save, 'changes=', Hotgrid.list_of_unsaved_changes);
    if(discard_changes) {
        Hotgrid.list_of_unsaved_changes = [];
        Hotgrid.list_of_unsaved_changes_idx = {};
    }
    $.ajax({
        url: Hotgrid.url_load_save,
        dataType: 'json',
        type: 'POST',
        data: {
            changes: JSON.stringify(Hotgrid.list_of_unsaved_changes)
        },
        success: function(response) {
            console.log('HOT-Grid response... response=', response);
            if(response.errors&&response.errors.length) {
                var error_messages_text = []
                $.each(response.errors, function(idx, e) {
                    error_messages_text.push( (e.field?e.field+': ':'')+e.error );
                    console.error('server error:', e.field, e.error, e.item);
                });
                error_messages_text = error_messages_text.join('\n- ');
                editing_enable();
                Hotgrid.handsontable_instance.validateCells(function() { Hotgrid.handsontable_instance.render(); });
                // try to determine row and column to give visual feedback.
                $.each(response.errors, function(idx, e) {
                    var rowno = e.item?e.item._hOt_rowno:null;
                    var colno = Hotgrid.handsontable_instance.propToCol(e.field?e.field:'pk')
                    if(colno===e.field) {
                        console.log('no colno for error?', colno, e.field, e);
                        colno=0;
                    }
                    console.error('server error:', e.field, 'row=', rowno, 'col=', colno, e)
                    if(rowno!==null) {
                        Hotgrid.handsontable_instance.setCellMeta(rowno, colno||0, 'valid', false);
                        Hotgrid.handsontable_instance.setCellMeta(rowno, colno||0, 'className', 'forceInvalid');
                    }else{
                        console.log('no row information on server error #', idx, e)
                    }
                });
            }else if(response.table_data) {
                Hotgrid.table_data = response.table_data;
                load_save_postprocess();
            }else{
                alert( "There was an unexpected error (1), and the changes were not saved.\n\nThe administrations have been notified." );
            }
        },
        error: function() {
            alert( "There was an unexpected error, and the changes were not saved.\n\nThe administrations have been notified." );
            editing_enable();
        },
    });
}

function editing_enable() {
    $('#footer_buttons_while_browsing').css('display', 'none');
    $('#footer_buttons_while_editing').css('display', 'inline');
    Hotgrid.flag_is_readonly = false;
    $('#handsontable_main').handsontable('getInstance').updateSettings({readOnly: Hotgrid.flag_is_readonly, minSpareRows: 1 });
    $('#click_to_edit_message').hide();
    $('#change_counter').show();
    $('#list_notification').html('<b>Change the contents of the spreadsheet and press Save to store the changes</b>');
}
function editing_disable() {
    $('#footer_buttons_while_browsing').css('display', 'inline');
    $('#footer_buttons_while_editing').css('display', 'none');
    Hotgrid.flag_is_readonly = true;
    $('#handsontable_main').handsontable('getInstance').updateSettings({readOnly: Hotgrid.flag_is_readonly, minSpareRows: 0 });
    $('#change_counter').text('');
    $('#change_counter').hide();
    $('#click_to_edit_message').show();
}
function editing_freeze() {
    $('#footer_buttons_while_browsing').css('display', 'inline');
    $('#footer_buttons_while_editing').css('display', 'none');
    Hotgrid.flag_is_readonly = true;
    $('#handsontable_main').handsontable('getInstance').updateSettings({readOnly: Hotgrid.flag_is_readonly, minSpareRows: 0 });
    $('#change_counter').hide();
}

// show a link when in read-only mode, and just a plain text when editing
var detaillink_Renderer = function (instance, td, rowno, colno, prop, value, cellProperties) {
    if(Hotgrid.flag_is_readonly) {
        var url = cellProperties.link_to.replace('%28val%29', value);
        //td.innerHTML = '<a href="'+url+'" class="btn btn-primary btn-xs" style="width: 100%;" title="Detail view">'+Handsontable.helper.stringify(value)+'</a>';
        var buf = ['<div class="btn-group" style="width:100px;"><a href="'+url+'" class="btn btn-primary btn-xs" title="Detail view">details</a>'];
        var cp = cellProperties.extra_links;
        if(cp.length) {
            buf.push('<button type="button" class="btn btn-primary btn-xs dropdown-toggle" data-toggle="dropdown"><span class="caret"></span><span class="sr-only">Toggle Dropdown</span></button>'+
                '<ul class="dropdown-menu" role="menu">');
            $.each(cp, function(i,e) {
                var url = e[1].replace('%(val)s', value);
                buf.push('<li><a href="'+url+'">'+e[0]+'</a></li>');
            });
            buf.push('</ul>');
        }
        buf.push('</div>');
        td.innerHTML = buf.join('');
        /* the little arrow does not play well with text-overflow */
        $(td).css('overflow', 'visible');
        return td;
    }else{
        /*
        //change_record_field(rowno, 'uid', null, true);
        var url = cellProperties.link_to.replace('%28val%29', value);
        td.innerHTML = '<a id="btn_delrow_'+rowno+'"  href="'+url+'" class="btn btn-danger btn-xs" style="width: 100%;" title="Delete row">'+Handsontable.helper.stringify(value)+'</a>';
        $(td).closest('tr').css('background-color', 'red');
        return td;
        */
        Handsontable.renderers.TextRenderer.apply(this, arguments);
    }
};
// show a link when in read-only mode, and just a plain text when editing
var link_to_Renderer = function (instance, td, rowno, colno, prop, value, cellProperties) {
    if(Hotgrid.flag_is_readonly) {
        var val = Hotgrid.table_data[rowno][cellProperties.fieldname]
        var url = cellProperties.link_to.replace('%28val%29', val);
        td.innerHTML = '<a href="'+url+'" class="btn btn-xs" style="width: 100%;" title="Detail view">'+Handsontable.helper.stringify(value)+'</a>';
        return td;
    }else{
        Handsontable.renderers.TextRenderer.apply(this, arguments);
    }
};

$(function() {
    // Enable/disable editing
    $('#edit_sheet').on('click', function () {
        editing_enable();
    });
    $('#cancel_sheet').on('click', function () {
        if( Hotgrid.list_of_unsaved_changes.length<=0 || confirm('You have unsaved changes, are you sure you want to dicard them?')) {
            editing_disable();
            load_save(true);
        }
    });
    $('#save_sheet').on('click', function () {
        if(Hotgrid.list_of_unsaved_changes.length) {
            $('#save_notification').text('Saving...');
        }else{
            $('#save_notification').text('No changes made.');
        }
        window.setTimeout(function() {
            $('#save_notification').text('');
        }, 1000);
        editing_freeze();
        load_save();
    });
    $('#handsontable_main td').dblclick(function() {
        editing_enable();
    });


    // process each column, adding callbacks and validators
    $.each(Hotgrid.table_columns, function(idx, def) {
        if (def.type == 'numeric' && !def.required) {
            def.validator = function (value, callback) {
                if (value===null||value==undefined) {
                    callback(true);
                } else {
                    callback(/^-?\d*(\.|\,)?\d*$/.test(value));
                }
            };
        }
        // foreignkey field special setup.
        if (def.type == 'foreignkey') {
            def.data += '.l';
            def.strict = true;
            def.allowInvalid = false;
            def.lookup_choices = {};
            def.lookup_choices_text_idx = {};
            if(def.nullable||!def.required) {
                def.lookup_choices[null] = '';
                def.lookup_choices_text_idx[''] = null;
                def.validator = function (value, callback) {
                    callback(true);
                };
            }
            def.source = function (query, process) {
                if(!query && (def.nullable||!def.required)) {
                    console.log('processing', def.data, query)
                    process(['']);
                    return;
                }
                $.ajax({
                    url: def.lookup_remote_url,
                    dataType: 'json',
                    data: {query: query},
                    success: function (response) {
                        var temp = [];
                        $.each(response.items, function (dummy, o) {
                            if(o.text==undefined || o.pk==undefined)
                                console.error('an autocomplete item had no text/pk', o, response)
                            temp.push(o.text);
                            def.lookup_choices[o.pk] = o.text;
                            def.lookup_choices_text_idx[o.text] = o.pk;
                        });
                        process(temp);
                    }
                });
            };
            def.save_change = function(rec, v) {
                rec[def.data] = v;
                rec[def.fieldname] = def.lookup_choices_text_idx[v];
            };
            Hotgrid.table_columns_foreignkey_idx[def.data] = def;
            Hotgrid.table_columns_lookup_idx[def.data] = def;
        }else if (def.lookup_choices) {
            def.data += '.l';
            def.subtype = def.type;
            def.type = 'lookup';
            def.strict = true;
            def.allowInvalid = false;
            def.source = [];
            def.lookup_choices_text_idx = {};
            if (def.nullable||!def.required) {
                def.lookup_choices[''] = '';
                def.lookup_choices_text_idx[''] = '';
                def.validator = function (value, callback) {
                    callback(true);
                };
            }
            $.each(def.lookup_choices, function (key, text) {
                def.source.push(text);
                def.lookup_choices_text_idx[text] = key;
            });
            def.save_change = function(rec, v) {
                rec[def.data] = v;
                rec[def.data.replace('.l','')] = def.lookup_choices_text_idx[v];
            };
            Hotgrid.table_columns_lookup_idx[def.data] = def;
        }
        if (def.renderer == 'detaillink_Renderer') {
            def.renderer = detaillink_Renderer;
//        }else if (def.link_to) {
//            def.renderer = link_to_Renderer;
        }
        Hotgrid.table_column_no_by_name_idx[def.data] = idx;
        Hotgrid.table_headers.push(def.label||def.data);
    });

    $('#handsontable_main').handsontable({
        colHeaders : Hotgrid.table_headers,
        columns : Hotgrid.table_columns,
        data : Hotgrid.table_data,
        readOnly: true,
        minSpareRows: 0,
        stretchH: 'none',
        fillHandle : false,
        currentRowClassName: 'currentRow',
        manualColumnResize: true,
        manualColumnMove: true,
        columnSorting: true,
//        persistentState: true,
        dataSchema: {}, // NOTE: this is to avoid weird issues after updating: adding extra rows for no good reason.
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcontextMenu: {
            items: {
                "remove_row": {
                    name: 'Remove this row',
                    disabled: function () {
                        return Hotgrid.flag_is_readonly;
                    }
                },
            }
        },
        afterChange: function(changes, source) {
            if(!changes) return;
            $.each(changes, function(i, change) {
                var rowno=change[0], field=change[1], oldVal=change[2], newVal=change[3];
                // if the cell changed AND it's not just as empty as it was before
                if(oldVal!==newVal) {
                    if( oldVal===undefined && newVal==='' )
                        return;
                    change_record_field(rowno, field, newVal);
                }
            });
        },
        beforeRemoveRow: function(index, amount) {
            var index_amount = index + amount;
            for(var rowno=index ; rowno < index_amount; rowno++ ) {
                change_record_field(rowno, 'pk', null, true);
            }
        },
    });
    Hotgrid.handsontable_instance = $('#handsontable_main').handsontable('getInstance');

    load_save_postprocess();

    // DEBUGGING ONLY
    window.setTimeout(function() {
        editing_enable();
        //Hotgrid.handsontable_instance.setDataAtRowProp(0, 'order_no', 'xx')
        //Hotgrid.handsontable_instance.setDataAtRowProp(1, 'restaurant', 'xx')
        //window.setTimeout(function() {
        //    $('#save_sheet').trigger('click');
        //}, 100);
    }, 500);
});
