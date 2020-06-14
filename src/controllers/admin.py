import os
from flask import Flask, flash, request, redirect, url_for, session, render_template
from werkzeug.utils import secure_filename
from common import utility, config
from repositories import db, cos
import datetime
import jinja2

def isloggedin():
    return True

loader = jinja2.FileSystemLoader('./')
env = jinja2.Environment(loader=loader)
env.filters['isLoggedin'] = isloggedin

def importdata():
    try:
        player_id = session.get("admno")
        if player_id is None:
            flash("Please Login as admin.")
            return redirect(url_for('home'))

        #if db.authorize(player_id, utility.Authorization.TEACHER):
        if not db.isTeacher(player_id):
            flash("Please Login as teacher/admin.")
            return redirect(url_for('home'))

        if request.method == 'GET':
            dbrows = db.getAssessmentToRemove(player_id)
            return render_template("admin.html", dbrows=dbrows)
        elif request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No CSV file selected')
                return redirect(request.url)
            
            if file and utility.allowed_file(file.filename):
                folder_path = config.get("DB_IMPORT", "UPLOAD_FOLDER")
                secfilename = secure_filename(file.filename)
                
                fnsplit = secfilename.split(".")
                filename = fnsplit[0] + datetime.datetime.now().strftime("_%Y%m%d_%I-%M-%S_%p") + "." + fnsplit[1]

                print (os.path.join(folder_path, filename))
                file.save(os.path.join(folder_path, filename))

                table_name = request.form.get('tablename')
                isHeader = request.form.get("chkHeader") != None
                isReplace = request.form.get("chkReplace") != None

                isCSVImportOK = db.import_csv_data(folder_path + "/" + filename, table_name, isHeader)
                
                if isCSVImportOK:
                    flash("Data imported successfully")
                else:
                    flash("Unable to import data. Please contact your administrator.")

                return redirect(request.url)
            else:
                flash("Please select a CSV file")
                return redirect(request.url)
    except Exception as ex:
        print ("Unable to process request..", ex)
    
    return

def confirmregistration():
    rowCount = 0
    if request.method == 'GET':
        dbrows, rowcount = db.getRegistrations()
        if rowcount == 0:
            flash("No registrations to confirm.")

        return render_template('confirmreg.html', dbrows = dbrows, rowcount = rowcount, isloggedin=True)
    elif request.method == 'POST':
        for key in request.form:
            if key.startswith("admno"):
                id_ = key.partition("_")[-1]
                admno = request.form[key]

                confrm_date = datetime.datetime.now()
                isconfrmregOK = db.adminConfirmRegistration(admno, confrm_date)
                if (isconfrmregOK):
                    flash("Admission No. " + str(admno) + " confirmed.")
                else:
                    flash("Admission No. " + str(admno) + " could not be confirmed.")
        
        return redirect(url_for("request.url"))

def removeassessment():
    if request.method == "POST":
        userid = session.get("admno")
        assessment = request.form.get("assessment")
        
        if not db.authorize(userid, assessment, utility.Authorization.TEACHER):
            flash("You are not authorized to remove assessment")
        else:
            if db.removeAssessment(assessment):
                flash("Assessment removed successfully")
            else:
                flash("Unable to remove assessment. Assessment responses exist.")
    
    return redirect(url_for("uploadassessment"))

def classassessmentsum():
    loginid = ""
    classselected = ""
    assessmentselected = ""
    dbclassrows = []
    dbassessmentrows = []
    dbclassassessmentrows = []

    try:
        loginid = session.get("admno")
        
        if loginid is None:
            flash("Please login to view report")
            return redirect(url_for('home'))
        elif not db.isTeacher(loginid):
                flash("You do not have permission to view this report")
        elif request.method == "GET":
            dbclassrows = db.getTeacherClasses(loginid)

            if len(dbclassrows) > 0:
                classselected = dbclassrows[0][0]
                dbassessmentrows = db.getClassAssessments(classselected)
        elif request.method == "POST":
            classselected = request.form.get("classid")
            assessmentselected = request.form.get("assessmentid")
            
            dbclassassessmentrows = db.getClassAssessmentStudents(classselected, assessmentselected)
            
            dbclassrows = db.getTeacherClasses(loginid)
            dbassessmentrows = db.getClassAssessments(classselected)
            
        return render_template("classassessmentsum.html", dbclassrows=dbclassrows, dbassessmentrows=dbassessmentrows, dbclassassessmentrows=dbclassassessmentrows, classselected=classselected, assessmentselected=assessmentselected, isloggedin=True)
    except Exception as ex:
        print ("classassessmentsum():", ex)
        statusmessage = "Unable to load data."

