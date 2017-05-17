# RigMinder

Hardware, Firmware, and Server-ware implementation of a power-off watchdog
for amateur radio gear. This is interesting for hams that want to operate
their rigs remotely over the Internet, and want to comply with 
47 CFR 97.213(b):

    (b) Provisions are incorporated to limit transmission by the station 
    to a period of no more than 3 minutes in the event of malfunction 
    in the control link.

Because Internet connections fail in unpredictable and interesting ways,
this project seeks to implement an external fail-safe based on a hardware 
watchdog timer. The watchdog is pinged periodically over the Internet. The
easiest way to do this is to open a web page on the controller server. As 
long as your http POSTS go through, the station stays up. If they do not, 
the station is automatically powered down.

## Hardware

The hardware portion is built around a combination of Raspberry Pi 
as the controlling computer and Atmel ATMEGA328 as the watchdog controller. 

The RPi is an easy platform to use and has flexible network interfaces
and GPIO, and you can program it in any language you want with any libraries
you want.

The ATMEGA directly controls the switches, and implements the timer 
functionality. If the RPi crashes for some reason, the system will still
shut down. The ATMEGA is running very simple firmware and is unlikely to 
fail. The ATMEGA is also connected to headers on the board arranged like
an Arduino Duemilanove,  so in essence the board *is* and Arduino.

The board has provision for controller one DC device using a parallel
pair of low Rds_on P-FETs, allowing "high side" switching. An AC device 
can also be switched, using a Triac driver circuit. The device is safe 
without an enclosure if you are not using the AC. However, if you are, you
really need a box.

The board also has two controllable LEDs, one of which is also connected
to an optisolated open collector transistor which you can use to switch
"whatever"

### Hardware features:

 * Atmel ATMEGA328P-PU, just like an Ardunio Due and with the same header

 * Additional header designed to connect directly to first portion of RPi 
   GPIO header

 * Provision for 1, 2, or 3 parallel P-FETS to drive DC output. This 
   should result in low overall Rds_on and minimal power dissipation in
   the switch, even when operating at 30A

 * DC termination is in 45A Anderson Power Pole connectors. The input
   is on top and the output is on the bottom.

 * An ATO-style fuse for the DC side

 * An opto-isolated 6A triac that can control AC loads -- use at your own 
   risk. The AC output is also fused.

 * An opto-isolated output for other control use

 * An additional controllable LED

 * Voltage measurement in the Atmel for both the DC input and output 
   voltages. The difference between these can be used to make a crude
   current measurement as well.

 * The board has very flexible power options. A 5V regulator can power
   the board from the 12C DC input, or you can do it from a separate
   power jack, or you can let the RPi power the board (or let the board
   power the RPi)

 * Entire board can fit in a Hammon 1285 box


## Software

The software is in three components:

On the Atmel, we run a very simple firmware. It implements a handful
of "registers" that can be written and read externally. These registers
contain the current value of the countdown timer, as well as controls 
for the outputs and the values for the voltage sensing. The Atmel simply
counts down the timer aand when it hits zero, the outputs are switched
off.

Provision is made for communications between the Atmel and the Raspberry
Pi using i2c, or using the i2c pins but a custom protocol, or the serial
pins, or the SPI pins. It's your choice. I have implemented a custom
protocol over the i2c pins, but this was mostly for the fun in doing so.

On the RPi, we run a python-based web server that can return the status
of the underlying watchdog in a GET request, or update the registers with
various POST requests. The server also serves up some static files, including
the html and javascript code that represent the third component.

Your remote browser loads a page hosted by the RPi server. On that page,
code runs that periodically pings the server to obtain the status, and
sends a watchdog reset command when the timer gets low.




