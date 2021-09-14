import asyncio
import curses
import time
from itertools import cycle, count
from random import choice, randint


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break
                
            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, sleep_time, symbol='*'):
    for i in range(sleep_time):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)
    while True:
        for i in range(20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)

        for i in range(4):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for i in range(2):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)

        for i in range(2):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)



def draw(canvas):

    TIC_TIMEOUT = 0.1

    with open('frames/rocket_frame_1.txt', 'r') as f:
        rocket_frame_1 = f.read()
    with open('frames/rocket_frame_2.txt', 'r') as f:
        rocket_frame_2 = f.read()
    rocket_width = 5
    rocket_height = 9

    canvas.border()
    curses.curs_set(False)

    max_raw, max_column = canvas.getmaxyx()
    coroutines = []
    for _ in range (100):
        symbol = choice(['*', ':', '+', '.'])
        row = randint(3, max_raw)
        column  = randint(3, max_column)

        sleep_time = randint(0,15)
        star_coroutine = blink(canvas, row-2, column-2, sleep_time, symbol)
        coroutines.append(star_coroutine)

    fire_coroutine = fire(canvas, max_raw - 2, max_column/2)
    coroutines.append(fire_coroutine)

    rocket_frames = [rocket_frame_1, rocket_frame_1,]
    rocket_iterator = cycle(rocket_frames)

    for tic in count(0):
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if not coroutines:
            break
        time.sleep(TIC_TIMEOUT)
        if tic//10 % 2 == 0:
            next(rocket_iterator)
        draw_frame(
            canvas,
            (max_raw - rocket_height) / 2,
            (max_column - rocket_width) / 2,
            rocket_iterator
        )
        canvas.refresh()


  
if __name__ == '__main__':

    curses.update_lines_cols()
    curses.wrapper(draw)
