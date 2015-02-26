/**
 * cell type: checkbox, without "## Bad Value ##"
 * cell types: datetime, date, time
 */

(function(Handsontable) {

    var clonableINPUT = document.createElement('INPUT');
    clonableINPUT.className = 'htCheckboxRendererInput';
    clonableINPUT.type = 'checkbox';
    clonableINPUT.setAttribute('autocomplete', 'off');

    var CheckboxRenderer = function(instance, TD, row, col, prop, value, cellProperties) {

        if (typeof cellProperties.checkedTemplate === "undefined") {
            cellProperties.checkedTemplate = true;
        }
        if (typeof cellProperties.uncheckedTemplate === "undefined") {
            cellProperties.uncheckedTemplate = false;
        }

        Handsontable.Dom.empty(TD); // TODO identify under what circumstances
        // this line can be removed

        var INPUT = clonableINPUT.cloneNode(false); // this is faster than
        // createElement
        if (value === cellProperties.checkedTemplate
                || value === Handsontable.helper.stringify(cellProperties.checkedTemplate)) {
            INPUT.checked = true;
            TD.appendChild(INPUT);
        } else if (value === cellProperties.uncheckedTemplate
                || value === Handsontable.helper.stringify(cellProperties.uncheckedTemplate)) {
            TD.appendChild(INPUT);
        } else {
            INPUT.className += ' noValue';
            TD.appendChild(INPUT);
        }

        var $input = $(INPUT);

        if (cellProperties.readOnly) {
            $input.on('click', function(event) {
                event.preventDefault();
            });
        } else {
            $input.on('mousedown', function(event) {
                event.stopPropagation(); // otherwise can confuse cell
                // mousedown handler
            });

            $input.on('mouseup', function(event) {
                event.stopPropagation(); // otherwise can confuse cell
                // dblclick handler
            });

            $input.on('change', function() {
                if (this.checked) {
                    instance.setDataAtRowProp(row, prop, cellProperties.checkedTemplate);
                } else {
                    instance.setDataAtRowProp(row, prop, cellProperties.uncheckedTemplate);
                }
            });
        }

        if (!instance.CheckboxRenderer || !instance.CheckboxRenderer.beforeKeyDownHookBound) {
            instance.CheckboxRenderer = {
                beforeKeyDownHookBound : true
            };

            instance.addHook('beforeKeyDown', function(event) {
                if (event.keyCode == Handsontable.helper.keyCode.SPACE) {

                    var cell, checkbox, cellProperties;

                    var selRange = instance.getSelectedRange();
                    var topLeft = selRange.getTopLeftCorner();
                    var bottomRight = selRange.getBottomRightCorner();

                    for (var row = topLeft.row; row <= bottomRight.row; row++) {
                        for (var col = topLeft.col; col <= bottomRight.col; col++) {
                            cell = instance.getCell(row, col);
                            cellProperties = instance.getCellMeta(row, col);

                            checkbox = cell.querySelectorAll('input[type=checkbox]');

                            if (checkbox.length > 0 && !cellProperties.readOnly) {

                                if (!event.isImmediatePropagationStopped()) {
                                    event.stopImmediatePropagation();
                                    event.preventDefault();
                                }

                                for (var i = 0, len = checkbox.length; i < len; i++) {
                                    checkbox[i].checked = !checkbox[i].checked;
                                    $(checkbox[i]).trigger('change');
                                }

                            }

                        }
                    }
                }
            });
        }
    };
    // Blank editor, because all the work is done by renderer
    var CheckboxEditor = Handsontable.editors.BaseEditor.prototype.extend();

    CheckboxEditor.prototype.beginEditing = function() {
        var checkbox = this.TD.querySelector('input[type="checkbox"]');

        if (checkbox) {
            $(checkbox).trigger('click');
        }

    };

    CheckboxEditor.prototype.finishEditing = function() {
    };

    CheckboxEditor.prototype.init = function() {
    };
    CheckboxEditor.prototype.open = function() {
    };
    CheckboxEditor.prototype.close = function() {
    };
    CheckboxEditor.prototype.getValue = function() {
    };
    CheckboxEditor.prototype.setValue = function() {
    };
    CheckboxEditor.prototype.focus = function() {
    };

    Handsontable.CheckboxCell = {
        editor : CheckboxEditor,
        renderer : CheckboxRenderer,
    };
    Handsontable.CheckboxRenderer = CheckboxRenderer;
    Handsontable.renderers.CheckboxRenderer = CheckboxRenderer;
    Handsontable.cellTypes['checkbox'] = Handsontable.CheckboxCell;
    Handsontable.renderers.registerRenderer('checkbox', DateTimeRenderer);

    // How to use moment.js with jquery datetimepicker
    Date.parseDate = function(input, format) {
        return moment(input, format).toDate();
    };
    Date.prototype.dateFormat = function(format) {
        return moment(this).format(format);
    };

    var DateTimeEditor = Handsontable.editors.TextEditor.prototype.extend();

    DateTimeEditor.prototype.init = function() {
        Handsontable.editors.TextEditor.prototype.init.apply(this, arguments);
        this.isCellEdited = false;
        var that = this;
        this.instance.addHook('afterDestroy', function() {
            that.destroyElements();
        })
    };

    DateTimeEditor.prototype.createElements = function() {
        Handsontable.editors.TextEditor.prototype.createElements.apply(this, arguments);

        this.dateTimePicker = document.createElement('DIV');
        Handsontable.Dom.addClass(this.dateTimePicker, 'htDatepickerHolder');
        this.dateTimePickerStyle = this.dateTimePicker.style;
        this.dateTimePickerStyle.position = 'absolute';
        this.dateTimePickerStyle.top = 0;
        this.dateTimePickerStyle.left = 0;
        this.dateTimePickerStyle.zIndex = 99;
        document.body.appendChild(this.dateTimePicker);
        this.$dateTimePicker = $(this.dateTimePicker);

        var that = this;
        var defaultOptions = {
            dateFormat: $.datepicker.ISO_8601,
            separator: 'T',
            timeFormat: 'hh:mm:ssZ',
            ampm: false,
            showButtonPanel : true,
            changeMonth : true,
            changeYear : true,
            onSelect : function(dateStr) {
                that.setValue(dateStr);
                that.finishEditing(false);
            }
        };
        this.$dateTimePicker.datetimepicker(defaultOptions);
        // Prevent recognizing clicking on jQuery Datepicker as clicking outside
        // of table
        this.$dateTimePicker.on('mousedown', function(event) {
            event.stopPropagation();
        });

        this.hideDatepicker();
    };

    DateTimeEditor.prototype.destroyElements = function() {
        this.$dateTimePicker.datetimepicker('destroy');
        this.$dateTimePicker.remove();
    };

    DateTimeEditor.prototype.open = function() {
        Handsontable.editors.TextEditor.prototype.open.call(this);
        this.showDatepicker();
    };

    DateTimeEditor.prototype.finishEditing = function(isCancelled) {
        this.hideDatepicker();
        Handsontable.editors.TextEditor.prototype.finishEditing.apply(this, arguments);
    };

    DateTimeEditor.prototype.showDatepicker = function() {
        var $td = $(this.TD);
        var offset = $td.offset();
        this.dateTimePickerStyle.top = (offset.top + $td.height()) + 'px';
        this.dateTimePickerStyle.left = offset.left + 'px';

        var dateOptions = {
            defaultDate : this.originalValue || void 0
        };
        $.extend(dateOptions, this.cellProperties);
        this.$dateTimePicker.datetimepicker("option", dateOptions);
        if (this.originalValue) {
            this.$dateTimePicker.datetimepicker("setDate", this.originalValue);
        }
        this.$dateTimePicker.datetimepicker("show");
//        this.dateTimePickerStyle.display = 'block';
    };

    DateTimeEditor.prototype.hideDatepicker = function() {
        this.dateTimePickerStyle.display = 'none';
    };

    Handsontable.editors.DateTimeEditor = DateTimeEditor;
    Handsontable.editors.registerEditor('time', DateTimeEditor);
    Handsontable.editors.registerEditor('date', DateTimeEditor);
    Handsontable.editors.registerEditor('datetime', DateTimeEditor);

    var DateRenderer = function(instance, TD, row, col, prop, value, cellProperties) {
        value = value ? moment.utc(value).format('ddd DD MMM, YYYY') : '';
        Handsontable.renderers.AutocompleteRenderer(instance, TD, row, col, prop, value, cellProperties);
    };
    var TimeRenderer = function(instance, TD, row, col, prop, value, cellProperties) {
        value = value ? moment.utc(value).format('h:m a') : '';
        Handsontable.renderers.AutocompleteRenderer(instance, TD, row, col, prop, value, cellProperties);
    };
    var DateTimeRenderer = function(instance, TD, row, col, prop, value, cellProperties) {
        value = value ? moment.utc(value).format('ddd DD MMM, YYYY h:m a') : '';
        Handsontable.renderers.AutocompleteRenderer(instance, TD, row, col, prop, value, cellProperties);
    };

    Handsontable.DateCell = {
        editor : DateTimeEditor,
        renderer : DateRenderer,
        validator : Handsontable.AutocompleteValidator
    };
    Handsontable.DateRenderer = DateRenderer;
    Handsontable.renderers.DateRenderer = DateRenderer;
    Handsontable.cellTypes['date'] = Handsontable.DateCell;
    Handsontable.renderers.registerRenderer('date', DateTimeRenderer);

    Handsontable.TimeCell = {
        editor : DateTimeEditor,
        renderer : TimeRenderer,
        validator : Handsontable.AutocompleteValidator
    };
    Handsontable.TimeRenderer = TimeRenderer;
    Handsontable.renderers.TimeRenderer = TimeRenderer;
    Handsontable.cellTypes['time'] = Handsontable.TimeCell;
    Handsontable.renderers.registerRenderer('time', TimeRenderer);

    Handsontable.DateTimeCell = {
        editor : DateTimeEditor,
        renderer : DateTimeRenderer,
        validator : Handsontable.AutocompleteValidator
    };
    Handsontable.DateTimeRenderer = DateTimeRenderer;
    Handsontable.renderers.DateTimeRenderer = DateTimeRenderer;
    Handsontable.cellTypes['datetime'] = Handsontable.DateTimeCell;
    Handsontable.renderers.registerRenderer('datetime', DateTimeRenderer);

})(Handsontable);
