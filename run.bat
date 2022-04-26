if ! pip list | grep -F opencv ; then
	pip install opencv-python face_recognition mysql-connector-python pillow python-dotenv >nul
fi

python3 src/main.py
