/**
    Copyright 2015 Robert Nelson. All Rights Reserved.
*/

var https = require('https');
var REMOTE_CLOUD_BASE_PATH = "/request";
var REMOTE_CLOUD_PORT = "42000";
var REMOTE_CLOUD_HOSTNAME = "isy994i.the-nelsons.org";

var log = log;

/**
 * Main entry point.
 * Incoming events from Alexa Lighting APIs are processed via this method.
 */
exports.handler = function(event, context) {

    // Warning! Logging this in production might be a security problem.
    log('Input', event);

    var postData = JSON.stringify(event);

    /**
     * Make a remote call to execute the action based on accessToken and the applianceId and the switchControlAction
     * Some other examples of checks:
     *	validate the appliance is actually reachable else return TARGET_OFFLINE error
     *	validate the authentication has not expired else return EXPIRED_ACCESS_TOKEN error
     * Please see the technical documentation for detailed list of errors
     */
    var options = {
        hostname: REMOTE_CLOUD_HOSTNAME,
        port: REMOTE_CLOUD_PORT,
        path: REMOTE_CLOUD_BASE_PATH,
        method: "POST",
        headers: {
            "Accept": '*/*', // Warning! Accepting all headers in production could lead to security problems.
            'Content-Type': 'application/json',
            'Content-Length': postData.length,
        }
    };

    if ('accessToken' in event.payload) {
        options.headers.Authorization = 'Bearer ' + event.payload.accessToken;
    }
    
    var callback = function(response) {
        var str = '';

        response.on('data', function(chunk) {
            // TODO: Add string limit here
            str += chunk.toString('utf-8');
        });

        response.on('end', function() {
            /**
             * Test the response from remote endpoint (not shown) and craft a response message
             * back to Alexa Connected Home Skill
             */
            // Warning! Logging this with production data might be a security problem.
            log('Done with result', str);
            
            context.succeed(JSON.parse(str));
        });

        response.on('error', function(e) {
            log('Error', e.message);
            /**
             * Craft an error response back to Alexa Connected Home Skill
             */
            context.fail(e.message);
        });
    };

    process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
    
    /**
     * Make an HTTPS call to remote endpoint.
     */
    var req = https.request(options, callback);
    
    req.end(postData);

    req.on('error', function(e) {
            log('Error', e.message);
            /**
             * Craft an error response back to Alexa Connected Home Skill
             */
            context.fail(generateControlError('SwitchOnOffRequest', 'DEPENDENT_SERVICE_UNAVAILABLE', 'Unable to connect to server'));
        });
};

/**
 * Utility functions.
 */
function log(title, msg) {
    console.log('*************** ' + title + ' *************');
    console.log(msg);
    console.log('*************** ' + title + ' End*************');
}

function generateControlError(name, code, description) {
    var headers = {
        namespace: 'Control',
        name: name,
        payloadVersion: '1'
    };

    var payload = {
        exception: {
            code: code,
            description: description
        }
    };

    var result = {
        header: headers,
        payload: payload
    };

    return result;
}
