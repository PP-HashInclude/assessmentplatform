from flask import render_template, session
from repositories import db

#@app.route('/')
def home():
    isteacher = False

    loginid = session.get("admno")
    if loginid is None:
        isteacher = False
    else:
        isteacher = db.isTeacher(loginid)

    return render_template("home.html", isteacher=isteacher)
