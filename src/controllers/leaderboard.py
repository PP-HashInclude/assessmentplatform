from flask import render_template, session, request, redirect, url_for, flash
from repositories import db

def leaderboard():
    playerid = ""
    student_name = session.get("username")
    print (student_name)
    student_class = session.get("classid")
    assessment = ""
    dbresultrows = []
    dbassessmentrows =[]

    try:
        playerid = session.get("admno")
        
        if playerid is None:
            flash("Please login to view your score")
            return redirect(url_for('home'))
        else:
            if request.method == "GET":            
                dbassessmentrows = db.getStudentExpiredCompetitions(playerid)
            elif request.method == "POST":
                dbassessmentrows = db.getStudentExpiredCompetitions(playerid)
                assessment = request.form.get("assessmentid")
                dbresultrows = db.getScore(playerid, assessment)
    except Exception as ex:
        print ("leaderboard():", ex)
        
    return render_template("leaderboard.html", student_name=student_name, student_class=student_class, assessmentselected=assessment, dbresultrows=dbresultrows, dbassessmentrows=dbassessmentrows, isloggedin=True)
