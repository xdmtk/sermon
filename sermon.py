import curses, os, time
import socket, sys, serial
import signal, subprocess
from threading import Thread
import queue

Q = None
S = None
LT = None
COL = None
ROW = None
PORT = None
INPUT_HEIGHT = None
TERM_CHR = '\n'
BAUD_RATE = 9600

ERROR = -1
MODE = 'normal'
LINE_BUFFER = ''
COMMAND_BUFFER = ''
LINE_POS_BEGIN = 2
USER_PROMPT = os.getenv('USER') + '@' + socket.gethostname() + ' >> '

serial_history = []
input_history = []

com_hist_mark = 0
quit_flag = None
b_count_w = 0
b_count_r = 0


def main(w):
    global Q
    global LT

    def clean_thread_exit(sig, frame):
        global quit_flag
        quit_flag = True
        quit()

    signal.signal(signal.SIGINT, clean_thread_exit)

    draw_workspace(w)
    Q = queue.Queue()
    listener_thread = Thread(target=serial_listen, args=[w])
    LT = listener_thread
    if PORT is not None:
        listener_thread.start()

    while True:
        key_events(w)


def serial_listen(w):
    global quit_flag
    global S
    global b_count_r

    S = serial.Serial(PORT)
    S.baudrate = BAUD_RATE
    while True:
        if quit_flag is not None:
            S.close()
            curses.endwin()
            quit()
        msg = S.readline()
        b_count_r += len(msg)
        Q.put(msg)
        write_history(w)


# SECTION: MASTER KEY EVENTS
#############################################
###
#

def key_events(w):
    
    global com_hist_mark
    key = w.getch()
    
    # Handle normal mode entries
    if MODE == 'normal':
        if key == ord(':'):
            enter_command(w)
        if key == ord('i'):
            set_insert_mode(w)
        if key == curses.KEY_NPAGE:
            pass
        if key == curses.KEY_PPAGE:
            pass

    # Handle insert mode entries
    elif MODE == 'insert':
        if key == 27:
            set_normal_mode(w)
        else:
            if key == curses.KEY_ENTER or key == 10:
                flush_input(w)
                com_hist_mark = 0
            else:
                process_input(w, key)



# SECTION: CURSES WRITERS
#############################################
###
#

def write_byte_count(w):

    (cur_y, cur_x) = curses.getsyx()

    # Starting position decided by len of r/w string
    start_pos = COL - len('RECV: XXX  -  WRITE: XXX')

    # Write received and written to upper right corner
    w.addstr(0, start_pos, 'RECV: ' + str(b_count_r).rjust(3) +
             '  -  WRITE: ' + str(b_count_w).rjust(3), curses.A_REVERSE | curses.A_BOLD)

    w.move(cur_y, cur_x)
    w.refresh()



def write_history(w, user_write=False):

    # Save current cursor position
    (cur_y, cur_x) = curses.getsyx()

    # Check for new entries from serial port into serial queue
    if Q.empty() is False:

        # Add all data from queue to the serial history list
        while Q.empty() is False:
            ser_response = Q.get().decode('ascii').replace('\n', '')
            serial_history.append(PORT + ' >> ' + str(ser_response))

    # Count measures the amount of overflow lines in serial history
    # to determine for curses when to start writing text to the text area
    count = 0
    if len(serial_history) >= (INPUT_HEIGHT - LINE_POS_BEGIN):
        count = len(serial_history) - (INPUT_HEIGHT - LINE_POS_BEGIN - 1)

    
    x = 0
    line_pos = LINE_POS_BEGIN
    for line in serial_history:

        if count != 0 and x < count:
            x += 1
            continue
        for y in range(2, COL - 1):
            w.addch(line_pos, y, ' ')
        w.addstr(line_pos, 1, line)
        line_pos += 1
    if user_write is True:
        w.move(INPUT_HEIGHT, 2)
    else:
        write_byte_count(w)
        w.move(cur_y, cur_x)
    w.refresh()


# SECTION: INSERT MODE INPUT
#############################################
###
#

def process_input(w, key):

    global LINE_BUFFER

    # Backspace logic for text entry
    if key == curses.KEY_BACKSPACE:
        (y, x) = curses.getsyx()
        if x == 2:
            return
        w.addch(y, x - 1, ' ')
        w.move(y, x - 1)
        LINE_BUFFER = LINE_BUFFER[:-1]
        w.refresh()
        return

    # Currently only key up works, cycling through
    # previous input
    elif key == curses.KEY_UP:
        write_input_history(w, 'up')
        return
    elif key == curses.KEY_DOWN:
        write_input_history(w, 'down')
        return

    # Silently ignore left and right keys
    elif key == curses.KEY_LEFT:
        return
    elif key == curses.KEY_RIGHT:
        return

    # Otherwise add to the line buffer and print it
    LINE_BUFFER += chr(key)
    w.addstr(INPUT_HEIGHT, 2, LINE_BUFFER)
    w.refresh()


