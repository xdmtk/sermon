# sermon
![](https://s3.amazonaws.com/xdmtk-test-group/sermon-demo3.gif)
_Demo from simple Arduino Uno sketch to echo received serial input_

`sermon` is a curses-based serial monitor designed to be an alternative to the graphical
serial monitor provided by the Arduino IDE. 

### Dependencies
 `sermon` requires Python3 and the `pyserial` module, installable through `pip3`

`apt-get install python3 python3-pip` <br>
`pip3 install pyserial`

### Usage

`python3 sermon.py [ -p ] [ serial device ]`

`sermon` uses `vim` style keybindings to enter insert and command modes. 
