
# Remote Rig Control

These files are not, strictly, part of this project. But if your
rig is connected to the Raspberry Pi for CI-V and/or for audio, or,
as many late-model Icom rigs will allow, connected by all of those
through a single USB cable, then it *is* possible to control and use
the rig remotely using only the RPi as your host.

## How it works

The files in here show some of the commands necessary to accomplish this
trick. It assumes Ubuntu 16.04 on the client side and Rasbbian Jessie on the 
host side.

`socat` command allows a serial port to be forwarded to a TCP port and back again. You run it on the client and host, with different parameters.

`pulseaudio` also can naturally connected audio devices to network ports

`ssh` can be used to roll up several ports and forwarded them over a 
cryptographically secure external port, allow a client to open one 
secure port to the host and the have "virtual" local ports that connect
to the various ports on the host that are being forwarded.

I know this file and the snippets in this folder are not enough to 
get everything working, but they should get your started. I have successfully
controlled and used my IC-7300 to make QSOs from work using the commands
herein.

