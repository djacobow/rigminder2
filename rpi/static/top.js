
var config = {
    bitpositions: {
        'dc':  [ 0x1, '12V DC output' ],
        'ac':  [ 0x8, 'AC Triac output' ],
        'led': [ 0x2, 'LED Indicator' ],
        'oc':  [ 0x4, 'Isolated Open Collector Output' ],
    },
    voltage_ratios: {
        vin: 14.07 / 959,
        vout: 14.07 / 959,
        warn_hi: 13.8 * 1.1,
        warn_lo: 13.8 * 0.9,
    },
};


var drawProgress = function(elem,val,max) {
    var fr = val / max;
    var width = Math.floor(fr*100 + 0.5);
    if (width < 0)   width = 0;
    if (width > 100) width = 100;
    elem.style.width = width.toString() + '%';
};

var colorizeBar = function(elem,val,color,lo,locolor,hi,hicolor) {
    if      (lo && (val <= lo)) color = locolor;
    else if (hi && (val >= hi)) color = hicolor;
    elem.style['background-color'] = color;
};


var showStatus = function(d) {
    var fetch_time = new Date();
    var status_time = new Date(d.last_read);
    var wdog_mask_value = d.registers.REG_WDOG_MASK.value;
    var output_value = d.registers.REG_OUTPUT.value;
    var timer_value = d.registers.REG_TIMER.value;
    document.getElementById('dbg').innerText = JSON.stringify(d,null,2);

    var bpids = Object.keys(config.bitpositions);
    for (var i=0; i<bpids.length; i++) {
        var bpid = bpids[i];
        var bp   = config.bitpositions[bpid];
        var mask = bp[0];
        var name = bp[1];
        var elemid = 'output_bits_' + bpid;
        document.getElementById(elemid).checked = output_value & mask ? 'checked' : '';
        elemid = 'mask_bits_' + bpid;
        document.getElementById(elemid).checked = wdog_mask_value & mask ? 'checked' : '';
    }

    document.getElementById('timer_val').innerText = timer_value;


    var voltages = {
        vin: 'REG_VIN',
        vout: 'REG_VOUT',
    };

    Object.keys(voltages).forEach(function(v) {
        var value = d.registers[voltages[v]].value & 0x3ff;
        var volts = Math.floor((value * config.voltage_ratios[v]) * 100) / 100;
        var bdiv  = document.getElementById(v + '_bar');
        colorizeBar(bdiv,volts,
            'green',
            config.voltage_ratios.warn_lo,'yellow',
            config.voltage_ratios.warn_hi,'yellow');
        drawProgress(bdiv,value,1023);
        document.getElementById(v + '_val').innerText = volts.toString() + ' V';
    });



    var tbar_div = document.getElementById('timer_bar');
    var tbar_back_div = document.getElementById('timer_all');

    var reset_val = parseInt(document.getElementById('wdog_reset_timer_val').value);
    drawProgress(tbar_div,timer_value,reset_val);
    var ping_time = parseInt(document.getElementById('wdog_ping_time').value);
    if (timer_value < 1) {
        tbar_back_div.style['background-color'] = 'red';
    } else if (timer_value <= ping_time) {
        tbar_div.style['background-color'] = 'yellow';
        tbar_back_div.style['background-color'] = 'grey';
    } else {
        tbar_div.style['background-color'] = 'green';
        tbar_back_div.style['background-color'] = 'grey';
    }

    var auto_reset = document.getElementById('wdog_enable_auto').checked;
    if (auto_reset) {
        if (timer_value <= ping_time) resetTimer();
    }
};


var postAndDo = function(url,data,cb) {
    var xhr = new XMLHttpRequest();
    var loadListener = function() {
        if (xhr.status === 200) {
            var d = JSON.parse(xhr.responseText);
            cb(d);
        } else {
            cb({status: xhr.status, msg: 'post fail at ' + url});
        }
    };
    xhr.timeout = 5000;
    xhr.addEventListener('load',loadListener);
    xhr.open('POST',url);
    xhr.ontimeout = function() {
        cb({status: 'err', msg: 'timeout on ' + url});
    };
    xhr.setRequestHeader('Content-Type','application/json');
    xhr.send(JSON.stringify(data));
};



var showResetTimerResult = function(d) {
    var rdiv = document.getElementById('last_update_result');
    if (d.ok) {
        rdiv.innerText = JSON.stringify(d);
    } else {
        rdiv.innerText = JSON.stringify(d);
    }
};

var resetTimer = function() {
    var send_obj = {
        'timer_val': parseInt(document.getElementById('wdog_reset_timer_val').value),
    };
    postAndDo('/timer',send_obj,showResetTimerResult);
};

var doNothing = function() {};

var changeResetMask = function(ev) {
    var bpids = Object.keys(config.bitpositions);
    var ov = 0;
    bpids.forEach(function(bpid) {
        var cbid = 'mask_bits_' + bpid;
        var msk  = config.bitpositions[bpid][0];
        var set  = document.getElementById(cbid).checked;
        if (set) ov |=msk;
    });

    postAndDo('/setresetmask',{set_val: ov}, doNothing);
};

var changeOutput = function(ev) {
    var bpids = Object.keys(config.bitpositions);
    var ov = 0;
    bpids.forEach(function(bpid) {
        var cbid = 'output_bits_' + bpid;
        var msk  = config.bitpositions[bpid][0];
        var set  = document.getElementById(cbid).checked;
        if (set) ov |=msk;
    });

    postAndDo('/setoutput',{set_val: ov}, doNothing);
};

var fetchStatus = function() {
    var xhr = new XMLHttpRequest();
    var loadListener = function() {
        if (xhr.status === 200) {
            try {
                var d = JSON.parse(xhr.responseText);
                showStatus(d);
            } catch (e) {
                console.warn('That went poorly.');
                console.warn(xhr.responseText);
            }
        }
    };
    xhr.addEventListener('load',loadListener);
    xhr.open('GET','/status');
    xhr.send();
};

var fetchStatusWrapper = function() {
    fetchStatus();
    setTimeout(fetchStatusWrapper, 2000);
};

var createOutputCheckboxes = function() {
    var bpids = Object.keys(config.bitpositions);
    var groups = {
        'outputs': [ 'outputs_val', 'output_bits_', ],
        'reset_mask': [ 'reset_mask_val', 'mask_bits_', ],
    };
    Object.keys(groups).forEach(function(k) {
        var nelems = [];
        var tgtdiv = document.getElementById(groups[k][0]);
        bpids.forEach(function(bpid) {
            var cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.id = groups[k][1] + bpid;
            cb.checked = '';
            cb.addEventListener('change',k === 'outputs' ? changeOutput : changeResetMask);
            var sp = document.createElement('span');
            var br = document.createElement('br');
            sp.innerText = config.bitpositions[bpid][1];
            nelems.push(cb);
            nelems.push(sp);
            nelems.push(br);
        });
        nelems.forEach(function(ne) { tgtdiv.appendChild(ne); });
    });


};
var init = function() {
    createOutputCheckboxes();
    document.getElementById('wdog_reset').addEventListener('click',resetTimer);
    fetchStatusWrapper();

};


init();

