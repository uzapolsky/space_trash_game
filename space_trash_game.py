import asyncio
import curses
import time
from itertools import cycle, count
from random import choice, randint


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def get_frame_size(text):
    """Calculate size of multiline text fragment,
    return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of
    drawing if negative=True is specified."""

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

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def fire(canvas, start_row, start_column,
               rows_speed=-0.3, columns_speed=0):
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


async def blink(canvas, row, column, symbol='*'):
    sleep_time = randint(0, 30)
    for _ in range(sleep_time):
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
    while True:

        for _ in range(4):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for _ in range(2):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)

        for _ in range(2):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for _ in range(20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)


def is_inside(canvas, row, column, height, width):
    rows_number, columns_number = canvas.getmaxyx()
    y_inside = 0 < row < rows_number - height
    x_inside = 0 < column < columns_number - width
    return y_inside and x_inside


def draw(canvas):

    tic_timeout = 0.1

    with open('frames/rocket_frame_1.txt', 'r') as f:
        rocket_frame_1 = f.read()
    with open('frames/rocket_frame_2.txt', 'r') as f:
        rocket_frame_2 = f.read()
    rocket_height, rocket_width = get_frame_size(rocket_frame_1)

    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    coroutines = []
    star_positions = []
    for _ in range(200):
        symbol = choice(['*', ':', '+', '.'])

        bottom_indent = 1
        top_indent = 2
        row = randint(bottom_indent, height-top_indent)
        column = randint(bottom_indent, width-top_indent)
        while (row, column) in star_positions:
            row = randint(bottom_indent, height-top_indent)
            column = randint(bottom_indent, width-top_indent)

        star_positions.append((row, column))
        star_coroutine = blink(canvas, row, column, symbol)
        coroutines.append(star_coroutine)

    center_column = width/2
    fire_coroutine = fire(canvas, height - top_indent, center_column)
    coroutines.append(fire_coroutine)

    rocket_frames = [rocket_frame_1, rocket_frame_2]
    rocket_iterator = cycle(rocket_frames)
    rocket_row = (height - rocket_height) / 2
    rocket_column = (width - rocket_width) / 2

    for tic in count(0):
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if not coroutines:
            break

        if tic % 2 == 0:
            rocket_frame = next(rocket_iterator)

        rows_direction, columns_direction, space_pressed =  \
            read_controls(canvas)

        inside = is_inside(
            canvas,
            rocket_row + rows_direction,
            rocket_column + columns_direction,
            rocket_height,
            rocket_width)

        if inside:
            rocket_row += rows_direction
            rocket_column += columns_direction

        draw_frame(
            canvas,
            rocket_row,
            rocket_column,
            rocket_frame
        )
        canvas.refresh()

        draw_frame(
            canvas,
            rocket_row,
            rocket_column,
            rocket_frame,
            negative=True
        )
        time.sleep(tic_timeout)


if __name__ == '__main__':

    curses.update_lines_cols()
    curses.wrapper(draw)
