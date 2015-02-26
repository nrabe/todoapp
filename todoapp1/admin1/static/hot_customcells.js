(function(window, Handsontable) {

    // "Fix" the numbers that do not allow for null values.
    var NumericRenderer = function(instance, TD, row, col, prop, value, cellProperties) {
        if (Handsontable.helper.isNumeric(value)) {
            if (typeof cellProperties.language !== 'undefined') {
                numeral.language(cellProperties.language)
            }
            value = numeral(value).format(cellProperties.format || '0'); //docs: http://numeraljs.com/
            Handsontable.Dom.addClass(TD, 'htNumeric');
        }
        Handsontable.renderers.TextRenderer(instance, TD, row, col, prop, value, cellProperties);
    };

    Handsontable.NumericRenderer = NumericRenderer; //Left for backward compatibility with versions prior 0.10.0
    Handsontable.renderers.NumericRenderer = NumericRenderer;
    Handsontable.renderers.registerRenderer('numeric', NumericRenderer);
    Handsontable.cellTypes.numeric.renderer = NumericRenderer;


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
        if (value === cellProperties.checkedTemplate || value === Handsontable.helper.stringify(cellProperties.checkedTemplate)) {
            INPUT.checked = true;
            TD.appendChild(INPUT);
        } else if (value === cellProperties.uncheckedTemplate || value === Handsontable.helper.stringify(cellProperties.uncheckedTemplate)) {
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
                beforeKeyDownHookBound: true
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

    CheckboxEditor.prototype.finishEditing = function() {};

    CheckboxEditor.prototype.init = function() {};
    CheckboxEditor.prototype.open = function() {};
    CheckboxEditor.prototype.close = function() {};
    CheckboxEditor.prototype.getValue = function() {};
    CheckboxEditor.prototype.setValue = function() {};
    CheckboxEditor.prototype.focus = function() {};

    Handsontable.CheckboxCell = {
        editor: CheckboxEditor,
        renderer: CheckboxRenderer,
    };
    Handsontable.CheckboxRenderer = CheckboxRenderer;
    Handsontable.renderers.CheckboxRenderer = CheckboxRenderer;
    Handsontable.cellTypes['checkbox'] = Handsontable.CheckboxCell;
    Handsontable.renderers.registerRenderer('checkbox', CheckboxRenderer);
})(window, Handsontable);

//////////////////////////////////////////////////////////////////////////////////////////////////////////////

(function(window, Handsontable) {

    var DateTimeEditor = Handsontable.editors.TextEditor.prototype.extend();
    DateTimeEditor.prototype.string_format = 'ddd DD MMM, YYYY h:mm a z';
    DateTimeEditor.prototype.startView = 2;
    DateTimeEditor.prototype.minView = 0;
    DateTimeEditor.prototype.maxView = 5;

    DateTimeEditor.prototype.init = function() {
        if (typeof jQuery != 'undefined') {
            $ = jQuery;
        } else {
            throw new Error("You need to include jQuery to your project in order to use the jQuery UI Datepicker.");
        }
        if (!$.fn.datetimepicker) {
            throw new Error("jQuery UI Datetimepicker dependency not found. Did you forget to include jquery-ui.custom.js or its substitute?");
        }

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
        this.dateTimePickerStyle.zIndex = 3000;
        document.body.appendChild(this.dateTimePicker);

        this.$dateTimePicker = $(this.dateTimePicker);

        var that = this;
        console.log(this.minView, this.maxView)
        var defaultOptions = {
            startView:this.startView,
            minView: this.minView,
            maxView: this.maxView,
            autoclose: true,
            minuteStep: 15,
            showMeridian: true,
            pickerPosition: 'bottom-right',
        };
        this.$dateTimePicker.datetimepicker(defaultOptions);
        this.$dateTimePicker.on('changeDate', function(ev) {
            var dateStr = ev.date ? moment.utc(ev.date).format(that.string_format) : '';
//            console.log('changeDate', ev.date, dateStr)
            that.setValue(dateStr);
            that.finishEditing(false);
        });

        var eventManager = Handsontable.eventManager(this);

        /**
         * Prevent recognizing clicking on jQuery Datepicker as clicking outside of table
         */
        eventManager.addEventListener(this.dateTimePicker, 'mousedown', function(event) {
            Handsontable.helper.stopPropagation(event);
            //event.stopPropagation();
        });

        this.hideDatepicker();
    };

    DateTimeEditor.prototype.destroyElements = function() {
        this.$dateTimePicker.dateTimePicker('destroy');
        this.$dateTimePicker.remove();
        //var eventManager = Handsontable.eventManager(this);
        //eventManager.removeEventListener(this.dateTimePicker, 'mousedown');
    };

    DateTimeEditor.prototype.open = function() {
        Handsontable.editors.TextEditor.prototype.open.call(this);
        this.showDatepicker();
    };

    DateTimeEditor.prototype.finishEditing = function(isCancelled, ctrlDown) {
        this.hideDatepicker();
        Handsontable.editors.TextEditor.prototype.finishEditing.apply(this, arguments);
    };

    DateTimeEditor.prototype.showDatepicker = function() {
        var offset = this.TD.getBoundingClientRect(),
            DatepickerSettings,
            datepickerSettings;


        this.dateTimePickerStyle.top = (window.pageYOffset + offset.top + Handsontable.Dom.outerHeight(this.TD)) + 'px';
        this.dateTimePickerStyle.left = (window.pageXOffset + offset.left) + 'px';

        DatepickerSettings = function() {};
        DatepickerSettings.prototype = this.cellProperties;
        datepickerSettings = new DatepickerSettings();
        datepickerSettings.defaultDate = this.originalValue || void 0;

        this.$dateTimePicker.datetimepicker('option', datepickerSettings);

        if (this.originalValue) {
            var value = moment.utc(this.originalValue);
//            console.log('showDatepicker', this.originalValue, value.format(), value.toDate())
            this.$dateTimePicker.datetimepicker('setUTCDate', value.toDate());
        }
        this.$dateTimePicker.datetimepicker("show");
        this.dateTimePickerStyle.display = 'block';
    };

    DateTimeEditor.prototype.hideDatepicker = function() {
        this.$dateTimePicker.datetimepicker('hide');
        this.dateTimePickerStyle.display = 'none';
    };

    var DateTimeEditor_renderer = function(instance, TD, row, col, prop, value, cellProperties) {
        console.log('DateTimeEditor_renderer', value,
            value?moment.utc(value).format():null,
            value?moment.utc(value).format(DateTimeEditor.prototype.string_format):null)
        value = value ? moment.utc(value).format(DateTimeEditor.prototype.string_format) : '';
        Handsontable.renderers.AutocompleteRenderer(instance, TD, row, col, prop, value, cellProperties);
    };

    Handsontable.DateTimeCell = {
        editor: DateTimeEditor,
        renderer: DateTimeEditor_renderer,
        validator: Handsontable.AutocompleteValidator
    };
    Handsontable.DateTimeRenderer = DateTimeEditor.rendererFunction;
    Handsontable.renderers.DateTimeRenderer = DateTimeEditor.rendererFunction;
    Handsontable.cellTypes.datetime = Handsontable.DateTimeCell;
    Handsontable.renderers.registerRenderer('datetime', DateTimeEditor.rendererFunction);

    var DateEditor = DateTimeEditor.prototype.extend();
    DateEditor.prototype.string_format = 'ddd DD MMM, YYYY';
    DateEditor.prototype.minView = 2;
    var DateEditor_renderer = function(instance, TD, row, col, prop, value, cellProperties) {
        console.log('DateEditor_renderer', value,
            value?moment.utc(value).format():null,
            value?moment.utc(value).format(DateEditor.prototype.string_format):null)
        value = value ? moment.utc(value).format(DateEditor.prototype.string_format) : '';
        Handsontable.renderers.AutocompleteRenderer(instance, TD, row, col, prop, value, cellProperties);
    };

    Handsontable.DateCell = {
        editor: DateEditor,
        renderer: DateEditor_renderer,
        validator: Handsontable.AutocompleteValidator
    };
    Handsontable.DateRenderer = Handsontable.DateCell.renderer;
    Handsontable.renderers.DateRenderer = Handsontable.DateCell.renderer;
    Handsontable.cellTypes.date = Handsontable.DateCell;
    Handsontable.renderers.registerRenderer('date', Handsontable.DateCell.renderer);


    var TimeEditor = DateTimeEditor.prototype.extend();
    TimeEditor.prototype.string_format = 'h:mm a';
    TimeEditor.prototype.maxView = 1;
    TimeEditor.prototype.startView = 1;
    TimeEditor.prototype.minView = 0;
    var TimeEditor_renderer = function(instance, TD, row, col, prop, value, cellProperties) {
        console.log('TimeEditor_renderer', value,
            value?moment.utc(value, 'h:mm a').format():null,
            value?moment.utc(value, 'h:mm a').format(TimeEditor.prototype.string_format):null)
        value = value ? moment.utc(value, 'h:mm a').format(TimeEditor.prototype.string_format) : '';
        Handsontable.renderers.AutocompleteRenderer(instance, TD, row, col, prop, value, cellProperties);
    };

    Handsontable.TimeCell = {
        editor: TimeEditor,
        renderer: TimeEditor_renderer,
        validator: Handsontable.AutocompleteValidator
    };
    Handsontable.TimeRenderer = Handsontable.TimeCell.renderer;
    Handsontable.renderers.TimeRenderer = Handsontable.TimeCell.renderer;
    Handsontable.cellTypes.time = Handsontable.TimeCell;
    Handsontable.renderers.registerRenderer('time', Handsontable.TimeCell.renderer);
})(window, Handsontable);


//////////////////////////////////////////////////////////////////////////////////////////////////////////////


(function(window, Handsontable) {

    var LookupRenderer = Handsontable.renderers.AutocompleteRenderer;

    var LookupEditor = Handsontable.editors.AutocompleteEditor.prototype.extend();

    Handsontable.renderers.registerRenderer('lookup', LookupRenderer);
    Handsontable.editors.registerEditor('lookup', LookupEditor);

    Handsontable.LookupCell = {
        editor: LookupEditor,
        renderer: LookupRenderer,
        validator: Handsontable.AutocompleteValidator
    };
    Handsontable.cellTypes.lookup = Handsontable.LookupCell;
    Handsontable.cellTypes.foreignkey = Handsontable.LookupCell;

})(window, Handsontable);