def flush_input(w):

    global LINE_BUFFER
    global b_count_w
    
    # Add input to history 
    input_history.append(LINE_BUFFER)

    # Clear text area 
    for x in range(2, COL - 1):
        w.addch(INPUT_HEIGHT, x, ' ')

    # Only write to serial if port is specified
    if PORT is None:
        serial_history.append(USER_PROMPT + LINE_BUFFER)
        serial_history.append('No port/device specified!')
        write_history(w, True)
    
    # Record bytes written successfully
    else:
        b_written = S.write(bytes((LINE_BUFFER + TERM_CHR).encode('ascii')))

        if b_written != 0:
            serial_history.append(USER_PROMPT + LINE_BUFFER)
            write_history(w, True)

        # If no bytes are written, log error
        else:
            serial_history.append(USER_PROMPT + LINE_BUFFER)

            if len(LINE_BUFFER) != 0:
                serial_history.append('Failed to write to serial port')

            # Unless buffer was empty
            else:
                serial_history.append('Can\'t write empty message')
            write_history(w, True)

        b_count_w += b_written
        write_byte_count(w)

    LINE_BUFFER = ''



# SECTION: MODE SETTERS
#############################################
###
#

def set_normal_mode(w):

    global MODE

    # Remove insert label on top left
    w.addstr(0, 0, '      ', curses.A_REVERSE | curses.A_BOLD)
    w.refresh()
    MODE = 'normal'
    pass


def set_insert_mode(w):
   
    global MODE
    MODE = 'insert'

    # Add insert label
    w.addstr(0, 0, 'INSERT', curses.A_REVERSE | curses.A_BOLD)

    # Move cursor to text entry area
    w.move(INPUT_HEIGHT, 2 + len(LINE_BUFFER))
    curses.curs_set(1)
    w.refresh()


# SECTION: COMMAND ENTRY
#############################################
###
#

def enter_command(w):

    # Global containing current command
    global COMMAND_BUFFER

    # Make cursor visible
    curses.curs_set(1)

    # Clear out command entry area
    for x in range(0, COL):
        w.addch(ROW + 1, x, ' ')

    # Begin command buffer with entry character ':'
    # and print it
    COMMAND_BUFFER = ':'
    w.addstr(ROW + 1, 0, COMMAND_BUFFER)
    w.refresh()

    # Enter key entry loop
    key = w.getch()

    # Flush command on enter
    while key != curses.KEY_ENTER and key != 10:

        # Backspace logic ( move curses back and either 
        # keep cursor at begin on empty buffer )
        if key == curses.KEY_BACKSPACE:
            (y, x) = curses.getsyx()
            if x == 2:
                key = w.getch()
                continue

            # Or clear the buffer 1 character at a time and print it
            w.addch(y, x - 1, ' ')
            w.move(y, x - 1)

            COMMAND_BUFFER = COMMAND_BUFFER[:-1]
            key = w.getch()
            w.refresh()
            continue
        
        # Silently ignore keypad keys
        if key == curses.KEY_UP:
            key = w.getch()
            continue
        elif key == curses.KEY_DOWN:
            key = w.getch()
            continue
        elif key == curses.KEY_LEFT:
            key = w.getch()
            continue
        elif key == curses.KEY_RIGHT:
            key = w.getch()
            continue

        # If all passes, add key to buffer and print result
        COMMAND_BUFFER += chr(key)
        w.addstr(ROW + 1, 0, COMMAND_BUFFER)
        w.refresh()

        # Restart key grab
        key = w.getch()

    # On finish, jump to parse command
    parse_command(w)


def parse_command(w):
    global LINE_BUFFER
    global COMMAND_BUFFER
    global INPUT_HEIGHT
    global quit_flag
    global PORT
    global b_count_w 

    # For the few select commands, find special keys to parse
    if COMMAND_BUFFER.find('q') != -1:
        quit_flag = True
        quit()

    # For port entry
    elif COMMAND_BUFFER.find('port ') != -1:

        # Verify port exists
        if os.path.exists(COMMAND_BUFFER.split(' ')[1]):

            # Gets the second token in port command entry
            PORT = COMMAND_BUFFER.split(' ')[1]
            draw_workspace(w)

            # Now that we have the port, start the serial listening thread store
            # in global LT
            LT.start()
        
        # If port is invalid, print error
        else:
            w.addstr(ROW + 1, 0, 'Invalid port!')
            w.refresh()
            curses.curs_set(0)
            return

    # Parse bytes entered for byte entry command
    elif COMMAND_BUFFER.find('byte ') != -1:
        byte_str = COMMAND_BUFFER[6:]

        b_count_w_local = 0
        byte_str = byte_str.split(' ')
        for b in byte_str:
            b_count_w_local += S.write(bytearray([int(b)]))
        
        w.addstr(ROW+1, 0, 'Wrote ' + str(b_count_w_local) + ' bytes')
        w.refresh()
        
    if COMMAND_BUFFER.find('byte ') == -1:
        # On enter, clear command entry area
        for x in range(0, len(COMMAND_BUFFER)):
            w.addch(ROW + 1, x, ' ')

        # Disappear cursor
        curses.curs_set(0)
        w.refresh()


