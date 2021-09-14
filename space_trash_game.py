import asyncio
import curses
import time


async def blink(canvas, row, column, symbol='*'):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    await asyncio.sleep(0)

    canvas.addstr(row, column, symbol)
    await asyncio.sleep(0)

    canvas.addstr(row, column, symbol, curses.A_BOLD)
    await asyncio.sleep(0)

    canvas.addstr(row, column, symbol)
    await asyncio.sleep(0)


def draw(canvas):

    coroutine = blink(canvas, 5, 5)
    for i in range (4):
        (coroutine.send(None))
        canvas.refresh() 
        time.sleep(0.5)
    time.sleep(3)
  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
