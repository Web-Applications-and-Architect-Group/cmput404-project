
function sendJSONXMLHTTPRequest(url, objects, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState==4) {
            try {
                if (xhr.status==200) {
                    //XXX: parse some JSON from the request!
                    //XXX: Pass the data to the callback!
                    var response = JSON.parse(xhr.responseText);
                    callback(response);
                }
            } 
            catch(e) {
                alert('Error: ' + e.name);
            }
        }
    };
    //XXX: POST to a URL
    //XXX: set the mimetype and the accept headers!
    // Remember to use application/json !
    xhr.open("POST",url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.send(JSON.stringify(objects));
}