#!/usr/local/bin/python

import os

WIDTH = 60

LINES = """  _  __     _ _        _      _           
 | |/ /__ _| | |___  _| |__ _| |_ ___ _ _ 
 | ' </ _` | | / / || | / _` |  _/ _ \\ '_|
 |_|\\_\\__,_|_|_\\_\\\\_,_|_\\__,_|\\__\\___/_|  
 """.splitlines()

print("#" * (WIDTH + 6))
for line in LINES:
    print("## " + line.center(WIDTH) + " ##")
print("## " + "Welcome to very powerful calculator!".center(WIDTH) + " ##")
print("## " + "You can type any expression and it will be eval()uated!".center(WIDTH) + " ##")
print("## " + "Written in Python 3.11.4".center(WIDTH) + " ##")
print("## " + " " * WIDTH + " ##")
print("#" * (WIDTH + 6))
print("[*] module 'os' is imported!")

while True:
    try:
        print()
        exp = input(">> ")
        res = eval(exp)

        print("Result: {}".format(res))
    except KeyboardInterrupt:
        break
    except EOFError:
        break
    except:
        print("Something went wrong :(")
