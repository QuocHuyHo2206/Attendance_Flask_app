import sqlite3
from flask import make_response, jsonify
from datetime import datetime, timedelta

class teacher_handler():
    def __init__(self):
        #Connection establishment code
        try:
            # self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
            # self.con.row_factory = sqlite3.Row
            # self.cur = self.con.cursor()
            print("Connection successful")        
        except:
            print("Some error")

    #login
    def teacher_login_handler(self, data):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        self.cur.execute(f"SELECT * FROM teachers where email = '{data['email']}' and password = '{data['password']}'")
        teacher = self.cur.fetchone()
        self.con.close()
        if teacher:
            teacher_id = teacher[0]
            teacher_name = teacher[1]
            teacher_email = teacher[2]
            return make_response(jsonify({
                "message": "login successfully",
                "teacher_id": teacher_id,
                "teacher_name": teacher_name,
                "teacher_email": teacher_email
        }), 200)
        else:
            return make_response(jsonify({"message":"login fail"}), 404)
        
    #"2025-10-15 08:30:00"
    def add_new_session_handler(self, data):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        self.cur.execute(f"INSERT INTO sessions(title, numberofstudent, startdate, enddate, teacher_id) values( '{data['title']}', 0, '{data['startdate']}', '{data['enddate']}', {data['teacher_id']})")
        self.con.commit()
        session_id = self.cur.lastrowid
        self.con.close()
        return make_response(jsonify({
        "message": "create successfully",
        "session_id": session_id
        }), 200)

    #title, start, end
    def update_session_handler(self, id, data):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        query = "UPDATE sessions set "
        for key in data:
            query += f"{key}='{data[key]}',"
        query = query[:-1] + f"WHERE id = {id}"
        self.cur.execute(query)
        if self.cur.rowcount > 0:
            self.con.commit()
            self.con.close()
            return make_response(jsonify({"message":"session updated successfully"}), 200)
        else:
            self.con.close()
            return make_response(jsonify({"message":"Nothing to update"}), 202)
        
    #api lấy student danh sách students để có thể thêm attendance
    # def add_student_to_session_handler(self, data):
    #     self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
    #     self.con.row_factory = sqlite3.Row
    #     self.cur = self.con.cursor()

    #     query = """
    #         SELECT 1 FROM attendance
    #         WHERE session_id = ? AND student_id = ? """
    #     self.cur.execute(query, (data['session_id'], data['student_id']))
    #     exists = self.cur.fetchone()
    #     if exists:
    #         self.con.close()
    #         return make_response(jsonify({"error": "Student already added to this session"}), 400)

    #     self.cur.execute(f"INSERT INTO attendance(session_id, student_id, status, checkin_time) values({data['session_id']}, {data['student_id']}, 'absent', NULL)")
    #     self.con.commit()
    #     self.cur.execute(f"UPDATE sessions set numberofstudent = numberofstudent + 1 where id = {data['session_id']}")
    #     self.con.commit()
    #     self.con.close()
    #     return make_response(jsonify({"message":"add student successfully"}), 200)

    def add_student_to_session_handler(self, data):
        try:
            con = sqlite3.connect('attendance_app.db', check_same_thread=False)
            con.row_factory = sqlite3.Row
            cur = con.cursor()

            cur.execute(
            "SELECT 1 FROM attendance WHERE session_id = ? AND student_id = ?",
            (data['session_id'], data['student_id']))   

            if cur.fetchone():
                return make_response(jsonify({"error": "Student already added to this session"}), 400)

            cur.execute(
            "INSERT INTO attendance(session_id, student_id, status, checkin_time) VALUES (?, ?, 'absent', NULL)",
            (data['session_id'], data['student_id']))

            cur.execute(
            "UPDATE sessions SET numberofstudent = COALESCE(numberofstudent, 0) + 1 WHERE id = ?",
            (data['session_id'],))

            con.commit()
            return make_response(jsonify({"message": "add student successfully"}), 200)

        except sqlite3.OperationalError as e:
            print("SQLite error:", e)
            return make_response(jsonify({"error": f"Database error: {str(e)}"}), 500)

        finally:
            try:
                con.close()
            except:
                pass
    
    #get all student
    def get_all_student_handler(self):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        query = "Select id, name, email from students"
        self.cur.execute(query)
        students = self.cur.fetchall()

        self.cur.execute("Select * from attendance")
        attendances = self.cur.fetchall()

        result = list()
        high_attendance_count = 0
        low_attendance_count = 0

        for item in students:
            stu_id = item['id']
            num_present = 0
            total_sessions = 0
            for atd in attendances:
                if atd['student_id'] == stu_id:
                    total_sessions += 1
                    if atd["status"].lower() == "present":
                        num_present += 1
            
            attendance_rate = (num_present / total_sessions) * 100 if total_sessions > 0 else 0

            if attendance_rate >= 90: high_attendance_count += 1
            elif attendance_rate < 80: low_attendance_count += 1

            result.append({
                "id": item["id"],
                "name": item["name"],
                "email": item["email"],
                "number_of_present": num_present,
                "total_attendance_sessions": total_sessions,
                "attendance_rate": round(attendance_rate, 1)})
            
        payload = {
            "list_of_student" : result,
            "high_attendance" : high_attendance_count,
            "need_attention" : low_attendance_count
        }

        #result = [dict(row) for row in self.cur.fetchall()]
        self.con.close()
        return make_response(jsonify(payload), 200)
    
    #get all session
    def get_all_session_handler(self, startdate):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        query = "SELECT * FROM sessions WHERE DATE(startdate) = ? ORDER BY startdate ASC"
        self.cur.execute(query, (startdate,))
        list_of_session = [dict(row) for row in self.cur.fetchall()]

        for session in list_of_session:
            session_id = session['id']
            query = "SELECT status FROM attendance WHERE session_id = ?"
            self.cur.execute(query, (session_id,))
            statuses = self.cur.fetchall()

            num_present = 0
            num_absent = 0

            for item in statuses:
                if item['status'] == 'present':
                    num_present += 1
                else:
                    num_absent += 1

            total = num_present + num_absent
            if total > 0:
                percentage_of_attendance = (num_present / total) * 100
            else:
                percentage_of_attendance = 0

            session['percentage_of_attendance'] = round(percentage_of_attendance, 1)
            
        self.con.close()
        return make_response(jsonify({"payload": list_of_session}), 200)

    
    #get number of present/absent theo session_id
    def get_num_stu_followed_categories_endpoint(self, id):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        query = f"Select status from attendance where session_id = {id}"
        self.cur.execute(query)
        statuses = self.cur.fetchall()
        self.con.close()
        num_present = 0
        num_absent = 0
        for item in statuses:
            if item['status'] == 'present':
                num_present += 1
            elif item['status'] == 'absent':
                num_absent += 1
        return make_response(jsonify({
            'num_present': num_present, 
            'num_absent': num_absent, 
            'number_of_students': (num_present + num_absent)}))
    
    #get teacher information by id
    def get_teacher_information_handler(self, id):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        query = f"Select id, name, email, password from teachers where id = {id}"
        self.cur.execute(query)
        teacher = self.cur.fetchone()

        if teacher:
            teacher_result = dict(teacher)
            return make_response(jsonify(teacher_result), 200)
        else:
            return make_response(jsonify({"message": f"Can not find teacher with {id}"}), 404)
        
    # get session attendance status by session id
    def get_session_attendance_status_handler(self, id):
        self.con = sqlite3.connect('attendance_app.db', check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        self.cur.execute(f"Select * from sessions where id = {id}")
        session = self.cur.fetchone()
        if not session: 
            return make_response(jsonify({"message" : f"Can not find session with {id}"}), 404)
        
        result = list()
        number_of_student = session["numberofstudent"]
        if number_of_student == 0:
            return make_response(jsonify({
                "message" : f"Please add student to session",
                "number_of_student": number_of_student}), 200)

        query = f"Select student_id, status, checkin_time from attendance where session_id = {session['id']}"
        self.cur.execute(query)
        temp_list = self.cur.fetchall()

        for item in temp_list:
            self.cur.execute(f"Select id, name, email from students where id = {item['student_id']}")
            stu = self.cur.fetchone()
            result.append({
                "student_id": stu["id"],
                "student_name": stu["name"],
                "status": item["status"],
                "checkin_time": item["checkin_time"]
            })
            
        payload = {
            "number_of_student": number_of_student,
            "student_attendance_status": result
        }

        return make_response(jsonify({"payload": payload}), 200)
