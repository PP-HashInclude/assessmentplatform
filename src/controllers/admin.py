from flask import request, flash, redirect
from common import utility, config
from werkzeug.utils import secure_filename
import os
import datetime

def assessments():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No PDF file selected')
                return redirect(request.url)
            
            asssement_class = request.form.get("assessment_class")

            if file and utility.valid_qpaperfile(file.filename):
                folder_path = config.get("QPAPER_SETTINGS", asssement_class)
                secfilename = secure_filename(file.filename)
                
                fnsplit = secfilename.split(".")
                filename = fnsplit[0] + datetime.datetime.now().strftime("_%Y%m%d_%I-%M-%S_%p") + "." + fnsplit[1]

                #print (os.path.join(folder_path, filename))
                file.save(os.path.join(folder_path, filename))

                assessmentimages = utility.generateQPaperimages(os.path.join(folder_path, filename), folder_path)

                if len(assessmentimages) > 0:
                    flash("Assessment uploaded successfully")
                else:
                    flash("Unable to uploaded Assessment. Please contact your administrator.")

                return redirect(request.url)
            else:
                flash("Please select a PDF file")
                return redirect(request.url)
    except Exception as ex:
        print("assessments():", ex)