def classstudentsum():
    loginid = ""
    classselected = ""
    studentselected = ""
    dbclassrows = []
    dbstudentrows = []
    dbclassstudentrows = []

    try:
        loginid = session.get("admno")
        
        if loginid is None:
            flash("Please login to view report")
            return redirect(url_for('home'))
        elif not db.isTeacher(loginid):
                flash("You do not have permission to view this report")
        elif request.method == "GET":
            dbclassrows = db.getTeacherClasses(loginid)

            if len(dbclassrows) > 0:
                classselected = dbclassrows[0][0]
                dbstudentrows = db.getClassStudents(classselected)
        elif request.method == "POST":
            classselected = request.form.get("classid")
            studentselected = request.form.get("studentid")
           
            dbclassstudentrows = db.getClassStudentAssessments(classselected, studentselected)
            
            dbclassrows = db.getTeacherClasses(loginid)
            dbstudentrows = db.getClassStudents(classselected)
        
        return render_template("classstudentsum.html", dbclassrows=dbclassrows, dbstudentrows=dbstudentrows, dbclassstudentrows=dbclassstudentrows, classselected=classselected, studentselected=studentselected, isloggedin=True)
    except Exception as ex:
        print ("classstudentsum():", ex)
        statusmessage = "Unable to load data."

def studentassessmentdet():
    loginid = ""
    classselected = ""
    studentselected = ""
    assessmentselected = ""
    dbclassrows = []
    dbstudentrows = []
    dbassessmentrows = []
    dbassessmentresponserows = []

    try:
        loginid = session.get("admno")
        
        if loginid is None:
            flash("Please login to view report")
            return redirect(url_for('home'))
        elif not db.isTeacher(loginid):
            flash("You do not have permission to view this report")
        elif request.method == "GET":
            dbclassrows = db.getTeacherClasses(loginid)

            if len(dbclassrows) > 0:
                classselected = dbclassrows[0][0]
                dbstudentrows = db.getClassStudents(classselected)

                if len(dbstudentrows) > 0:
                    studentselected = dbstudentrows[0][0]
                    dbassessmentrows = db.getClassStudentAssessments(classselected, studentselected)

        elif request.method == "POST":
            classselected = request.form.get("classid")
            studentselected = request.form.get("studentid")
            assessmentselected = request.form.get("assessmentid")
            
            dbassessmentresponserows = db.getClassStudentAssessmentResponse(classselected, studentselected, assessmentselected)
            
            dbclassrows = db.getTeacherClasses(loginid)
            dbstudentrows = db.getClassStudents(classselected)
            dbassessmentrows = db.getClassStudentAssessments(classselected, studentselected)

        return render_template("classstudentassessmentdet.html", dbclassrows=dbclassrows, dbstudentrows=dbstudentrows, dbassessmentrows=dbassessmentrows, dbassessmentresponserows=dbassessmentresponserows, classselected=classselected, studentselected=studentselected, assessmentselected=assessmentselected, isloggedin=True)
    except Exception as ex:
        print ("studentassessmentdet():", ex)
        statusmessage = "Unable to load data."

