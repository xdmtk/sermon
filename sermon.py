import curses, os, time

COL = None; ROW = None
PORT = None
MODE = 'normal'
LINE_BUFFER = ''
LINE_POS = 1

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
    if MODE == 'insert':
        if key == 27:
            set_normal_mode(w)
        else:
            if key == curses.KEY_ENTER:
                flush_input(w,key)
            else:
                process_input(w,key)


def flush_input(w,key):
    global LINE_POS
    USER_PROMPT = os.getenv('USER') + '@' + os.getenv('HOSTNAME') + ' >> '
    for x in range(2, COLS-1):
        w.addchr(ROW-1, x, ' ')
    if PORT is None:
        w.addstr(LINE_POS, 1, USER_PROMPT + LINE_BUFFER)
        LINE_POS += 1
        w.addstr(LINE_POS, 1, 'No port/device specified!')
    else:
        # TODO: Implement serial logic 
        pass
    w.refresh()



def process_input(w,key):
    
    global LINE_BUFFER 
    INPUT_HEIGHT = ROW-1

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
    w.refresh()
    MODE = 'insert'
    pass

def enter_command(w):
    pass
    



def draw_workspace(w):
    DH_LINE = '═' ; LINE = '─' ; DU_RCOR = '╗' ; DU_LCOR = '╔' 
    DL_LCOR = '╚' ; DL_RCOR = '╝' ; DV_LINE = '║'

    global COL ; global ROW
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
    for x in range(0, COL):
        if (x > (COL/2) - (l_title/2)) and (x < (COL/2) + (l_title/2)):
            w.addch(0, x, title[y] , curses.A_REVERSE | curses.A_BOLD)
            y += 1
        else:
            w.addch(0, x, ' ', curses.A_REVERSE)

    w.refresh()


os.environ.setdefault('ESCDELAY', '25')
curses.wrapper(main)
