# sermon
![](https://s3.amazonaws.com/xdmtk-test-group/sermon-demo.gif)
_Serial communication with a SIM808 GPRS module via usb-ttl adapater_

### SYNOPSIS: 

`python3 sermon.py [ -p ] [ PORT ] [ -t ] [ TERMINATION CHAR ] [ -b ] [ BAUD RATE ]`

### DESCRIPTION: 

`sermon` is a light-weight curses-based terminal serial monitor used for reading and writing to serial ports. The sermon text 
interface  uses `vim` inspired key bindings to switch between insert mode and command mode. 

Command line usage allows optional specification of three arguments, namely the device port to open a serial connection
on, the terminating character to send after submitting input to the serial device, and the baud rate. 


* **-p**  - Device port ( _example: /dev/ttyUSB0_ )

* **-t**  - Termination character ( Defaults to newline )

* **nl** -> Newline/line feed `\n`

* **cr** -> Carriage return `\r`

* **nlcr** -> Newline/linefeed + Carriage return `\r\n`

* **-b**  - Baud rate ( _Defaults to 9600_ )



### COMMAND MODE:

To begin entering commands, enter command mode using the ESC key and then open the command buffer by 
typing the character ':' 


##### PORT SPECIFICATION: 

In command mode you can specify on the fly the serial port to read/write from by using the 'port' command. 

* **Usage**: `:port [ PORT ]`
* **Example**: `:port /dev/ttyACM0` 


##### WRITING RAW BYTES:

In addition to entering ASCII range input, you can also write raw bytes directly to the device by using the 'byte' 
command. 

* **Usage**: `:byte [ BYTE INTEGER VALUE ]` <br> 
* **Example**: `:byte 26`  ( _sends CTRL-Z_ ) 


### Dependencies
 `sermon` requires `python3` and the `pyserial` module, installable through `pip3`

`apt-get install python3 python3-pip` <br>
`pip3 install pyserial`



### CONTACT:

`sermon` is under active development. To report a bug, please open an 
issue at https://github.com/xdmtk/sermon/issues
