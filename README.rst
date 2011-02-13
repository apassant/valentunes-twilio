Valentunes Twilio API
=====================

An endpoint to send songs to your sweetheart using Twilio.
Used in valentun.es, created at NYC MusicHackDay, 12-13 February 2011

Requirements
------------
1) Twilio Python bindings
  * Integrated in this package, updated version available at http://twilio.com/docs/libraries/
2) Apache with mod_wsgi
  * http://code.google.com/p/modwsgi/
3) Web.py
  * http://webpy.org

Getting started
---------------

1) Install the endpoint by copying these files somewhere in your Apache directory
2) Setup WSGIScriptAlias in your Apache config
  * WSGIScriptAlias /v /path/valentunes-twilio/cgi.py
  * Check .htaccess in case you rename cgi.py
3) Create a ./data directory and make it writable
4) Copy config.dist.py into config.py and edit the parameters accordingly
5) You can now POST JSON data to send a call and play the tunes

Testing with curl
-----------------

Here's an example of POSTing JSON data to the endpoint.
Parameters should be well-formatted JSON, argument name is 'data'.
'voice' and 'message' are optional arguments in the JSON, other are mandatory.
You can send up to 5 songs (if more, that will be cut to 5)::

    $ curl -X POST -d 'data={
        "to": "Julie",
        "from" : "Alex",
        "phone" : "XXX-XXX-XXXX",
        "message" : "I love you",
        "songs" : [
            {
                "title" : "One love song for you",
                 "url" : "http://example.org/songs/love.wav"
            },
            {
                "title" : "Im so happy with you",
                "url" : "http://example.org/songs/happiness.mp3"
            }
        ]
    }' http://example.org/v/cgi.py/call