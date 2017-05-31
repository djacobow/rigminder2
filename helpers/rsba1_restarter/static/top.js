
var xhrAndDo = function(url,cb,data) {
    var xhr = new XMLHttpRequest();
    var loadListener = function() {
        if (xhr.status === 200) {
            console.log(xhr.responseText)
            var d = JSON.parse(xhr.responseText);
            return cb(d);
        } else {
            return cb({status: xhr.status, msg: 'post/get fail at ' + url});
        }
    };
    xhr.timeout = 5000;
    xhr.addEventListener('load',loadListener);
    if (data === null) {
        xhr.open('GET',url);
    } else {
        xhr.open('POST',url);
    }
    xhr.ontimeout = function() {
        cb({status: 'err', msg: 'timeout on ' + url});
    };
    xhr.setRequestHeader('Content-Type','application/json');
    if (data === null) {
        xhr.send();
    } else {
        xhr.send(JSON.stringify(data));
    }
};

var getTok = function(cb) {
    var kn = function(d) {
        if (d && d.result && d.result === 'OK') {
            return cb(d.token);
        } else {
            return cb(null)
        }
    }
    xhrAndDo('/gettoken',kn,null);
};

var tryIt = function(tok, what) {
    data = {
        token: tok,
        secret: 'Beeblebrox',
    };
    xhrAndDo(what, function(res) {
        document.getElementById('results').innerText = JSON.stringify(res,null,2);
        console.log(res);
    }, data);
};

var setup = function() {
 var kb = document.getElementById('killit');
 var sb = document.getElementById('startit');
 kb.addEventListener('click', function() {
     getTok(function(tok) {
         tryIt(tok,'/killit');
     });
 });
 sb.addEventListener('click', function() {
     getTok(function(tok) {
         tryIt(tok,'/startit');
     });
 });
}


setup()


