
import curses, os, time
import socket, sys, serial
import signal 
from threading import Thread
import queue 

Q = None ; S = None ; LT = None
ERROR = -1
COL = None; ROW = None
PORT = None
MODE = 'normal'
LINE_BUFFER = ''
COMMAND_BUFFER = ''
LINE_POS_BEGIN = 2
USER_PROMPT = os.getenv('USER') + '@' + socket.gethostname() + ' >> '
INPUT_HEIGHT = None
serial_history = []
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
    if PORT != None:
        listener_thread.start()

    while True:
        key_events(w)

def serial_listen(w):
    global quit_flag
    global S
    global b_count_r 

    S = serial.Serial(PORT)
    while True:
        if quit_flag != None:
            S.close()
            curses.endwin()
            quit()
        msg = S.readline()
        b_count_r += len(msg)
        Q.put(msg)
        write_history(w)



def parse_args():
    global PORT
    if len(sys.argv) > 1:
        for x in range(1, len(sys.argv)):
            if sys.argv[x].find('-p') != -1:
                PORT = sys.argv[x+1]
                x += 1
                continue
    if validate_args() == ERROR:
        print("Error with arguments")
        quit()



def validate_args():
    if PORT != None:
        if os.path.exists(PORT) is False:
            return ERROR
    

def key_events(w):
    key = w.getch()
    if MODE == 'normal':
        if key == ord(':'):
            enter_command(w)
        if key == ord('i'):
            set_insert_mode(w)
    elif MODE == 'insert':
        if key == 27:
            set_normal_mode(w)
        else:
            if key == curses.KEY_ENTER or key == 10:
                flush_input(w,key)
            else:
                process_input(w,key)


def flush_input(w,key):
    global LINE_POS
    global LINE_BUFFER 
    global b_count_w

    for x in range(2, COL-1):
        w.addch(ROW-1, x, ' ')
    if PORT == None:
        serial_history.append(USER_PROMPT + LINE_BUFFER)
        serial_history.append('No port/device specified!')
        write_history(w, True)
    else:
        b_written = S.write(bytes(LINE_BUFFER.encode('ascii')))
        if b_written != 0:
            serial_history.append(USER_PROMPT + LINE_BUFFER)
            write_history(w, True)
        else:
            serial_history.append(USER_PROMPT + LINE_BUFFER)
            if len(LINE_BUFFER) != 0:
                serial_history.append('Failed to write to serial port')
            else:
                serial_history.append('Can\'t write empty message')
            write_history(w, True)
        
        b_count_w += b_written
        write_byte_count(w)

    LINE_BUFFER = ''

def write_byte_count(w):
    (cur_y , cur_x) = curses.getsyx()
    start_pos = COL - len('BYTES RECEIVED: XXX  -  BYTES WRITTEN: XXX')
    w.addstr(0, start_pos, 'BYTES RECEIVED: ' + str(b_count_r).rjust(3) + 
            '  -  BYTES WRITTEN: ' + str(b_count_w).rjust(3),  curses.A_REVERSE | curses.A_BOLD)

    w.move(cur_y, cur_x)
    w.refresh()

   


def write_history(w, user_write = False):
    (cur_y, cur_x) = curses.getsyx()
    count = 0
    x = 0
    q_write = False
    if Q.empty() is False:
        q_write = True
        while Q.empty() is False:
            ser_response = Q.get().decode('ascii').replace('\n','')
            serial_history.append(PORT + ' >> ' + str(ser_response))

    if len(serial_history) >= (INPUT_HEIGHT - LINE_POS_BEGIN):
        count = len(serial_history) - (INPUT_HEIGHT - LINE_POS_BEGIN - 1)

    line_pos = LINE_POS_BEGIN
    for line in serial_history:
        if count != 0 and x < count:
            x += 1
            continue
        for y in range(2,COL-1):
            w.addch(line_pos, y, ' ')
        w.addstr(line_pos, 1, line) 
        line_pos += 1
    if user_write is True:
        w.move(INPUT_HEIGHT, 2)
    else:
        write_byte_count(w)
        w.move(cur_y, cur_x)
    w.refresh()



