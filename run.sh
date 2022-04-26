#!/usr/bin/env sh

pip list | grep -F opencv >> /dev/null

if [ $? -ne 0 ]; then
	pip install opencv-python face_recognition mysql-connector-python pillow python-dotenv >> /dev/null
fi

python3 src/main.py
