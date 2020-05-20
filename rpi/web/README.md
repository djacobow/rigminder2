# RPi Software

The server here is a very simple example of code to run to communicate
between a client (a web browser) and the watchdog itself, providing 
a simple user interface to control the watchdog.

The server runs on port 8003 by default and implements a simple http
scheme, by which a browser can fetch an index.html (plus associated)
static file, and to which the browser can do xmlhttprequests to exchange
json with the server to cause certain actions.

## Installation

Assuming you have Raspbian Jessie already running on the pi, installation
is simple. Use raspi-config to enable i2c. Add the supplied example
systemd file to make the server into a service, then start the service
and look for errors. Assuming there are none, try to open
localhost:8003. If you get a page, you're in business.

