from app_init import app

@app.route("/")
def welcome():
    return "FLASK_ATTENDANCE_APP"

from endpoints import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)