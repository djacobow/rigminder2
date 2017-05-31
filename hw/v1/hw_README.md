# Hardware Notes

This folder contains the basic files to reproduce the v1 hardware of the 
Rigwatcher. This consists of a circuit board that contains a power
FET switch to control the rig power, controled by a built-in Arduino.

This is designed to be pretty easy assembly using almost all through-
hole parts. There are a couple of exceptions. I used a surface mount
button because I have a bunch of them, and I used a surface mount 
crystal (rear of board) for the Atmega. (However, it is possible to 
run the Atmega at 8 MHz with no crystal at all -- an option you should
consider.) It may also be hard to find a 0.1" TH 22pF capacitors. If
so, you can easily solder in 0805 22pF caps onto the TH pads.

## Bill of materials

The attached bill of materials contains the part numbers for most
parts, except for resistors and capacitors, which you can choose yourself.

### Anderson Power Poles

The connectors for Anderson Power Poles are rather special. Specified
in the BOM as "J1", they are actually assemblies of four differnt parts:
2x "bottom" right-angle 45A connector, 2x "top" right-angle 45A connectors,
2x red housings and 2 black housings.

### LEDs

Choose your own LEDs. The values provided should work for Red or 
Green with typical voltages. However, for the LED current limiting
resistors, you may want to choose larger resistors to make the LEDs
dimmer. This is a bit of a balancing act, as some LEDs are wired in series
with another LED inside an optoisolating device. Use that device's data
sheet to set the current, and pick a resistor appropriately given your 
chosen LEDs voltage drop and that of the LED in the opto.

### Headers

This board has a bunch of headers on it. All of them are 0.1" headers,
and I recommend you just buy strips of 0.1" headers and cut them appropriately.
You probably will want some jumpers to jump various headers, appropriately.

### AC Circuit

You should consider whether to populate the AC circuit at all. If you
are not comfortable with mains AC, leave it out. If you do, the entire
project should be in a box, and the wires connected to the board, either
soldered directly, or screwed in through an AK300/4 terminal block,
should have strain relief. Choose an appropriate 5x20 fuse for the device
you'll be switching.

If you are switching a resistive or capacitive load, like most power
supplies, you can leave out the snubber network C100 and R103. If
you are switching something inductive, you probably want them, though
the Triac in the BOM is "snubberless" and may be able to handle the 
load without them. You'll know if the load doesn't switch off.

### Other bits

You'll want a ribbon cable and appropriate female connectors 
to connect between the Raspberry Pi and this board. The connector
is 2x8 but actually, you only need the first few rows if you only
want to use i2c. The other pins are for other tricks you might want
to play with such, as using the serial interface, or hooking up the
SPI interface to program the Arduino in-situ

You'll also need hardware to mount the board. I'm partial to m3
screws and hex bolts, and typically do not mount the project in a 
case at all, but instead sandwich it between two pieces of acrylic.

The TO-220 device in the kit should also be heat-sunk. If you 
plan to power the board and RPi rom the 12V side or dc power jack,
the 7805 in particular will get quite warm. I recommend instead,
doing the reverse. Use a 5V plug-pack to power the RPi, and let that
power the 5V to the board. If you do that, you can leave the DC jack
and 5V regulator off the BOM. You won't need them.

You'll need a handful of 0.1" jumpers.

## Construction Notes

There's not much special about this board in terms of assembly. It
is your standard TH kit. Observe polarity on the electrolytic caps
and diodes.

### Anderson Power Poles

This board is designed to switch 30A. That's a lot of current. In order
to make this possible with the minimum of voltage drop and heat generation,
I chose to connect big polygons of copper traces to the PowePole slots
withOUT any thermal isolation. The result is that you probably will not
be able to solder these with the typical pencil iron. Instead, use a 100W+
soldering "gun" and do the powerpoles very first. They are not difficult
to solder with the gun. While you are at it, use the gun to solder the 
fuse holder for the ATO fuse.

Attaching the housings to the APP connector is best done by aassembling
them together first, then pushing the assembly onto the soldered pins.
Facing the connectors, the black should be on the left. The housings
slide together using a dovetail arrangement. They will form a solid 2x2
block.