def uploadassessment():
    dbclassrows = []

    try:
        userid = session.get("admno")
        if userid is None:
            flash("Please Login as teacher / admin.")
            return redirect(url_for('home'))

        #if db.authorize(player_id, utility.Authorization.TEACHER):
        if not db.isTeacher(userid):
            flash("Please Login as teacher.")
            return redirect(url_for('home'))

        if request.method == 'GET':
            dbclassrows = db.getClasses()
            dbassessmentrows = db.getAssessmentToRemove(userid)
            dbassessmentrowschangedate = db.getCompetitions()
            return render_template("assessmentupload.html", dbclassrows=dbclassrows, dbassessmentrows=dbassessmentrows, dbassessmentrowschangedate=dbassessmentrowschangedate, isloggedin=True)
        elif request.method == 'POST':
            # check if the post request has the file part
            if 'qpfile' not in request.files:
                flash('No question paper file')
                return redirect(request.url)
            
            if 'akfile' not in request.files:
                flash('No answer-key paper file')
                return redirect(request.url)
            
            qpfile = request.files['qpfile']
            qpjpgfiles = ""

            akfile = request.files['akfile']
            # if user does not select file, browser also
            # submit an empty part without filename
            if qpfile.filename == '' or akfile.filename == '':
                flash('File not selected')
                return redirect(request.url)
            
            if qpfile and utility.allowed_qpaperfile_extensions(qpfile.filename):
                folder_name = config.get("QPAPER", "UPLOAD_FOLDER_NAME")
                folder_path = config.get("QPAPER", "UPLOAD_FOLDER")
                secfilename = secure_filename(qpfile.filename)
                
                fnsplit = secfilename.split(".")
                qpfilename = fnsplit[0] + datetime.datetime.now().strftime("_%Y%m%d_%I-%M-%S_%p") + "." + fnsplit[1]

                qpfile.save(os.path.join(folder_path, qpfilename))

                qpjpgfiles = utility.convert_qpaper(folder_path, qpfilename, folder_path, folder_name)

                if akfile and utility.allowed_answerkeyfile_extensions(akfile.filename):
                    folder_path = config.get("QPAPER", "UPLOAD_FOLDER")
                    secfilename = secure_filename(akfile.filename)
                    
                    fnsplit = secfilename.split(".")
                    akfilename = fnsplit[0] + datetime.datetime.now().strftime("_%Y%m%d_%I-%M-%S_%p") + "." + fnsplit[1]

                    akfile.save(os.path.join(folder_path, akfilename))
                else:
                    flash("Please select a CSV file")
                    return redirect(request.url)

                dtformat = "%d-%m-%Y %H:%M:%S"
                classname = request.form.get("classid")
                assesementname = request.form.get("assessmentname")
                description = request.form.get("description")
                
                startson = request.form.get("startson")
                startson = datetime.datetime.strptime(startson, dtformat)

                endson = request.form.get("endson")
                endson = datetime.datetime.strptime(endson, dtformat)

                note = request.form.get("note")

                isAssessmentSaved = db.createAssessmentWithFile(classname, assesementname, description, startson, endson, note, qpfilename, qpjpgfiles)
                if isAssessmentSaved:
                    isanswerkeysaved = db.import_csv_data(folder_path + "/" + akfilename, "QuestionBank", True)
                    if isanswerkeysaved:
                        flash("Assessment created successfully")
                    else:
                        flash("Unable to save Answer-Key. Please contact your administrator")
                else:
                    flash("Unable to create Assessment. Please contact your adminstrator")

                return redirect(request.url)
            else:
                flash("Please select a PDF file")
                return redirect(request.url)
    except Exception as ex:
        print ("uploadassessment()", ex)
    
    return

def updateassessmentdate():
    if request.method == "POST":
        userid = session.get("admno")
        assessment = request.form.get("assessmentchangedate")
        
        if not db.authorize(userid, assessment, utility.Authorization.TEACHER):
            flash("You are not authorized to remove assessment")
        else:
            endson = request.form.get("endsonremove")
            
            dtformat = "%d-%m-%Y %H:%M:%S"
            endson = datetime.datetime.strptime(endson, dtformat)

            if db.updateAssessmentDate(assessment, endson):
                flash("Assessment End Date/Time updated successfully")
            else:
                flash("Unable to update assessment End Date/Time.")
    
    return redirect(url_for("uploadassessment"))
