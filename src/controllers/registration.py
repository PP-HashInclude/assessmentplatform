from flask import render_template, request, make_response, redirect, url_for, session, flash
from repositories import db
from werkzeug.security import generate_password_hash
import datetime
from common import utility

#@app.route('/signup')
def signup():
    dbrows = db.getCompetitions()
    competition = request.args.get("competition")
    return render_template("registration.html", competitionselected=competition, registrationmessage="", dbrows=dbrows)

#@app.route('/senddetails')
def register():
    name = request.form.get('uname')
    email = request.form.get('email')
    passwd = generate_password_hash(request.form.get('psw1'))
    mobilNo = request.form.get('mobno')
    admno = request.form.get('admno')
    registerOn = str(datetime.datetime.now())
    isunregisterok = False

    isunregisterok = db.unregisterPlayer(admno, isunconfirmed=True)

    isRegistrationOK = db.registerPlayer(admno, name, email, passwd, mobilNo, registerOn)

    if isRegistrationOK:
        # confirmURL = request.host_url + "/validateregistration?admno=" + admno + "&rgdt=" + registerOn
        flash("Your registration is accepted")
        
        otp = utility.generateOTP()
        otpvalidtilltime = datetime.datetime.now() + datetime.timedelta(minutes=10)
        isotpsaved = db.saveOTP(admno, otp, otpvalidtilltime)

        if not isotpsaved:
            flash ("Unable to send OTP for registration confimation. Pl. retry registration")
            
            isunregisterok = db.unregisterPlayer(admno)
            
            if not isunregisterok:
                flash("Unable to complete registration. Pl. try again later.")
                resp = redirect(url_for("register"))
                return resp

        eMailMsg = "Your KSVSS Online Assessment registration OTP is " + otp

        utility.sendEmail(email, eMailMsg)

        flash("Please check your eMail for OTP to confirm registration. OTP is valid for 10 min.")

        session["admno"] = admno

        resp = redirect(url_for("validateregistration"))
        return resp
    else:
        flash("Unable to register. Pl. contact your administrator.")
        return render_template("registration.html", registrationmessage="")

def genpass():
    #competition = request.form.get('competition')
    mobilNo = request.args.get('playerid')
    newpassmessage = request.args.get('newpassmessage')
    
    return render_template("newpass.html", newpassmessage=newpassmessage, playerid=mobilNo)

def newpassupdate():
    admno = request.form.get("admno")
    usrotp = request.form.get('otp')
    npasswd1 = request.form.get('npsw1')
    npasswd2 = request.form.get('npsw2')
    statusmessage = ""

    if admno is None:
        flash("Invalid mobile number or mobile number not found")
    else:
        if npasswd1 != npasswd2:
            flash("New password does not match")
        else:
            isOTPOK = db.IsOTPValid(admno, usrotp)

            if isOTPOK:
                isUpdateOK = db.UpdatePassword(admno, generate_password_hash(npasswd1))
                
                if isUpdateOK > 0:
                    flash("Password updated successfully. Login with your new password")
                    return redirect(url_for('login', loginmessage=statusmessage))
                else:
                    flash("Invalid Login/Password. Password could not be updated")
            else:
                flash("OTP does not match")
    
    return redirect(url_for('genpass', player_id=admno))


def validateregistration():
    userregmsg = ""
    isUserRegOK = False

    if request.method == 'POST':
        admno = request.form.get("admno")
        otp = request.form.get("otp")
        isUserRegOK = db.IsOTPValid(admno, otp)

        if (isUserRegOK):
            isupdateregistration = db.isUserConfirmation(admno, datetime.datetime.now())
            userregmsg = "Your registration is validated successfully. Please use your admission/joining number and password to login"
        else:
            userregmsg = "Invalid Admin or Joining number/OTP. Your registeration could not be validated"
        
        flash(userregmsg)
        
    return render_template("userregistration.html", signupotpok = isUserRegOK)