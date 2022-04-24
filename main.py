#!/usr/bin/env python3

__version__ = "1.0.0"

from datetime import datetime
import time
import face_recognition as ai
import cv2
import mysql.connector
import numpy as np
import tkinter as tk
import sys
import os
from dotenv import load_dotenv
load_dotenv()


def move_old_data():
    cursor = database.cursor()
    cursor.execute(
        f"SELECT * FROM attendance WHERE date != '{datetime.now().strftime('%Y-%m-%d')}'")
    result = cursor.fetchall()

    for row in result:
        cursor.execute(
            f"INSERT INTO attendance_old (name, face, date, status, attendanceTime) VALUES ('{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}')")
        database.commit()


def find_encodings(images):
    return [ai.face_encodings(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))[0] for img in images]


def mark_attendance(img, name, encode_face):
    cursor = database.cursor()
    date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        f"SELECT * FROM attendance WHERE name = '{name}' AND date = '{date}'")
    result = cursor.fetchall()

    if len(result) == 0:
        cursor.execute(
            f"INSERT INTO attendance (name, face, date, status, attendanceTime) VALUES ('{name}', '{encode_face}', '{date}', 'Present', '{datetime.now().strftime('%H:%M:%S')}')")
        database.commit()
        cv2.putText(img, f"'{name}' is present", (5, 25),
                    cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
        time.sleep(1)
    else:
        cv2.putText(img, f"'{name}' is already present", (5, 25),
                    cv2.FONT_HERSHEY_PLAIN, 2, color, 2)


def main():
    move_old_data()

    while True:
        ret, img = cam.read()

        if not ret:
            print("Failed to capture video")
            raise KeyboardInterrupt

        frame = cv2.cvtColor(cv2.resize(
            img, (0, 0), None, 0.25, 0.25), cv2.COLOR_BGR2RGB)  # type: ignore

        faces_in_frame = ai.face_locations(frame)
        encodings_in_frame = ai.face_encodings(frame, faces_in_frame)

        for encode_face, face_location in zip(encodings_in_frame, faces_in_frame):
            matches = ai.compare_faces(encode_faces_known, encode_face)
            face_distance = ai.face_distance(encode_faces_known, encode_face)

            match_index = np.argmin(face_distance)

            if matches[match_index]:
                name = class_names[match_index].capitalize()

                y1, x2, y2, x1 = face_location
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

                cv2.putText(img, name, (x1 + 6, y1 - 6),
                            cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

                mark_attendance(img, name, encode_face)

        cv2.imshow("VisitorWiz", img)
        if cv2.waitKey(1) == ord('q'):
            raise KeyboardInterrupt


if __name__ == "__main__":
    print("Setting up...", end=" ")

    database = mysql.connector.connect(
        host="localhost",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database=os.environ.get("DB_NAME")
    )

    color = (0, 0, 255)

    path = "tests"
    images = []
    class_names = []

    for f in os.listdir(path):
        if f not in [".gitignore", ".DS_Store"]:
            images.append(cv2.imread(os.path.join(path, f)))
            class_names.append(os.path.splitext(f)[0])

    encode_faces_known = find_encodings(images)

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    print("Done.")

    try:
        main()
    except KeyboardInterrupt:
        cam.release()
        cv2.destroyAllWindows()

        print("Bye")
