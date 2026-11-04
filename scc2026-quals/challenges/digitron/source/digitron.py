#!/usr/bin/env python3

import curses
from curses import wrapper
from math import *

hyp = hypot
rnd = round
fac = factorial

funcs = [
    ["log", "exp", "pow", "rnd"],
    ["asin", "acos", "atan", "sqrt"],
    ["sin", "cos", "tan", "hyp"],
    ["abs", "gcd", "fac", "del"],
    ["(", ")", ".", ","],
    ["7", "8", "9", "+"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "*"],
    ["C", "0", "=", "/"]
]

banner = [
    "  ___  _      _ _                ",
    " |   \\(_)__ _(_) |_ _ _ ___ _ _  ",
    " | |) | / _` | |  _| '_/ _ \\ ' \\ ",
    " |___/|_\\__, |_|\\__|_| \\___/_||_|",
    "        |___/                    "
]

cx, cy = 0, 0
MINW = 40
MINH = 24
expr = ""


def print_banner(stdscr):
    h, w = stdscr.getmaxyx()
    x = w // 2 - len(banner[0]) // 2
    y = h // 2 - 6 - len(banner)

    for y_off in range(len(banner)):
        stdscr.addstr(y + y_off, x, banner[y_off])


def print_funcs(stdscr):
    h, w = stdscr.getmaxyx()

    x = w // 2 - 10
    y = h // 2 - 3
    y_off = 0
    stdscr.addstr(y + y_off - 3, x - 1, "┌" + "─" * 20 + "┐")
    stdscr.addstr(y + y_off - 2, x - 1, "│" + expr[-20:].rjust(20) + "│")
    stdscr.addstr(y + y_off - 1, x - 1, "├" + "─" * 20 + "┤")
    for func in funcs:
        stdscr.addstr(y + y_off, x - 1, "│")
        for x_off in range(4):
            if cx == x_off and cy == y_off:
                stdscr.addstr(y + y_off, x + x_off * 5, func[x_off].center(5), curses.A_REVERSE)
            else:
                if func[x_off] == "del":
                    stdscr.addstr(y + y_off, x + x_off * 5, func[x_off].center(5), curses.color_pair(1))
                else:
                    stdscr.addstr(y + y_off, x + x_off * 5, func[x_off].center(5))
        stdscr.addstr(y + y_off, x + 20, "│")
        y_off += 1
    stdscr.addstr(y + y_off, x - 1, "└" + "─" * 20 + "┘")


def controls(key):
    global cx, cy, expr

    if key == curses.KEY_UP:
        if cy > 0:
            cy -= 1
    elif key == curses.KEY_DOWN:
        if cy < len(funcs) - 1:
            cy += 1
    elif key == curses.KEY_LEFT:
        if cx > 0:
            cx -= 1
    elif key == curses.KEY_RIGHT:
        if cx < len(funcs[0]) - 1:
            cx += 1
    elif key == ord('\n'):
        ch = funcs[cy][cx]
        if ch in "0123456789+-/*.,()":
            expr += ch
        elif ch == '=':
            try:
                expr = str(eval(expr))
            except:
                expr = 'Error'
        elif ch == 'C':
            expr = ''
        elif ch == "del":
            expr = expr[:-1]
        else:
            expr += ch + '('


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    stdscr.keypad(True)
    curses.curs_set(0)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    if h < MINH or w < MINW:
        stdscr.addstr(
            0, 0, "Terminal is too small! Min width is 40 and min height is 24!")
    else:
        print_banner(stdscr)
        print_funcs(stdscr)
    curses.doupdate()
    while True:
        key = stdscr.getch()
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        if h < MINH or w < MINW:
            stdscr.addstr(
                0, 0, "Terminal is too small! Min width is 40 and min height is 20!")
        else:
            if key == ord('q') or key == ord('Q'):
                break
            controls(key)
            print_banner(stdscr)
            print_funcs(stdscr)
        stdscr.refresh()


wrapper(main)
