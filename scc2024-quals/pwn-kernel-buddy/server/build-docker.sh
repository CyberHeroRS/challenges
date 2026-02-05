#!/bin/bash
sudo docker build --network host --tag=kernel_pwn .
sudo docker run -d -p 1337:1337 --rm --name=kernel_pwn kernel_pwn
