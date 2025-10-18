from app_init import app
from flask import request
from handlers.teacher_handler import teacher_handler

tea = teacher_handler()

@app.route("/api/teacher/login", methods=['POST'])
def teacher_login_endpoint():
    return tea.teacher_login_handler(request.form)

@app.route("/api/teacher/addnewsession", methods=['POST'])
def add_new_session_endpoint():
    return tea.add_new_session_handler(request.form)

@app.route("/api/teacher/updatesession/<id>", methods=['PATCH'])
def update_session_endpoint(id):
    return tea.update_session_handler(id, request.form)

@app.route("/api/teacher/addstudenttosession", methods=['POST'])
def add_student_to_session_endpoint():
    return tea.add_student_to_session_handler(request.form)

@app.route("/api/teacher/getallstudent", methods=['GET'])
def get_all_student_endpoint():
    return tea.get_all_student_handler()

@app.route("/api/teacher/getallsession/<startdate>", methods=['GET'])
def get_all_session_endpoint(startdate):
    return tea.get_all_session_handler(startdate)

@app.route("/api/teacher/getnumstufollowedcategories/<id>", methods=['GET'])
def get_num_stu_followed_categories_endpoint(id):
    return tea.get_num_stu_followed_categories_endpoint(id)

@app.route("/api/teacher/getteacherinformation/<id>")
def get_teacher_information_endpoint(id):
    return tea.get_teacher_information_handler(id)

@app.route("/api/teacher/getsessionattendancestatus/<id>")
def get_session_attendance_status_endpoint(id):
    return tea.get_session_attendance_status_handler(id)