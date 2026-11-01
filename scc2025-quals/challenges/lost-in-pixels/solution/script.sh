#!/bin/sh

grep -R "Data write" annotations | sed 's/.*Data write: //' | xargs > file
