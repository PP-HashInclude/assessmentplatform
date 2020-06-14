from flask import request, render_template, session, redirect, url_for
from repositories import db

def competitions():
    player_id = session.get("admno")
    competitionmessage = ""

    if player_id is None:
        competitionmessage = "Please Login to view Competition details."
        #return render_template("competitionanswers.html", competitionmessage=competitionmessage, dbcompetitionrows=[], dbcompetitiondetail={}, dbanswerrows=[])
        return redirect(url_for('home'))
    
    if db.isTeacher(player_id):
        dbcompetitionrows = db.getAllCompetitionNames()
    else:
        dbcompetitionrows = db.getExpiredCompetitions()

    if len(dbcompetitionrows) == 0:
        competitionmessage = "All competitions are active.  Please try later."
        return render_template("competitionanswers.html", competitionmessage=competitionmessage, dbcompetitionrows={}, dbcompetitiondetail={}, dbanswerrows=[], isloggedin=True)

    return render_template("competitionanswers.html", competitionmessage=competitionmessage, dbcompetitionrows=dbcompetitionrows, dbcompetitiondetail={}, dbanswerrows=[], isloggedin=True)

def competitionanswers():
    competitionmessage = ""
    competitionselected = request.form.get("selCompetition")
    player_id = session.get("admno")

    if player_id is None:
        competitionmessage = "Please Login to view Competition details."
        #return render_template("competitionanswers.html", competitionmessage=competitionmessage, competitionselected=competitionselected, dbcompetitionrows=[], dbcompetitiondetail={}, dbanswerrows=[])
        return redirect(url_for('home'))

    if db.isTeacher(player_id):
        dbcompetitionrows = db.getAllCompetitionNames()
    else:
        dbcompetitionrows = db.getExpiredCompetitions()

    if competitionselected == "":
        competitionmessage = "Please select Competition."
        return render_template("competitionanswers.html", competitionmessage=competitionmessage, competitionselected=competitionselected, dbcompetitionrows=dbcompetitionrows, dbcompetitiondetail={}, dbanswerrows=[], isloggedin=True)

    dbcompetitiondetail = db.getCompetitionDetail(competitionselected)

    dbanswerrows = db.getQuestionAnwers(competitionselected)

    return render_template("competitionanswers.html", competitionmessage=competitionmessage, competitionselected=competitionselected, dbcompetitionrows=dbcompetitionrows, dbcompetitiondetail=dbcompetitiondetail, dbanswerrows=dbanswerrows, isloggedin=True)
