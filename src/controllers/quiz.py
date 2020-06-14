from flask import render_template, request, session, flash, redirect, flash, url_for, make_response, jsonify
import datetime
from repositories import db
import flask
import io
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import base64
import os
from common import config

def question():
    if request.user_agent.browser == "firefox":
        flash("Assessment is not support in firefox.  Please use a different browser")
        return redirect(request.referrer)

    player_id = session.get("admno")
    if player_id is None:
        quizmessage = "Please Login to take assessment."
        #return render_template("quiz.html", playername="", dbexamtopic=[], questionmessage=quizmessage, dbqna={}, maxqcount="")
        return redirect(url_for('home'))

    assessment = request.args.get('asmt')
    dbstudent= []
    dbassessment = []
    dbqna = []
    dbqpaperimages = []

    dbstudent = db.getStudentDetail(player_id)
    dbassessment = db.getCompetitionDetail(assessment)
    dbqna = db.getAllQuizQuestions(player_id, assessment)
    dbqpaperimages = db.getQpaperImages(assessment)

    if len(dbqna) == 0 or len(dbassessment) == 0:
        flash("No active assessment or question. Please try again later.")

    return render_template("quiz2.html", dbstudent=dbstudent, dbassessment=dbassessment, dbqna=dbqna, dbqpaperimages=dbqpaperimages, isloggedin=True)

def submit():
    player_id = session["admno"]
    assessment = request.form.get("assessment")

    isSubmitted = db.isSubmitted(player_id, assessment)

    if isSubmitted == True:
        flash("You have already submitted response. Response cannot be submitted again.")
    else:
        qCount = int(request.form.get("qCount"))
        
        for i in range(1, qCount+1):
            qid = request.form.get("qid" + str(i))
            ans = request.form.get("choice" + str(i))
            points = request.form.get("points" + str(i))
            negativepoints = request.form.get("negativepoints" + str(i))

            correct_ans = db.getAnswer(assessment, qid)

            if correct_ans != ans:
                points = negativepoints
            
            subtime = datetime.datetime.now()
           
            isRegisterOK = db.registerAndSubmitResponse(player_id, assessment, qid, ans, points, subtime)

            if isRegisterOK:
                #questionmessage = "Your response registered successfully"
                flash("Response to Question: " + str(qid) + " was saved successfully" )
            else:
                # questionmessage = "Unable to register response."
                flash("Response to Question: " + str(qid) + " could not be saved.." )

            if i == (qCount):
                flash("All responses were submitted successfully.")

    return redirect(url_for("question", isloggedin=True))

def assessment():
    if request.user_agent.browser == "firefox":
        flash("Assessment is not support in firefox.  Please use a different browser")
        return redirect(request.referrer)

    student_admno = session.get("admno")
    if student_admno is None:
        flash("Please login to take assessment")        
        #return redirect(url_for('login', loginmessage=""))
        return redirect(url_for('home'))
    else:
        dbrows = db.getAssessmentList(student_admno)
        return render_template("assessmentlist.html", dbrows=dbrows, isloggedin=True)


def savesnap():
    if request.method == "POST":
        studentid = session.get("admno")
        classid = "class" + request.form.get("classid")
        assessment = request.form.get("assessment")
        assessment = assessment.replace(" ", "_")

        imgdata = request.form['snapimgdata']
        imgdata = imgdata[imgdata.find(',')+1:]
        file_imgdata = io.BytesIO(base64.b64decode(imgdata))
        
        student_image_file = "s_" + studentid + assessment + "_" + datetime.datetime.now().strftime("_%Y%m%d_%I-%M-%S_%p") + ".jpg"
        file = FileStorage(file_imgdata, filename=student_image_file)
        filename = secure_filename(file.filename)

        save_folder = config.get("STUDENT", "UPLOAD_FOLDER") + "/" + classid

        file.save(os.path.join(save_folder, filename))

        #return jsonify(studentid, request.form['snapimgdata'])
        return jsonify(success=True)
