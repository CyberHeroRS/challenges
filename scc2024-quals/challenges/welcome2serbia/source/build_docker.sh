#!/bin/bash
docker build -t welcome2serbia .
docker run --rm -d -p 3500:3500 --name welcome2serbia welcome2serbia
