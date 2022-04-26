#!/usr/bin/env python3

import base64
import os
import re
import sys
from io import BytesIO
import tkinter as tk

import cv2
import mysql.connector as mysql
import numpy as np
from dotenv import load_dotenv
from PIL import Image, ImageTk

load_dotenv()


class VisitorWiz:
    database = mysql.connect(
        host="localhost",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database=os.environ.get("DB_NAME")
    )

    color = (0, 0, 255)

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            f"{cv2.data.haarcascades}/haarcascade_frontalface_default.xml")

        self.init_ui()
        self.cursor = self.database.cursor()

        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 640)
        self.cam.set(4, 480)

        self.show_frames()

        # Train the model using the sql database and save it to a file
        self.train_model()

        self.root.mainloop()
        self.cam.release()
        cv2.destroyAllWindows()

    def init_ui(self):
        self.root = tk.Tk()
        self.root.title("VisitorWiz")
        self.root.geometry("640x480")

        self.label = tk.Label(self.root)
        self.label.grid(row=0, column=0)

    def detect_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.25,
            minNeighbors=5,
            minSize=(20, 20)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), self.color, 2)
            face_gray = gray[y:y+h, x:x+w]
            face_color = frame[y:y+h, x:x+w]

    def show_frames(self):
        ret, frame = self.cam.read()

        if not ret:
            print("Can't receive frame. Exiting...")
            exit(1)

        self.detect_face(frame)

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        self.cursor.execute(
            f"INSERT INTO faces (face) VALUES (\"{base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode('utf-8')}\")")
        self.database.commit()

        self.label.imgtk = imgtk  # type: ignore
        self.label.configure(image=imgtk)
        self.label.after(1, self.show_frames)

    def train_model(self):
        # self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.train(
            self.get_images()[0], np.array(self.get_images()[1]))
        self.recognizer.write(os.environ.get("TRAINED_MODEL"))


if __name__ == "__main__":
    label_count = 0

    VisitorWiz()


# region OLD CODE:

"""
Open the recognized face as an image

cursor.execute("SELECT face FROM faces")

for (face,) in cursor:
    img = Image.open(BytesIO(base64.b64decode(face)))
    img.show()
"""

# endregion
