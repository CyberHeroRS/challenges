#!/usr/bin/env sh

FLAG_VALUE="$FLAG"
unset FLAG

python3 /app/app.py "$FLAG_VALUE"
