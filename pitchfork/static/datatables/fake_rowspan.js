$.fn.dataTableExt.oApi.fnFakeRowspan = function (oSettings, iColumn) {
    oSettings.aoDrawCallback.push({ "fn": fakeRowspan, "sName": "fnFakeRowspan" });
    function fakeRowspan () {
        var firstOccurance = null,
            value = null,
            rowspan = 0;
        jQuery.each(oSettings.aoData, function (i, oData) {
            var val = oData._aData[iColumn],
                cell = oData.nTr.childNodes[iColumn + 1];

            if (val != value) {
                value = val;
                firstOccurance = cell;
                rowspan = 0;
            }
            if (val == value) {
                rowspan++;
            }
            if (firstOccurance !== null && val == value && rowspan > 1) {
                oData.nTr.removeChild(cell);
                firstOccurance.rowSpan = rowspan;
            }
        });
    }
    fakeRowspan();
    return this;
};
