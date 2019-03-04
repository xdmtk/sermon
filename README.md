# sermon
![](https://s3.amazonaws.com/xdmtk-test-group/sermon-demo3.gif)
_Demo from simple Arduino Uno sketch to echo received serial input_


### SYNOPSIS: 

    python3 sermon.py [ -p ] [ PORT ] [ -t ] [ TERMINATION CHAR ] [ -b ] [ BAUD RATE ] 

### DESCRIPTION: 

    sermon is a light-weight curses-based terminal serial monitor used for reading and writing to serial ports. The sermon text 
    interface uses VIM inspired key bindings to switch between insert mode and command mode. 

    Command line usage allows optional specification of three arguments, namely the device port to open a serial connection
    on, the terminating character to send after submitting input to the serial device, and the baud rate. 


    -p  - Device port ( example: /dev/ttyUSB0 )

    -t  - Termination character ( Defaults to newline )
        
            nl -> Newline/line feed \'\\n\'

            cr -> Carriage return \'\\r\'

            nlcr -> Newline/linefeed * Carriage return \'\\n\\r\'

    -b  - Baud rate ( Defaults to 9600 )



### COMMAND MODE:

    To begin entering commands, enter command mode using the ESC key and then open the command buffer by 
    typing the character ':' 


    ##### PORT SPECIFICATION: 
        
        In command mode you can specify on the fly the serial port to read/write from by using the 'port' command. 
        
        Usage: port [ PORT ]
        Example: ( port /dev/ttyACM0 )

    
    ##### WRITING RAW BYTES:

        In addition to entering ASCII range input, you can also write raw bytes directly to the device by using the 'byte' 
        command. 
       
        Usage: byte [ BYTE INTEGER VALUE ] 
        Example: byte 26  ( sends CTRL-Z ) 


### Dependencies
 `sermon` requires Python3 and the `pyserial` module, installable through `pip3`

`apt-get install python3 python3-pip` <br>
`pip3 install pyserial`



### CONTACT:

    sermon is under active development and still in beta stages. Usage is at your own risk. To report bugs, please open an 
    issue at https://github.com/xdmtk/sermon/issues
