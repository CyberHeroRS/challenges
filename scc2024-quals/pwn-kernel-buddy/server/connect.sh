#!/bin/sh

socat file:`tty`,raw,echo=0 tcp:127.0.0.1:1337
