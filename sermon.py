import curses, os, time


COL = None; ROW = None
DH_LINE = '═' ; LINE = '─' ; DU_RCOR = '╗' ; DU_LCOR = '╔' 
DL_LCOR = '╚' ; DL_RCOR = '╝' ; DV_LINE = '║'

def main(w):
    draw_workspace(w)
    time.sleep(5)
    pass



def draw_workspace(w):
    global COL ; global ROW
    (ROW, COL) = w.getmaxyx()
    ROW -= 2 ; COL -= 1 


    w.addch(0, 0, DU_LCOR)
    w.addch(0, COL,DU_RCOR)
    w.addch(ROW, 0, DL_LCOR)
    w.addch(ROW, COL, DL_RCOR)

    for x in range(1,COL-1):
        w.addch(0,x, DH_LINE)
        w.addch(ROW,x, DH_LINE)
        w.addch(ROW-2,x, DH_LINE)
    for x in range(1,ROW-1):
        w.addch(x,0, DV_LINE)
        w.addch(x,COL, DV_LINE)
    w.refresh()







curses.wrapper(main)
