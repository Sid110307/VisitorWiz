#!/usr/bin/env bash

echo -en "\033[36mResolving dependencies... \033[0m"
pip install cmake opencv-python face_recognition mysql-connector-python pillow python-dotenv >> /dev/null
echo -e "\033[1;32mDone.\033[0m"

python3 src/main.py