def process_input(w,key):
    
    global LINE_BUFFER 
    if key == curses.KEY_BACKSPACE:
        (y,x) = curses.getsyx()
        if x == 2:
            return
        w.addch(y,x-1, ' ')
        w.move(y,x-1)
        LINE_BUFFER = LINE_BUFFER[:-1]
        w.refresh()
        return
    elif key == curses.KEY_UP:
        return
    elif key == curses.KEY_DOWN:
        return
    elif key == curses.KEY_LEFT:
        return
    elif key == curses.KEY_RIGHT:
        return

    LINE_BUFFER += chr(key)
    w.addstr(INPUT_HEIGHT, 2, LINE_BUFFER)
    w.refresh()


def set_normal_mode(w):
    global MODE
    w.addstr(0,0, '      ', curses.A_REVERSE | curses.A_BOLD)
    w.refresh()
    MODE = 'normal'
    pass


def set_insert_mode(w):
    global MODE
    w.addstr(0,0, 'INSERT', curses.A_REVERSE | curses.A_BOLD)
    w.move(INPUT_HEIGHT, 2 + len(LINE_BUFFER))
    curses.curs_set(1)
    w.refresh()
    MODE = 'insert'
    pass

def enter_command(w):
    global COMMAND_BUFFER 
    curses.curs_set(1)
    for x in range(0, COL):
        w.addch(ROW+1, x, ' ')
    w.refresh()

    COMMAND_BUFFER = ':'
    w.addstr(ROW+1,0, COMMAND_BUFFER)
    w.refresh()
    key = w.getch() 
    while key != curses.KEY_ENTER and key != 10:
        if key == curses.KEY_BACKSPACE:
            (y,x) = curses.getsyx()
            if x == 2:
                key = w.getch()
                continue
            w.addch(y,x-1, ' ')
            w.move(y,x-1)
            COMMAND_BUFFER = COMMAND_BUFFER[:-1]
            key = w.getch()
            w.refresh()
            continue
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
        COMMAND_BUFFER += chr(key)
        w.addstr(ROW+1,0, COMMAND_BUFFER)
        w.refresh()
        key = w.getch()
    
    parse_command(w)


def parse_command(w):
    global COMMAND_BUFFER
    global INPUT_HEIGHT
    global quit_flag
    global PORT

    if COMMAND_BUFFER.find('q') != -1:
        quit_flag = True
        quit()
    elif COMMAND_BUFFER.find('port ') != -1:
        if os.path.exists(COMMAND_BUFFER.split(' ')[1]):
            PORT = COMMAND_BUFFER.split(' ')[1]
            draw_workspace(w)
            LT.start()
        else:
            w.addstr(ROW+1, 0, 'Invalid port!')
            w.refresh()
            curses.curs_set(0)
            return





    for x in range(0, len(COMMAND_BUFFER)):
        w.addch(ROW+1, x, ' ')
    curses.curs_set(0)
    w.refresh()
    pass



def draw_workspace(w):

    DH_LINE = '═' ; LINE = '─' ; DU_RCOR = '╗' ; DU_LCOR = '╔' 
    DL_LCOR = '╚' ; DL_RCOR = '╝' ; DV_LINE = '║'

    global COL ; global ROW
    global INPUT_HEIGHT
    (ROW, COL) = w.getmaxyx()
    ROW -= 2 ; COL -= 1 

    w.addch(1, 0, DU_LCOR)
    w.addch(1, COL,DU_RCOR)
    w.addch(ROW, 0, DL_LCOR)
    w.addch(ROW, COL, DL_RCOR)
    
    for x in range(1,COL):
        w.addch(1,x, DH_LINE)
        w.addch(ROW,x, DH_LINE)
        w.addch(ROW-2,x, DH_LINE)
    for x in range(2,ROW):
        w.addch(x,0, DV_LINE)
        w.addch(x,COL, DV_LINE)
   
    title = 'sermon v0.9'
    if PORT is None:
        title += ' - no port specified'
    else:
        title += ' - ' + str(PORT)
    l_title = len(title) ; y = 0
    for x in range(0, COL+1):
        if (x > (COL/2) - (l_title/2)) and (x < (COL/2) + (l_title/2)):
            w.addch(0, x, title[y] , curses.A_REVERSE | curses.A_BOLD)
            y += 1
        else:
            w.addch(0, x, ' ', curses.A_REVERSE)
    INPUT_HEIGHT = ROW - 1
    w.move(0,0)
    w.refresh()


parse_args()
os.environ.setdefault('ESCDELAY', '25')
curses.wrapper(main)