# SECTION: CURSES FUNCTIONS
#############################################
###
#

def draw_workspace(w):
    global COL
    global ROW
    global INPUT_HEIGHT
   
    # Line drawing chars
    DH_LINE = '═'
    DU_RCOR = '╗'
    DU_LCOR = '╔'
    DL_LCOR = '╚'
    DL_RCOR = '╝'
    DV_LINE = '║'

    # Set the terminal height
    (ROW, COL) = w.getmaxyx()

    # Leave space for command entry
    ROW -= 2
    COL -= 1

    # Set row number of text entry area
    INPUT_HEIGHT = ROW - 1

    # Set corners
    w.addch(1, 0, DU_LCOR)
    w.addch(1, COL, DU_RCOR)
    w.addch(ROW, 0, DL_LCOR)
    w.addch(ROW, COL, DL_RCOR)

    # Draw lines
    for x in range(1, COL):
        w.addch(1, x, DH_LINE)
        w.addch(ROW, x, DH_LINE)
        w.addch(ROW - 2, x, DH_LINE)
    for x in range(2, ROW):
        w.addch(x, 0, DV_LINE)
        w.addch(x, COL, DV_LINE)


    # Set title
    title = 'sermon v0.9'
    if PORT is None:
        title += ' - no port specified'
    else:
        title += ' - ' + str(PORT)

    # Set the length of title to determine center position in title bar
    l_title = len(title)
    y = 0
    for x in range(0, COL + 1):

        # Calcuate center of title bar
        if (x > (COL / 2) - (l_title / 2)) and (x < (COL / 2) + (l_title / 2)):
            w.addch(0, x, title[y], curses.A_REVERSE | curses.A_BOLD)
            y += 1
        else:
            w.addch(0, x, ' ', curses.A_REVERSE)


    w.move(0, 0)
    w.refresh()



# SECTION: ARGUMENT FUNCTIONS
#############################################
###
#

def parse_args():
    global PORT
    global TERM_CHR
    global BAUD_RATE

    if len(sys.argv) > 1:
        for x in range(1, len(sys.argv)):

            # Arguemnt setting device port
            if sys.argv[x].find('-p') != -1:
                PORT = sys.argv[x + 1]
                x += 1
                continue
            
            # Argument to set termination character
            if sys.argv[x].find('-t') != -1:
                TERM_CHR = term_chr_parse(sys.argv[x + 1])
                x += 1
                continue

            # Argument to set baud rate
            if sys.argv[x].find('-b') != -1:
                try:
                    BAUD_RATE = int(sys.argv[x + 1])
                except Exception as e:
                    BAUD_RATE = ERROR
                x += 1
                continue

    # Check for argument erros
    if validate_args() == ERROR:
        print("Error with arguments")
        quit()


def validate_args():

    # Make sure device exists
    if PORT is not None:
        if os.path.exists(PORT) is False:
            return ERROR

    # Check baudrate and termination character 
    if TERM_CHR == ERROR or BAUD_RATE == ERROR:
        return ERROR


def term_chr_parse(arg):

    # Sets the termination char
    if arg == "nl":
        return '\n'
    if arg == "cr":
        return '\r'
    if arg == "nlcr":
        return '\n\r'
    else:
        return ERROR




def write_input_history(w, direction):
    global com_hist_mark
    global LINE_BUFFER

    com_hist_len = len(input_history)
    if com_hist_len == 0:
        return

    if direction == 'up':
        input_history.reverse()
        if (com_hist_len - com_hist_mark) <= 0:
            return

        LINE_BUFFER = input_history[com_hist_mark]
        com_hist_mark += 1
        input_history.reverse()

        for x in range(2, COL - 1):
            w.addch(INPUT_HEIGHT, x, ' ')
        w.addstr(INPUT_HEIGHT, 2, LINE_BUFFER)



parse_args()
os.environ.setdefault('ESCDELAY', '25')
curses.wrapper(main)
