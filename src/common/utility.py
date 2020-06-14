import requests
from common import config
import math, random
import smtplib
import enum
from flask import session, json
from repositories import db
import datetime
from pdf2jpg import pdf2jpg
import os
import base64


class Authorization(enum.Enum):
    TEACHER = 0
    STUDENT = 1

def getDictionaryLength(myobj):
    keyLen, valLen = 0, 0
    k_lst = list(myobj.keys())
    v_lst = list(myobj.values())

    for i in range(len(k_lst)):
        keyLen += len(k_lst[i].encode('utf-8'))
        valLen += len(v_lst[i].encode('utf-8'))
    
    final = keyLen + valLen

    return final

def sendOTP(mobilenumber, otpMessage):
    isSent = False

    try:
        # print("INSIDE TRY")    
        url = config.getSMSURL()
        # print("STRING URL: ",str(url))
        usr = config.get("BULKSMS_URL", "user")
        # print("USER AND URL: ","BULKSMS_URL", usr)
        pwd = config.get("BULKSMS_URL", "password")
        sdr = config.get("BULKSMS_URL", "sender")
        typ = config.get("BULKSMS_URL", "type")
        
        # print ("ALL VARIABLES", url, usr, pwd, sdr, typ)
        
        myobj = {'user': str(usr),
            'password': str(pwd),
            'sender': str(sdr),
            'mobile': str(mobilenumber),
            'type': str(typ),
            'message': str(otpMessage)}
        
        conlength = getDictionaryLength(myobj)

        resp = requests.post(url, data = myobj, headers={'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': str(conlength)})

        # print(resp.text)
        isSent = True
    except Exception as ex:
        print ("sendOTP:", ex)

    return isSent
    
def generateOTP():
	digits_in_otp = "0123456789"
	OTP = ""

# for a 4 digit OTP we are using 4 in range
	for i in range(4):
		OTP += digits_in_otp[math.floor(random.random() * 10)]

	return OTP

def allowed_file(filename):
    extension = config.get("DB_IMPORT", "ALLOWED_EXTENSIONS")
    allowed_extensions = {extension}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def allowed_qpaperfile_extensions(filename):
    extension = config.get("QPAPER", "QPAPER_ALLOWED_EXTENSIONS")
    allowed_extensions = {extension}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def allowed_answerkeyfile_extensions(filename):
    extension = config.get("QPAPER", "ANSWERKEY_ALLOWED_EXTENSIONS")
    allowed_extensions = {extension}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def sendEmail(email_to, email_data):
   # creates SMTP session
    s = smtplib.SMTP(config.get("EMAIL_SETTINGS", "SERVER"), config.get("EMAIL_SETTINGS", "PORT"))
    
    # start TLS for security 
    s.starttls()
    
    # Authentication
    senderemail = config.get("EMAIL_SETTINGS", "SENDER_EMAIL_ID")
    senderpwd = config.get("EMAIL_SETTINGS", "SENDER_EMAIL_PWD")
    s.login(senderemail, senderpwd)
    
    # sending the mail 
    s.sendmail(config.get("EMAIL_SETTINGS", "SENDER_EMAIL_ID"), email_to, email_data)
    
    # terminating the session 
    s.quit()

    return True


def convert_qpaper(inputfolder, inputfilename, outputfolder, qpaperfoldername=""):
    inputpathfile = os.path.join(inputfolder, inputfilename)
    
    result = pdf2jpg.convert_pdf2jpg(inputpathfile, outputfolder, dpi=300, pages="ALL")
    print(result)
    
    #Remove filepaths and return only filenames as list
    if len(qpaperfoldername) > 0:
        qpaperfoldername = qpaperfoldername + "/" 

    jpgoutputfolder = qpaperfoldername + os.path.basename(result[0]['output_pdfpath'])
    jpgfilepaths = result[0]['output_jpgfiles']
    jpgfiles = []
    for jpgfile in jpgfilepaths:
        jpgfiles.append((inputfilename, jpgoutputfolder + "/" + os.path.basename(jpgfile)))

    return jpgfiles

def degenerateb64String(data):
    b64_one_bytes = base64.urlsafe_b64decode(data)

    b64_one_str = str(b64_one_bytes, "utf-8")
    b64_one_str = json.loads(b64_one_str)

    #return json.dumps(b64_one_str, indent=4)

    return b64_one_str