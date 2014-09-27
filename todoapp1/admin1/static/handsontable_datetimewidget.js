(function(Handsontable) {

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
            dateFormat : "yy-mm-dd",
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
        this.dateTimePickerStyle.display = 'block';
    };

    DateTimeEditor.prototype.hideDatepicker = function() {
        this.dateTimePickerStyle.display = 'none';
    };

    Handsontable.editors.DateTimeEditor = DateTimeEditor;
    Handsontable.editors.registerEditor('time', DateTimeEditor);
    Handsontable.editors.registerEditor('date', DateTimeEditor);
    Handsontable.editors.registerEditor('datetime', DateTimeEditor);

    var DateRenderer = function(instance, TD, row, col, prop, value, cellProperties) {
        value = value ? moment(value).format('ddd DD MMM, YYYY') : '';
        Handsontable.renderers.AutocompleteRenderer(instance, TD, row, col, prop, value, cellProperties);
    };
    var TimeRenderer = function(instance, TD, row, col, prop, value, cellProperties) {
        value = value ? moment(value).format('h:m a') : '';
        Handsontable.renderers.AutocompleteRenderer(instance, TD, row, col, prop, value, cellProperties);
    };
    var DateTimeRenderer = function(instance, TD, row, col, prop, value, cellProperties) {
        value = value ? moment(value).format('ddd DD MMM, YYYY h:m a') : '';
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
