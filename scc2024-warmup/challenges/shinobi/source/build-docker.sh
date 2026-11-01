#!/bin/sh
docker build -t shinobi .
docker run -d -p 3000:3000 shinobi
