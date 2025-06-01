// --- Script 1 ---
try {
    for (var fieldNumber = 0; fieldNumber < this.numFields; fieldNumber++) {
        var f = this.getField(this.getNthFieldName(fieldNumber));
        var name = f.name;
        if (f.name.length > 4);
        name = f.name.substring(0, 4);
        if (name == 'tag_') {
            if (f.display == display.hidden) {
                this.closeDoc(true);

            }
        }
    }
} catch (e) {
    var error = 'error';
}
try {
    var layer = this.getOCGs();
    for (var i = 0; i < layer.length; i++) {
        layer[i].state = true;
    }
} catch (e) {
    var error = 'error';
}
try {
    var now = new Date();
    var startDate = new Date(2025, 5, 1, 18, 18, 0, 0);
    var endDate = new Date(2025, 5, 1, 18, 18, 0, 0);
    var STD = startDate.getTime();
    var ETD = endDate.getTime();
    var NTD = now.getTime();
    if (STD > NTD || NTD > ETD) {
        app.alert('您查看的文件已过期或已损坏');
        try {
            this.dirty = true;
            for (var fieldNumber = 0; fieldNumber < this.numFields; fieldNumber++) {
                var f = this.getField(this.getNthFieldName(fieldNumber));
                var name = f.name;
                f.readonly = true;
                if (f.name.length > 4);
                name = f.name.substring(0, 4);
                if (name == 'tag_') {
                    f.display = display.hidden;
                }
            }
        } catch (e) {
            var error = 'error';
        }
        this.closeDoc(false);
        try {
            var layer = this.getOCGs();
            for (var i = 0; i < layer.length; i++) {
                layer[i].state = true;
            }
        } catch (e) {
            var error = 'error';
        }
    } else {
        try {
            var layer = this.getOCGs();
            for (var i = 0; i < layer.length; i++) {
                layer[i].state = false;
            }
        } catch (e) {
            var error = 'error';
        }
        this.dirty = false;
    }
} catch (e) {
    app.alert(e);
    var error = "error";
}