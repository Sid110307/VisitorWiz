#!/usr/bin/env python3

__version__ = "1.0.2"

import os
import time
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
from datetime import datetime

import cv2
import face_recognition as ai
import mysql.connector
import numpy as np
from dotenv import load_dotenv
from PIL import Image, ImageTk

load_dotenv()


class VisitorWiz():
    def __init__(self):
        self.database = mysql.connector.connect(
            host="localhost",
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASS"),
            database=os.environ.get("DB_NAME")
        )

        self.color = (0, 0, 255)
        self.stop_video_capture = False

        path = "tests"
        self.images = []
        self.class_names = []

        for f in os.listdir(path):
            if f not in [".gitignore", ".DS_Store"]:
                self.images.append(cv2.imread(os.path.join(path, f)))
                self.class_names.append(os.path.splitext(f)[0])

        self.encode_faces_known = self.find_encodings()
        self.date = datetime.now().strftime("%Y-%m-%d")

        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.init_ui()
        self.move_old_data()

        self.start_attendance()
        self.root.mainloop()

    def move_old_data(self):
        cursor = self.database.cursor(prepared=True)
        select_query = "SELECT * FROM attendance WHERE date != %s"
        insert_query = "INSERT INTO attendance_old (name, face, date, status, attendanceTime) VALUES (%s, %s, %s, %s, %s)"

        cursor.execute(
            select_query, (self.date,))
        result = cursor.fetchall()

        for row in result:
            cursor.execute(
                insert_query,
                (row[1], row[2], row[3], row[4], row[5]))
            self.database.commit()

        cursor.close()

    def find_encodings(self):
        return [ai.face_encodings(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))[0] for img in self.images]

    def mark_attendance(self, encode_face):
        cursor = self.database.cursor(prepared=True)
        select_query = "SELECT * FROM attendance WHERE name = %s AND date = %s"

        cursor.execute(
            select_query,
            (self.name, self.date))
        result = cursor.fetchall()

        if len(result) == 0:
            insert_query = "INSERT INTO attendance (name, face, date, status, attendanceTime) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(
                insert_query,
                (self.name, str(encode_face), self.date, "Present", "datetime.now().strftime('%I:%M %p')"))
            self.database.commit()

            print(f"{self.name} marked present")
            cv2.putText(self.img, f"'{self.name}' is present", (5, 25),
                        cv2.FONT_HERSHEY_PLAIN, 2, self.color, 2)
            time.sleep(1)
        else:
            cv2.putText(self.img, f"'{self.name}' is already present", (5, 25),
                        cv2.FONT_HERSHEY_PLAIN, 2, self.color, 2)

        cursor.close()

    def start_attendance(self):
        if self.stop_video_capture:
            return

        ret, self.img = self.cam.read()

        if not ret or not self.img:
            print("Failed to capture video")
            self.cleanup()

        self.frame = cv2.cvtColor(cv2.resize(
            self.img, (0, 0), None, 0.25, 0.25), cv2.COLOR_BGR2RGB)  # type: ignore

        faces_in_frame = ai.face_locations(self.frame)
        encodings_in_frame = ai.face_encodings(self.frame, faces_in_frame)

        for encode_face, face_location in zip(encodings_in_frame, faces_in_frame):
            matches = ai.compare_faces(
                self.encode_faces_known, encode_face)
            face_distance = ai.face_distance(
                self.encode_faces_known, encode_face)

            match_index = np.argmin(face_distance)

            if matches[match_index]:
                self.name = self.class_names[match_index].capitalize()

                y1, x2, y2, x1 = face_location
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(self.img, (x1, y1), (x2, y2), self.color, 2)

                cv2.putText(self.img, self.name, (x1 + 6, y1 - 6),
                            cv2.FONT_HERSHEY_PLAIN, 2, self.color, 2)

                self.mark_attendance(encode_face)

        img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(
            self.img, cv2.COLOR_BGR2RGB)))
        self.frame_label.imgtk = img_tk  # type: ignore
        self.frame_label.configure(image=img_tk)

        self.frame_label.after(1, self.start_attendance)

    def init_ui(self):
        self.root = tk.Tk()
        self.root.title("VisitorWiz")
        self.root.focus_set()
        self.root.resizable(False, False)
        self.root.bind("q", lambda _: self.cleanup())

        self.frame_label = tk.Label(self.root)
        self.frame_label.grid(row=0, column=0, columnspan=2)

        self.register_button = ttk.Button(
            self.root, text="Register", command=self.register)
        self.register_button.grid(row=1, column=0, sticky="nsew")

    def register(self):
        self.registration = tk.Toplevel(self.root)
        self.registration.title("Register")
        self.registration.focus_set()
        self.registration.resizable(False, False)

        self.stop_video_capture = True
        self.registration.bind("q", lambda _: self.registration.destroy())

        ttk.Label(self.registration, text="Name:").grid(
            row=0, column=0, sticky="e")
        self.name_input = ttk.Entry(self.registration)
        self.name_input.grid(row=0, column=1)

        ttk.Label(self.registration, text="Face:").grid(
            row=1, column=0, sticky="e")
        self.face_input = ttk.Entry(self.registration)
        self.face_input.grid(row=1, column=1)

        self.choose_face_button = ttk.Button(
            self.registration, text="Choose", command=self.choose_face)
        self.choose_face_button.grid(row=1, column=2)

        self.register_button = ttk.Button(
            self.registration, text="Register", command=self.register_face)
        self.register_button.grid(row=2, column=1)

        def continue_video_capture(_):
            self.stop_video_capture = False

        # type: ignore
        self.registration.protocol("WM_DELETE_WINDOW", continue_video_capture)

    def choose_face(self):
        self.face_input.delete(0, tk.END)
        self.face_input.insert(0, filedialog.askopenfilename())

    def register_face(self):
        self.reg_name = self.name_input.get().capitalize()
        self.reg_face = self.face_input.get()

        if self.reg_name == "" or self.reg_face == "":
            messagebox.showerror("Error", "Please fill in all fields")
            return

        face_img = cv2.imread(self.reg_face)
        cv2.imwrite(f"tests/{self.reg_name}.jpg", face_img)

        self.encode_faces_known.append(
            ai.face_encodings(face_img)[0])
        self.class_names.append(self.reg_name)

        messagebox.showinfo("Success", "Successfully registered")
        self.registration.destroy()

    def cleanup(self):
        self.cam.release()

        self.root.destroy()
        cv2.destroyAllWindows()

        if self.database.is_connected():
            self.database.close()

        print("Bye")
        os._exit(0)


if __name__ == "__main__":
    VisitorWiz()
