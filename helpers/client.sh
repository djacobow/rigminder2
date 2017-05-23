#!/bin/sh

# set up ssh so that it will tunnel X as well as
# forward remote 7001 to localhost:7001 -- this will be the serial port
# forward remote 4713 to localhost:7002 -- this is pulseaudio 
# forward remote 8003 to localhost:7003 -- this is for the watchdog server
ssh -N \
    -X \
    -L 7001:localhost:7001 \
    -L 7002:localhost:4713 \
    -L 7003:localhost:8003 \
    pi@10.0.0.7  &

sleep 1

# not connect that serial port up
socat -d -d pty,raw,b19200 tcp:localhost:7001,nodelay &

sleep 1

# and make it writeable to we don't need to operate with sudo
sudo chmod a+rw /dev/pts/*

sleep 1

# point the pulse server to the forwarded port from the remote's 
# pulse server
export PULSE_SERVER=tcp:localhost:7002

# restart pulseaudio

pulseaudio --kill
sleep 1

pulseaudio --start

sleep 1
pulseaudio & 

