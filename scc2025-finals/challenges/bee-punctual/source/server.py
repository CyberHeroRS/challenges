#!/usr/local/bin/python

from string import punctuation

pool = (set(punctuation) | {"e"}) - {"\\"}

code = input("Code pls: ")

assert len(code) < 1500, "Code too long"
assert all(c in pool for c in code), "Invalid character in code"

eval(eval(code, {"__builtins__": {"e": lambda e: e()}}, {}), {"__builtins__": None}, {})
