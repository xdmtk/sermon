# sermon
![](https://xdmtk-test-group.s3.amazonaws.com/fsasa.gif)


_Serial communication with a SIM808 GPRS module via usb-ttl adapater_


### Introduction

`sermon` is a light-weight curses-based terminal serial monitor used for reading and writing to serial 
devices during embedded development sessions. The sermon text interface  uses `vim` inspired key bindings 
to switch between insert mode and command mode. 

Command line usage allows optional specification of three arguments, namely the device port to open a serial 
connection on, the terminating character to send after submitting input to the serial device, and the baud rate. 

### Dependencies 

`sermon` makes use of the `serial` module, installable via the `pyserial` Pip package. Install using the 
`requirements.txt` file 

```
sudo pip3 install -r requirements.txt
```

### Usage

`./sermon [ -p ] [ PORT ] [ -t ] [ TERMINATION CHAR ] [ -b ] [ BAUD RATE ]`

##### Port

Without arguments `sermon` isn't very useful. At minimum a serial device should be specified with the `-p` 
argument. The following opens a serial session on `/dev/USB0`

```
./sermon -p /dev/USB0
```

##### Termination Character

Some serial enabled devices are picky about what constitutes a complete transmission. When sending messages 
to a serial device with `sermon`, the default behavior is to append a `\n` character to the message. 

However this can be changed by specifying the `-t` argument with the the following options.

* **nl** -> Newline/line feed `\n`

* **cr** -> Carriage return `\r`

* **nlcr** -> Newline/linefeed + Carriage return `\r\n`

The following opens a serial session on `/dev/USB0`, and specifies the termination sequence as `\n\r`

```
./sermon  -p /dev/USB0 -t nlcr
```

##### Baud Rate

`sermon` also allows you to set the baud rate for the serial communication session with the `-b` flag. This
option defaults to 9600 if no baud rate is specified.


### Runtime Command Modes

To begin entering commands, enter command mode using the ESC key and then open the command buffer by 
typing the character ':' 


##### Port

In command mode you can specify on the fly the serial port to read/write from by using the 'port' command. 

* **Usage**: `:port [ PORT ]`
* **Example**: `:port /dev/ttyACM0` 


##### Raw Byte Transmission

In addition to entering ASCII range input, you can also write raw bytes directly to the device by using the 'byte' 
command. 

* **Usage**: `:byte [ BYTE INTEGER VALUE ]` <br> 
* **Example**: `:byte 26`  ( _sends CTRL-Z_ ) 


### Contact

`sermon` is slowly being revived as I continue with my own embedded projects. The latest release, 
v1.1, fixes a handful of annoying bugs that were present in the previous iterations. To report a bug, 
please open an issue at https://github.com/xdmtk/sermon/issues , though I may not get around to it. 
