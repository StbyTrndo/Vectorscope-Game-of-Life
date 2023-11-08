# The game of life

import screennorm
import keyboardcb
import keyleds
import vectoros
import timer
import asyncio
from vos_state import vos_state
import colors
import random
import vos_debug


screen=screennorm.ScreenNorm()   # get the screen

board = []
oldboard = []

random.seed()

exit_flag=False    # don't exit
tid=None           # timer ID
timer_rate=5      # timer rate (ticks; see vos_launch.py for multiplier)
rows = 7
cols = 15
cycle_flag = True

def presets(x):

    global board, rows, cols

    #clear board
    board = []
    for i in range(rows): board.append([0] * cols)

    center_y = rows // 2
    center_x = cols // 2

    live_cells_relative = []

    # R-Pentomino
    if x == 'b':

        live_cells_relative = [
            [0,0],
            [-1,0],
            [-1,1],
            [1,0],
            [0,-1]
        ]

    # Glider
    if x == 'c':

        live_cells_relative = [
            [-1,0],
            [0,0],
            [1,0],
            [1,1],
            [0,2]
        ]

    # Diehard
    if x == 'd':

        live_cells_relative = [
            [0,-3],
            [0,-2],
            [1,-2],
            [-1,3],
            [1,3],
            [1,4],
            [1,2]
        ]

    for cell in live_cells_relative:
        board[cell[0]+center_y][cell[1]+center_x] = 1

    del live_cells_relative

def init_board():
    global board, rows, cols, oldboard
    board = []
    row = []

    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"Init Board:")

    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(random.randint(0,1))
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,str(row))
        board.append(row)
        oldboard.append(row)

#update the board
def board_update():
    global board, oldboard

    # create a copy of the board that is unlinked from the global board variable
    newboard = []
    for i in range(rows): newboard.append([0] * cols)
    for i in range(rows):
        for j in range(cols):
            newboard[i][j] = board[i][j]

    for i in range(rows):
        for j in range(cols):

            #calculate neighbor sum using toroidal conditions
            total = (board[i][(j-1)%cols] +
                         board[i][(j+1)%cols] +
                         board[(i-1)%rows][j] +
                         board[(i+1)%rows][j] +
                         board[(i-1)%rows][(j-1)%cols] +
                         board[(i-1)%rows][(j+1)%cols] +
                         board[(i+1)%rows][(j-1)%cols] +
                         board[(i+1)%rows][(j+1)%cols])

            if board[i][j] == 1:
                if (total < 2) or (total > 3):
                    newboard[i][j] = 0
            else:
                if total == 3:
                    newboard[i][j] = 1

    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,str("New Board:"))
    for row in newboard:
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,str(row))

    if (newboard == board or newboard == oldboard) and cycle_flag == True:
        init_board()
    else:
        oldboard = board
        board = newboard

    del newboard

# print screen and increment the game
def next():
    global board

    x=0
    y=0

    #print the board
    for row in board:
        display_row=""
        for cell in row:
            if cell == 1:
                display_row = display_row+"X"
            elif cell == 0:
                display_row = display_row+" "
            else:
                display_row = display_row+str(cell)
        
        screen.text(x,y,display_row,colors.rgb(random.randint(50,255), random.randint(50,255), random.randint(50,255)) ,colors.BLACK)
        y+=30

    board_update()

# if you change the timeout we have to kill the old timer and make a new one
def update_timer():
    global tid, timer_rate
    timer.Timer.remove_timer(tid)
    tid=timer.Timer.add_timer(timer_rate,next)  # change over

# Joystick
# Up is delay up, Down is delay down
# Right is next, and Left toggles the cycle_flag
def joycb(key):
    global timer_rate, cycle_flag
    if (key==keyleds.JOY_UP):
        timer_rate+=5
        if timer_rate>200:
            timer_rate=200
        update_timer()
    if (key==keyleds.JOY_DN):
        timer_rate-=5
        if timer_rate<=0:
            timer_rate=1
        update_timer()
    if (key==keyleds.JOY_RT):
        next()
    if (key==keyleds.JOY_LF):
        cycle_flag = not cycle_flag
    if (key==keyleds.KEY_A):
        cycle_flag = True
        init_board()
    if (key==keyleds.KEY_B):
        cycle_flag = False
        presets('b')
    if (key==keyleds.KEY_C):
        cycle_flag = False
        presets('c')
    if (key==keyleds.KEY_D):
        cycle_flag = False
        presets('d')



    
def menu(key):						# menu -bail out
    global exit_flag
    exit_flag=True





async def vos_main():
    global exit_flag, board, tid, timer_rate
    init_board()
    # we treat the joystick like any other key here
    keys=keyboardcb.KeyboardCB({keyleds.KEY_MENU: menu, keyleds.JOY_UP: joycb, keyleds.JOY_DN: joycb, keyleds.JOY_RT: joycb, keyleds.JOY_LF: joycb, keyleds.KEY_A: joycb, keyleds.KEY_B: joycb, keyleds.KEY_C: joycb, keyleds.KEY_D: joycb})
    tid=timer.Timer.add_timer(timer_rate,next)
    # prime it
    next()
    # do nothing... everything is on keyboard and timer
    while exit_flag==False:
        await asyncio.sleep_ms(500)
# stop listening for keys
    keys.detach()
    timer.Timer.remove_timer(tid)
    exit_flag=False  # next time

    vos_state.show_menu=True  # tell menu to wake up
    


if __name__=="__main__":
    import vectoros
    vectoros.run()
