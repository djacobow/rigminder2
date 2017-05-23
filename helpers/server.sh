#!/bin/sh 

# first, use paprefs to turn on network access to 
# pulseaudio

pulseaudio --kill

pulseaudio &

# take a tty and offer it up on the network
socat -d TCP-LISTEN:7001,nodelay,fork /dev/ttyUSB0,raw,b19200,echo=0 &



