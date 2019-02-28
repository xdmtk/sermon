
import curses, os, time
import socket

COL = None; ROW = None
PORT = None
MODE = 'normal'
LINE_BUFFER = ''
COMMAND_BUFFER = ''
LINE_POS_BEGIN = 2
USER_PROMPT = os.getenv('USER') + '@' + socket.gethostname() + ' >> '
INPUT_HEIGHT = None
serial_history = []

def main(w):
    draw_workspace(w)
    while True:
        key_events(w)




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

    for x in range(2, COL-1):
        w.addch(ROW-1, x, ' ')
    if PORT == None:
        serial_history.append(USER_PROMPT + LINE_BUFFER)
        serial_history.append('No port/device specified!')
        write_history(w)
    else:
        # TODO: Implement serial logic 
        pass
    LINE_BUFFER = ''

def write_history(w):
    count = 0
    x = 0
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
    w.move(INPUT_HEIGHT, 2)
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

    COMMAND_BUFFER = ':'
    w.addstr(ROW+1,0, COMMAND_BUFFER)
    w.refresh()
    key = w.getch() 
    while key != curses.KEY_ENTER and key != 10:
        COMMAND_BUFFER += chr(key)
        w.addstr(ROW+1,0, COMMAND_BUFFER)
        w.refresh()
        key = w.getch()
    
    parse_command(w)


def parse_command(w):
    global COMMAND_BUFFER
    global INPUT_HEIGHT

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


os.environ.setdefault('ESCDELAY', '25')
curses.wrapper(main)
