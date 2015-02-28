// handy function to encapsulate each API call, complete with logging and optional error handling
function api_call(name, params, callback, callback_error) {
    var json_request = JSON.stringify([{"id": 0, "jsonrpc": "2.0", "method": name, "params": params}]);
    console.log('api_call.REQUEST', json_request);
    $.ajax({
        url: '/api/v1/jsonrpc/client-version.0.0.1/', // API_ENDPOINT + SERVER VERSION + CLIENT_VERSION
        type: 'POST',
        data: json_request,
        dataType: 'json',
        headers: {
            'X-CLIENT-KEY': '21d56076-0df0-4b01-bd4e-13bb7fb4a403', // CLIENT KEY
        },
        success: function(response) {
            console.log('api_call.RESPONSE', response);
            if(response[0].error) {
                if(callback_error) {
                    callback_error(response);
                }else{
                    throw JSON.stringify(response[0].error);
                }
            }else{
                callback(response);
            }
        }
    });
}

$(document).ready(function() {
    api_call('sys_test', {'test': 'success'}, function(response) {
        alert(JSON.stringify(response));
    });
});
