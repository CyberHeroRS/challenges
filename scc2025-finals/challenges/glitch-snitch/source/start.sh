#!/bin/bash

echo $FLAG > /flag.txt

cd /app/frontend
npm start &

cd /app/backend
npm start &

wait