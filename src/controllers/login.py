from flask import render_template, request, make_response, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from repositories import db
from common import utility

#@app.route('/login')
def login():
    loginmessage = request.args.get('loginmessage')

    if loginmessage is None:
        loginmessage = ""
    
    return render_template("login.html", loginmessage=loginmessage)

def chklogin():
    admno = request.form.get('admno')
    passwd = request.form.get('psw')
    remember = request.form.get('remember')

    isadminconfirmed = db.isAdminConfirmation(admno)

    if not isadminconfirmed:
        flash("Your registration is under Administration review.  Pl. try again later.")
        return render_template("login.html", loginmessage="")

    playenrname, email, mobile, playerpwd, classid = db.CheckLogin(admno)
    if len(playenrname) > 0:
        if not check_password_hash(playerpwd, passwd):
            flash("Invalid admission/joining number/password")
            return render_template("login.html", loginmessage="")

        session["admno"] = admno
        session["email"] = email
        session["mobile"] = mobile
        session["username"] = playenrname
        session["classid"] = classid

        if db.isTeacher(admno):
            session["isteacher"] = True
        else:
            session["isteacher"] = False

        # questionmessage = "You are logged in"
        #resp = make_response(redirect(url_for("squestion", questionmessage=questionmessage)))
        if session.get("isteacher"):
            resp = make_response(redirect(url_for("classassessmentsum")))
        else:
            resp = make_response(redirect(url_for("assessment")))
        
        if (remember == "on"):
            resp.set_cookie("admin_no", admno, max_age=1)
        
        return resp
    else:
        flash("Invalid admission/joining number/password")
        return render_template("login.html", loginmessage="")
    
def forgotpass():
    return render_template("forgotpass.html", resetpassmessage="")

def genotp():
    try:
        newpassmessage = ""
        competitionselect = ""

        admno = request.form.get('admno')
        otpnum = utility.generateOTP()
        otpmsg = otpnum + " is your One Time Password to reset password. It isvalied for 5 min."
        #isSendOTPOK = utility.sendOTP(admno, otpmsg)
        emailto = db.getUserEmail(admno)
        issendotpok = utility.sendEmail(emailto, otpmsg)

        if issendotpok:
            otpvalidtilltime = datetime.datetime.now() + datetime.timedelta(minutes=5)
            isSaveOTPOK = db.saveOTP(admno, otpnum, otpvalidtilltime)

            if isSaveOTPOK:
                session["admno"] = admno
                #dbrows = db.getCompetitions()
                flash("OTP sent. Please check your registered email.")
            else:
                flash("Unable to send OTP..")
        else:
            flash("Error while sending OTP..")
    except Exception as ex:
        flash("Unable to reset. Please try again later.")
    
    return redirect(url_for('genpass', playerid=admno))


def logout():
    session.clear()
    return redirect(url_for('home'))