import sqlite3
from flask import make_response, jsonify
from datetime import datetime, timedelta
import os
import numpy as np
from PIL import Image
import face_recognition
from datetime import datetime

class student_handler():
    def __init__(self):
        #Connection establishment code
        try:
            # self.con = sqlite3.connect('attendance_app.db')
            # self.con.row_factory = sqlite3.Row
            # self.cur = self.con.cursor()
            print("Connection successful")        
        except:
            print("Some error")

    #login
    def student_login_handler(self, data):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        self.cur.execute(f"SELECT * FROM students where email='{data['email']}' and password = '{data['password']}' ")
        student = self.cur.fetchone()
        self.con.close()
        if student:
            student_id = student[0]
            student_name = student[1]
            student_email = student[2]
            return make_response(jsonify({
                "message": "login successfully",
                "student_id": student_id,
                "student_name": student_name,
                "student_email": student_email
            }), 200)

        else:
            return make_response(jsonify({"message":"login fail"}), 404)
        
    #register
    def student_register_handler(self, data):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        os.makedirs('images', exist_ok=True)

        name = data.form['name']
        email = data.form['email']
        password = data.form['password']
        file = data.files['image']

        ext = os.path.splitext(file.filename)[1] #file.filename trả về tên gốc của file, hàm splitext tách phần tên và phần mở rộng
        image_path = os.path.join('images', f'{name}{ext}') #join đảm bảo đường dẫn đúng định dạng
        file.save(image_path)

        image = face_recognition.load_image_file(image_path) #numPy array
        encodings = face_recognition.face_encodings(image) # vector encoding list (128 float value/value)
        if len(encodings) == 0:
            return make_response({"error": "unrecognized"}, 400)
        
        encoding = encodings[0]
        encoding_bytes = encoding.tobytes()
        query = """ INSERT INTO students(name, email, password, encoding) VALUES (?, ?, ?, ?) """
        self.cur.execute(query, (name, email, password, encoding_bytes))

        self.con.commit()
        self.con.close()

        return make_response(jsonify({"message":"register successfully"}), 200)
    
    #Compare
    def student_take_attendance_handler(self, data):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        file = data.files['image']

        img = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(img)
        if len(encodings) == 0:
            self.con.close()
            return make_response(jsonify({"message": "unrecognized"}), 400)
        
        attendance_encoding = encodings[0]
        student_id = data.form['student_id']
        session_id = data.form['session_id']

        self.cur.execute("SELECT id, encoding FROM students WHERE id = ?", (student_id,))
        student = self.cur.fetchone()
        if not student:
            self.con.close()
            return make_response(jsonify({"message": "student not found"}), 404)

        known_encoding = np.frombuffer(student['encoding'], dtype=np.float64)
        distance = face_recognition.face_distance([known_encoding], attendance_encoding)[0]

        if distance < 0.5:
            self.cur.execute(
                "SELECT status, checkin_time FROM attendance WHERE session_id = ? AND student_id = ?", (session_id, student_id))
            existing = self.cur.fetchone()

            if existing:
                if existing['status'] == 'present':
                    self.con.close()
                    return make_response(jsonify({
                        'message': 'already checked in',
                        'distance': float(distance),
                        'checkin_time': existing['checkin_time']}), 200)
                else:
                    checkin_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.cur.execute(
                        "UPDATE attendance SET status = 'present', checkin_time = ? WHERE session_id = ? AND student_id = ?",
                        (checkin_time, session_id, student_id))
                    self.con.commit()
                    self.con.close()
                    return make_response(jsonify({
                        'message': 'recognized',
                        'distance': float(distance),
                        'checkin_time': checkin_time}), 200)
            else:
                self.con.close()
                return make_response(jsonify({
                'message': 'attendance record not found',
                'student_id': student_id,
                'session_id': session_id}), 404)

        self.con.close()
        return make_response(jsonify({
            'message': 'unrecognized',
            'distance': float(distance)}), 400)

    
    #get session infomation by student_id
    def get_session_information_handler(self, id, startdate):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        query = """
            SELECT 
            a.status,
            a.checkin_time,
            t.name AS teacher_name,
            s.id AS session_id,
            s.title,
            s.startdate,
            s.enddate
        FROM attendance a
        JOIN sessions s ON a.session_id = s.id
        JOIN teachers t ON s.teacher_id = t.id
        WHERE a.student_id = ? AND DATE(s.startdate) = ?"""

        self.cur.execute(query, (id, startdate))
        result = [dict(row) for row in self.cur.fetchall()]
        self.con.close()

        return make_response(jsonify(result))
    
    #get student information by student_id
    def get_student_information_handler(self, id):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        query = f"Select id, name, email, password from students where id = {id}"
        self.cur.execute(query)
        student = self.cur.fetchone()
        self.con.close()

        if student:
            student_result = dict(student)
            return make_response(jsonify(student_result), 200)
        else:
            return make_response(jsonify({"message": f"Can not find student with {id}"}), 404)