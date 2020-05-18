# RigMinder

Hardware, Firmware, and Server-ware implementation of a power-off watchdog
for amateur radio gear. This is interesting for hams that want to operate
their rigs remotely over the Internet, and want to reliably comply with 
47 CFR 97.213(b):

    (b) Provisions are incorporated to limit transmission by the station 
    to a period of no more than 3 minutes in the event of malfunction 
    in the control link.

Because Internet connections, remote control software, and even modern,
highly computerized rigs fail in unpredictable and interesting ways,
this project seeks to implement an external fail-safe based on a hardware 
watchdog timer connected to a power switch: essentially, you must
periodically reset a timer in the watchdog or else the power is cut off. 
The easiest way to do this is to open a web page on the watchdog's server. 
As long as your http POSTS go through, the station stays up. If they do not, 
the station is automatically powered down. That's basically all there is
to it!

## Hardware

The hardware portion is built around a combination of Raspberry Pi 
as the controlling computer and Atmel ATMEGA328 as the watchdog controller. 

The RPi is a cheap and easy platform to use and has flexible network interfaces
and GPIO, and you can program it in any language you want with any libraries
you want. Another attraction of the Pi to me is that it could also serve
as the main "host" for remoting a rig over the Internet. For example,
I have an Icom rig with USB for audio and control. The RPi can be used to 
forward that audio and control as well as manage the watchdog -- a complete
remote solution in a tiny, cheap package.

The ATMEGA directly controls the switch and implements the timer 
functionality. If the RPi crashes for some reason, the system will still
shut down. The ATMEGA is running purposefully simple firmware and is 
unlikely to fail. The ATMEGA is also connected to headers on the 
board arranged like an Arduino Duemilanove, so in any practical sense, 
the board *is* an Arduino, if you want to use it that way.

Power switching is accomplised on the "high side" using a pair of low 
Rds_on PFETS connected to Anderson Power Poles. This means that the devices 
being switched always have a ground connection, only the 12V power is switched.

There is also provision for switching a small (<6A) AC device using
an optoisolated triac circuit on the board. If you are not comfortable
dealing with AC power, you should leave this part of the circuit
unpopulated. Also, if you do use the AC you *absolutely* should put
the project in a box, with strain relief on the AC wires.

The board also has two controllable LEDs, one of which is also connected
to an optisolated open collector transistor which you can use to switch
"whatever"

### Hardware features:

 * Atmel ATMEGA328P-PU, just like an Ardunio Due and with the same headers

 * Additional header designed to connect directly to first portion of RPi 
   GPIO header

 * Provision for 1, 2, or 3 parallel P-FETS to drive DC output. This 
   should result in low overall Rds_on and minimal power dissipation in
   the switch, even when operating at up to 30A. The board has been
   tested at 20A for over an hour without significant heating using only
   two 3.7 mOhm transistors.

 * DC termination is 45A Anderson Power Pole connectors. The input
   is on top and the output is on the bottom.

 * An ATO-style fuse is provided for protection on the DC side. You 
   should populaet with a 20A or 30A fuse.

 * An opto-isolated 6A triac that can control AC loads -- use at your own 
   risk. The AC output is also fused with a 5x20mm standard fuse. Use 
   a 6A fuse or less. For as 120V circuit, this should be enough to 
   switch a 30A 12V PSU.

 * An opto-isolated output is available for other control use (keying a 
   receier, etc)

 * An additional controllable LED just because LEDs are fun

 * Voltage measurement in the Atmel for both the DC input and output 
   voltages. This gives you positive data on whether the 12V source 
   power is present, and also whether the switch is really doing what 
   it was commanded to do (for example, if the PFETS have failed).
   The difference between these can also be used to make a very crude
   current measurement as well.

 * The board has very flexible options for powering itself. A 5V regulator 
   can power the board and the RPi from the 12V DC input or a DC barrel 
   jack, or you can skip the regulator and plug the RPi power directly into
   a plug pack and let that power the board.

 * Entire board can fit in a Hammond 1285 box


## Software

The software is in three components:

On the ATMEGA, we run a very simple firmware. It implements a handful
of "registers" that can be written and read externally. These registers
contain the current value of the countdown timer, as well as controls 
for the outputs and the values for the voltage sensing. The ATMEGA simply
counts down the timer aand when it hits zero, the outputs are switched
off (subject to a mask register).

Normal communication between the board and the RPi is done using i2c, and
at a minimum, only SCL, SDA, and ground must be shared between the RPi
and this board. However, the serial pins line up, and you can change the
firmware to use serial instead of i2c. You can even do it over SPI, using
additional GPIO on the RPi. (You may even be able to program the ATMEGA
this way.)

On the RPi, we run a python-based web server that can return the status
of the underlying watchdog in a GET request, or update the registers with
various POST requests. The server also serves up some static files, including
the html and javascript code that represent the third component.

Your remote browser loads a page hosted by the RPi server. On that page,
code runs that periodically pings the server to obtain the status, and
sends a watchdog reset command when the timer gets low.


## Setup

1. Build the hardware
2. Program the Arduino using the sketch provided. Use an ICSP programmer
   to program a brand new Atmega without a bootloader on it
3. Set up the server. Insteall the required Python modules and you should
   be good to go. Then create a systemd service to start the server 
   automatically.
4. Open a web page to the address and port of your RPi. You should get
   a web page that shows the state of the system.

## Operation

Operation is preetty straightforward, once you open the webpage, it will
periodically refresh, showing the state of the system. As the timer counts
down, the green timer bar will shorten. When it gets to a certain low value,
the system will automatically refresh it to a high value, and the process 
repeats. If, for any reason, the page loses contact with the server, the 
watchdog will time out and the rig will be turned off.

You can turn on and off the devices outputs by clicking on them. You can
also turn on and off a "mask" of the outputs, which defines which outputs
will be turned off in the event of the watchdog getting to zero. By default,
they're all one.

### Switching client computers on the fly

Sometimes you'll open this page on a computer, then walk away from the 
machine and forget about it. Unfortunatly, that machine will keep the 
watchdog up as long as it is running -- this may be be what you want if 
you switch to a different computer for remote operation. In this case,
open the webpage on the new computer and click the button "Update Session ID" 
to cause the server to generate a new unique ID. The new computer will have 
the new ID, but the old one will not. As a result, the old one will no 
longer be able to access the watchdog, and only the new one will be relevant
for keeping it up.

### Security

No provision is made for security. There is a magic key in the html that 
the json server expects to see, but anybody can pick that out of the html
code. Furthermore, everything is done over http rather than https.

If you want more robust security, edit the html to make the key an entry
that you have to fill in. Then consider hosting the server using https,
perhaps behind nginx and a free Let's Encrypt certificate. Alternatively,
if you are the only user, it might be easier to enable ssh on the Pi and 
use ssh to forward its local port with the server on it to a local port on
a computer connecting over ssh. This is what I do.

