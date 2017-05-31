This folder contains "Arduino" software to compile and upload to the board.

USe the file in "Rigwatcher_v2_i2c". The other one is of historical interest
to me only.

Use ICSP programmer to plug into the header to program the Atmel with this
code. Select Arduino Duemilenove as the board. You can also use the ICSP
to program the bootloader and subsequently use the serial port to program
the device, though I don't know why you'd do that if you have a programmer.

If you do not have a programmer, I can send you a programmed chip, though
I recommend you follow one of the many tutorials that show how to use 
another Arduino to make a programmer

## Clock

The chip out of the box runs at 1 MHz with no crystsal. If you do not 
make any changes to the fuses, you will have to make changes to the 
timing in the arduino program by a factor of 16. If you solder on a
16 MHz crystal and the two 22pF caps, you can run at 16 MHz. In this
case, you can use the "burn firmware" option (set at Duemilanove) to
set the built in "fuses" to use the external crystal oscillator.

Another option is to use the internal oscillator, but set it to
8MHz. To do this, you will have to set fuses directly using avrdude.
Do not burn the bootloader, as this will reset your fuses.
