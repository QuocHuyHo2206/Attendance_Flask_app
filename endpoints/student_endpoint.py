from app_init import app
from flask import request
from handlers.student_handler import student_handler

stu = student_handler()

@app.route("/api/student/login", methods=['POST'])
def student_login_endpoint():
    return stu.student_login_handler(request.form)

@app.route("/api/student/register", methods=['POST'])
def student_register_endpoint():
    return stu.student_register_handler(request)

@app.route("/api/student/takeattendance", methods=['POST'])
def student_take_attendance_endpoint():
    return stu.student_take_attendance_handler(request)

@app.route("/api/student/getsessioninformation/<id>/<startdate>")
def get_session_information_endpoint(id, startdate):
    return stu.get_session_information_handler(id, startdate)

@app.route("/api/student/getstudentinformation/<id>")
def get_student_information_endpoint(id):
    return stu.get_student_information_handler(id)