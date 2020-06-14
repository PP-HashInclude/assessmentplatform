from flask import render_template, session, request, redirect, url_for, make_response, json, flash
from repositories import db
from werkzeug.security import generate_password_hash, check_password_hash

def account():
    try:
        dbrows = {}

        playerid = session.get("admno")

        if playerid is not None:
            dbrows = db.getAccount(playerid)
        else:
            flash("Please login before accessing account.")

        return render_template("account.html", dbrows=dbrows)
    except Exception as ex:
        print ("account(), ex")
        flash("Please login before changing account settings.")

        return render_template("account.html", dbrows=dbrows)

        #return redirect(url_for("login", loginmessage=loginmessage))

def updateaccount():
    admno = request.form.get('admno')
    playername = request.form.get('uname')
    email = request.form.get('email')

    isUpdateOK = db.updateProfile(admno, playername, email)

    if isUpdateOK:
        flash("Profile updated successfully.")
    else:
        flash("Unable to update profile")

    return account()

def resetpassword():
    playerid = ""
    statusmessage = ""

    try:
        playerid = session.get("admno")

        if playerid is None:
            flash("Please login to reset password")
            return redirect(url_for('home'))
    except Exception as ex:
        print ("resetpassword(): ", ex)
        flash("Unable to load data.")
    
    return render_template("resetpass.html", playerid=playerid)

        #return redirect(url_for('forgetpassword', resetpassmessage=resetpassmessage, competitionselected="", dbrows=None, dbcompetitions=None))

def updatepassword():
    admno = session.get("admno")
    passwd = request.form.get('opsw')
    npasswd1 = request.form.get('npsw1')
    npasswd2 = request.form.get('npsw2')
    statusmessage = ""

    if admno is None:
        flash("Please login to update password")
        return redirect(url_for('home'))
    else:
        if npasswd1 != npasswd2:
            flash("New password does not match")
        else:
            playenrname, email, mobno, playerpwd, classid = db.CheckLogin(admno)

            if len(playenrname) > 0:
                if check_password_hash(playerpwd, passwd):
                    isUpdateOK = db.UpdatePassword(admno, generate_password_hash(npasswd1))
                    
                    if isUpdateOK > 0:
                        flash("Password updated successfully. Login with your new password")
                        return redirect(url_for('login', loginmessage=statusmessage))
                    else:
                        flash("Invalid Login/Password. Password could not be updated")
                else:
                    flash("Invalid Login/Password. Password could not be updated")

    #return make_response(redirect(url_for('resetpassword', resetpassmessage=statusmessage)))
    return render_template("resetpass.html", playerid=admno)

def checkregistration():
    if request.method == 'GET':
        return render_template("checkregistration.html")
    elif request.method == 'POST':
        admno = request.form.get('admno')

        classno = db.getRegistrationStatus(admno)

        if len(classno) > 0:
            flash("You are registered for class:", str(classno))
        else:
            flash("No registration found")
            
            return render_template("checkregistration.html")