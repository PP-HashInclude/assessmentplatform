from common import config, utility
import sqlite3
import csv
import datetime

dbfile = config.getdbfile()

def opendb():
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    return conn, c

def calculateRanks(rows):

    #row_lst = []
    newrows = []
    name_idx = 0
    competitionname_idx = 1
    totalpoints_idx = 2
    rank_idx = 3
    time_index = 4

    curr_rank = 1
    for row in range(len(rows)):
        if row == 0:
            #row_lst.append(1)
            curr_competition = rows[row][competitionname_idx]
            t1 = (rows[row][name_idx], rows[row][competitionname_idx],
                      rows[row][totalpoints_idx], curr_rank, rows[row][time_index])
            newrows.append(t1)
            continue

        if rows[row][competitionname_idx] != curr_competition:
            curr_competition = rows[row][competitionname_idx]
            curr_rank = 1
            t1 = (rows[row][name_idx], rows[row][competitionname_idx],
                      rows[row][totalpoints_idx], curr_rank, rows[row][time_index])
            newrows.append(t1)
            continue

        if rows[row][totalpoints_idx] == rows[row-1][totalpoints_idx]:
            if rows[row][time_index] == rows[row-1][time_index]:
                #row_lst.append(curr_rank)
                t1 = (rows[row][name_idx], rows[row][competitionname_idx],
                        rows[row][totalpoints_idx], curr_rank, rows[row][time_index])
                newrows.append(t1)
                continue
            else:
                curr_rank += 1
                t1 = (rows[row][name_idx], rows[row][competitionname_idx],
                        rows[row][totalpoints_idx], curr_rank, rows[row][time_index])
                newrows.append(t1)
        else:
            curr_rank += 1
            t1 = (rows[row][name_idx], rows[row][competitionname_idx],
                    rows[row][totalpoints_idx], curr_rank, rows[row][time_index])
            newrows.append(t1)
    
    return newrows


def calculateClassAssessmentStudentRanks(rows):
    #row_lst = []
    newrows = []
    sno_idx = 0
    name_idx = 1
    score_idx = 2
    rank_idx = 3
    time_index = 4

    curr_rank = 1
    for row in range(len(rows)):
        if row == 0:
            #row_lst.append(1)
            curr_score = rows[row][score_idx]
            t1 = (rows[row][sno_idx], rows[row][name_idx],
                      rows[row][score_idx], curr_rank, rows[row][time_index])
            newrows.append(t1)
            continue

        if rows[row][score_idx] == rows[row-1][score_idx]:
            if rows[row][time_index] == rows[row-1][time_index]:
                #row_lst.append(curr_rank)
                t1 = (rows[row][sno_idx], rows[row][name_idx],
                        rows[row][score_idx], curr_rank, rows[row][time_index])
                newrows.append(t1)
                continue
            else:
                curr_rank += 1
                t1 = (rows[row][sno_idx], rows[row][name_idx],
                        rows[row][score_idx], curr_rank, rows[row][time_index])
                newrows.append(t1)
        else:
            curr_rank += 1
            t1 = (rows[row][sno_idx], rows[row][name_idx],
                    rows[row][score_idx], curr_rank, rows[row][time_index])
            newrows.append(t1)
    
    return newrows

def quote_fix(string):
    new_string = ""
    for i in range(len(string)):
        if string[i] == "'":
            new_string += "'"
        new_string += string[i]
    return new_string

def getQuestionCount(competition_name):
    conn,  cur = opendb()
    sql = "SELECT max(qid) as maxqcount FROM QuestionBank WHERE CompetitionName = '" + competition_name + "'"
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    rowDict = {}
    maxqcount = 0

    if len(rows) > 0:
        maxqcount = rows[0][0]

    return maxqcount

def getQuizQuestion(playerid, competition_name):
    con, cur = opendb()
    
    strSql = "SELECT QId, Quesdesc, Choice1,Choice2,Choice3,Choice4,ValidTill,Points,NegativePoints, \
        (SELECT ResponseChoice from PlayerResponse pr2 where pr2.QId = QuestionBank.QId AND pr2.PlayerId = " + playerid + "  AND \
                            pr2.competitionname = QuestionBank.competitionname) As ResponseChoice \
        FROM QuestionBank \
        WHERE CompetitionName = '" + competition_name + "' AND \
            datetime(ValidTill) > datetime('now', 'localtime') AND \
            QId not in (SELECT QId \
                        FROM PlayerResponse \
                        WHERE PlayerResponse.QId = QuestionBank.QId AND \
                            PlayerResponse.competitionname = QuestionBank.competitionname AND \
                            PlayerResponse.SubmittedOn IS NULL AND \
                            PlayerResponse.PlayerId = " + playerid + ") \
        ORDER BY datetime(ValidTill) ASC LIMIT 1"

    cur.execute(strSql)
    rows = cur.fetchall()
    
    if len(rows) == 0:
        strSql = "SELECT QId, Quesdesc, Choice1,Choice2,Choice3,Choice4,ValidTill,Points,NegativePoints, \
                    (SELECT ResponseChoice from PlayerResponse pr2 where pr2.QId = QuestionBank.QId AND pr2.PlayerId = " + playerid + "  AND \
                                        pr2.competitionname = QuestionBank.competitionname) As ResponseChoice \
                    FROM QuestionBank \
                    WHERE CompetitionName = '" + competition_name + "' AND \
                        datetime(ValidTill) > datetime('now', 'localtime') AND \
                        QId in (SELECT QId \
                                    FROM PlayerResponse \
                                    WHERE PlayerResponse.QId = QuestionBank.QId AND \
                                        PlayerResponse.competitionname = QuestionBank.competitionname AND \
                                        PlayerResponse.SubmittedOn IS NULL AND \
                                        PlayerResponse.PlayerId = " + playerid + ") \
                    ORDER BY datetime(ValidTill) ASC LIMIT 1"
        cur.execute(strSql)

        rows = cur.fetchall()
    
    # print (strSql)

    cur.close()
    con.close()

    qid = ""
    qdesc = ""
    ch1 = ""
    ch2 = ""
    ch3 = ""
    ch4 = ""
    validtill = ""
    points = ""
    negativepoints = ""
    responsechoice = ""

    rowDict = {}
    
    for item in rows:
        qid = item[0]
        qdesc = item[1]
        ch1 = item[2]
        ch2 = item[3]
        ch3 = item[4]
        ch4 = item[5]
        validtill = item[6]
        points = item[7]
        negativepoints = item[8]
        responsechoice = item[9]
    
        rowDict = {"qid": qid,
                    "qdesc": qdesc,
                    "ch1": ch1,
                    "ch2": ch2,
                    "ch3": ch3,
                    "ch4": ch4,
                    "validtill": validtill,
                    "points": points,
                    "negativepoints": negativepoints,
                    "responsechoice": responsechoice
                    }
    
    return rowDict

def getAllQuizQuestions(playerid, competition_name):
    strSql = "SELECT QId, Quesdesc, Choice1, Choice2, Choice3, Choice4, Points, NegativePoints \
                FROM QuestionBank q, Competition c \
                WHERE CompetitionName = ? AND \
                    c.name = ? AND \
                    q.CompetitionName = c.name AND \
                    datetime(c.EndingOn) > datetime('now', 'localtime') AND \
                    datetime(c.startedon) < datetime('now', 'localtime')  AND \
                    NOT EXISTS (SELECT 1 \
                                FROM PlayerResponse p \
                                WHERE p.PlayerId = ? AND \
                                p.competitionname = ?) \
                ORDER by QId"

    data_tuple = (competition_name, competition_name, playerid, competition_name)
    con, cur = opendb()
    
    cur.execute(strSql, data_tuple)
    rows = cur.fetchall()

    cur.close()
    con.close()
    
    return rows

def getThisQuizQuestion(playerid, competition_name, qno):
    con, cur = opendb()
    
    strSql = "SELECT qb.QId, qb.Quesdesc, qb.Choice1, qb.Choice2, qb.Choice3, qb.Choice4, qb.ValidTill, qb.Points, qb.NegativePoints, pr.ResponseChoice \
                FROM QuestionBank qb LEFT OUTER JOIN PlayerResponse pr ON pr.QId = qb.QId AND pr.PlayerId = " + playerid + " \
                WHERE qb.QId = " + qno + " AND \
                qb.CompetitionName = '" + competition_name + "' AND \
                datetime(qb.ValidTill) > datetime('now', 'localtime')"
    
    # print ("getthisquizquestion", strSql)
    cur.execute(strSql)

    rows = cur.fetchall()
    
    cur.close()
    con.close()

    qid = ""
    qdesc = ""
    ch1 = ""
    ch2 = ""
    ch3 = ""
    ch4 = ""
    validtill = ""
    points = ""
    negativepoints = ""
    responsechoice = ""

    rowDict = {}
    
    for item in rows:
        qid = item[0]
        qdesc = item[1]
        ch1 = item[2]
        ch2 = item[3]
        ch3 = item[4]
        ch4 = item[5]
        validtill = item[6]
        points = item[7]
        negativepoints = item[8]
        responsechoice = item[9]
    
        rowDict = {"qid": qid,
                    "qdesc": qdesc,
                    "ch1": ch1,
                    "ch2": ch2,
                    "ch3": ch3,
                    "ch4": ch4,
                    "validtill": validtill,
                    "points": points,
                    "negativepoints": negativepoints,
                    "responsechoice": responsechoice
                    }
    
    return rowDict

def isSubmitted(player_id, competition_name):
    isallrespsubmitted = False
    
    try:
        #sql = "SELECT qb.QId, qb.competitionname \
        #        FROM PlayerResponse pr, QuestionBank qb \
        #        WHERE PlayerId = " + player_id + " AND  \
        #            qb.competitionname = '" + competition_name + "' AND \
        #            qb.Qid = pr.QId AND  \
        #            pr.SubmittedOn IS NOT NULL"
        strSql = "SELECT 1 \
			FROM PlayerResponse p \
			WHERE p.PlayerId = ? AND \
			p.competitionname = ?"
        data_tuple = (player_id, competition_name)

        conn, cur = opendb()
    
        cur.execute(strSql, data_tuple)
        dbrows = cur.fetchall()

        cur.close()
        conn.close()

        if len(dbrows) > 0:
            isallrespsubmitted = True

    except Exception as ex:
        print("issubmitted()", ex)
        #pass
    
    return isallrespsubmitted

def submitResponse(player_id, competition_name, subtime):
    issubmitOK = False
    try:
        conn, cur = opendb()

        strSql = "INSERT INTO PlayerResponse (PlayerId, competitionname, QId, Question, ResponseChoice, RespondedOn, Points, SubmittedOn) \
            SELECT ? AS PlayerId, \
                ? As competitionname, \
                    qb.QId, qb.Quesdesc, \
                    NULL AS ResponseChoice, \
                    datetime('now', 'localtime') AS RespondedOn, \
                    0 AS Points, \
                    ? AS SubmittedOn \
            FROM QuestionBank qb \
            WHERE CompetitionName = ? \
                AND QId NOT IN (SELECT QId \
                				FROM PlayerResponse pr \
                                WHERE PlayerId = ? AND \
                                    qb.Qid = pr.QId)"
        data_tuple = (player_id, competition_name, subtime, competition_name)
        # print ("insert:", sql)

        cur.execute(strSql, data_tuple)
        conn.commit()

        strSql = "UPDATE PlayerResponse SET SubmittedOn = ? WHERE PlayerId = ? AND CompetitionName = ? AND SubmittedOn IS NULL"
        data_tuple = (subtime, player_id, competition_name)

        #print ("update:", sql)

        cur.execute(strSql)
        conn.commit()

        cur.close()
        conn.close()

        issubmitOK = True    
    except Exception as ex:
        print("submitResponse", ex)
        #pass
    
    return issubmitOK


def createQuestion(qno, ques_desc, choice1, choice2, choice3, choice4, choice_right, valid_till):
    conn, cur = opendb()
    
    sql = "INSERT INTO QuestionBank VALUES (" + str(qno) + ",'" + quote_fix(str(choice1)) + "','" + quote_fix(str(choice2)) + "','" + quote_fix(str(choice3)) + "','" + quote_fix(str(choice4)) + "','" + quote_fix(str(choice_right)) + "','" + quote_fix(str(ques_desc)) + "', datetime('" + str(valid_till) + "'))"

    cur.execute(str(sql))
    conn.commit()

    cur.close()
    conn.close()

def CheckLogin(loginid):
    strSQL = "SELECT name, email, mobile, password, classid FROM Players WHERE admissionnumber = ? AND adminconfirmedon IS NOT NULL"
    data_tuple = (loginid,)
    
    conn, cur = opendb()

    cur.execute(strSQL, data_tuple)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if len(rows) > 0:
        playername = rows[0][0]
        email = rows[0][1]
        mobile = rows[0][2]
        pwd = rows[0][3]
        classid = rows[0][4]
    else:
        playername = ""
        email = ""
        mobile = ""
        pwd = ""
        classid = ""
    
    return playername, email, mobile, pwd, classid

def registerPlayer(admno, name, email, passwd, mobilNo, registerOn):
    isRegistrationOK = False
    try:
        conn, cur = opendb()
    
        # sql = "INSERT INTO Players VALUES ('" + str(name) + "','" + str(email) + "','" + str(passwd) + "', " + mobileNo + ", " + admno + ", '" + str(competitionname) + "')"
        sql = "INSERT INTO Players (admissionnumber, name, email, mobile, password, registeredon, classid) \
                        SELECT ?, ?, ?, ?, ?, ?, (SELECT classid FROM Admissions WHERE admissionnumber = ?)"

        data_tuple = (admno, name, email, mobilNo, passwd, registerOn, admno)
        
        cur.execute(sql, data_tuple)
        conn.commit()

        cur.close()
        conn.close()

        isRegistrationOK = True
    except Exception as ex:
        print("registerPlayer", ex)
        #pass
    
    return isRegistrationOK

def getCompetitions():
    sql = "SELECT Name FROM competition WHERE datetime('now', 'localtime') < datetime(EndingOn)"

    conn, cur = opendb()

    cur.execute(sql)
    dbrows = cur.fetchall()

    cur.close()
    conn.close()

    return dbrows

def getQuestionList(playerid, competitionname):
    #sql = "SELECT qb.QId, CASE WHEN pr.QId IS NULL THEN 'not saved' ELSE 'saved' END AS saved \
    #    FROM QuestionBank qb LEFT OUTER JOIN PlayerResponse pr ON qb.QId = pr.QId AND \
    #        pr.PlayerId = " + playerid + " \
    #    WHERE qb.competitionname = '" + competitionname + "'"
    strSql = "SELECT qb.QId, CASE WHEN (SELECT pr.qid \
                                    FROM PlayerResponse pr \
                                    WHERE pr.QId = qb.qid AND \
                                        pr.competitionname = qb.competitionname AND \
                                            PlayerId = ?) IS NULL \
                                THEN 'not saved' \
                                ELSE 'saved' END AS saved \
            FROM QuestionBank qb \
            WHERE qb.competitionname = ?"

    #print (sql)
    data_tuple = (playerid, competitionname)
    conn, cur = opendb()

    cur.execute(strSql, data_tuple)
    dbrows = cur.fetchall()

    cur.close()
    conn.close()

    return dbrows

def getExpiredCompetitions():
    sql = "SELECT Name FROM competition WHERE datetime('now', 'localtime') > datetime(EndingOn)"

    conn, cur = opendb()

    cur.execute(sql)
    dbrows = cur.fetchall()

    cur.close()
    conn.close()

    return dbrows

def getCompetitionDetail(competionname):
    strSql = "SELECT * FROM competition WHERE Name = ?"
    data_tuple = (competionname,)

    competionname = ""
    description = ""
    startedon = ""
    endingon = ""
    notes = ""
    classid = ""
    qpaperfile = ""

    rowDict = {}

    conn, cur = opendb()

    cur.execute(strSql, data_tuple)
    dbrows = cur.fetchall()

    cur.close()
    conn.close()

    for item in dbrows:
        competionname = dbrows[0][0]
        description = dbrows[0][1]
        startedon = dbrows[0][2]
        endingon = dbrows[0][3]
        notes = dbrows[0][4]
        classid = dbrows[0][5]
        qpaperfile = dbrows[0][6]
    
        rowDict = {"competitionname": competionname,
                    "description": description,
                    "startedon": startedon,
                    "endingon": endingon,
                    "notes": notes,
                    "classid": classid,
                    "qpaperfile": qpaperfile
                    }
    return rowDict

def getCompetitionEndingOn(competionname):
    strSql = "SELECT EndingOn FROM competition WHERE Name = ?"
    data_tuple = (competionname,)
    
    conn, cur = opendb()
    
    cur.execute(strSql, data_tuple)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

    endingon = ""

    if len(rows) > 0:
        endingon = rows[0][0]
    
    return endingon

def getQuestionAnwers(competionname):
    sql = "SELECT QId, ChoiceAnswer FROM QuestionBank WHERE CompetitionName = '" + str(competionname) + "'"
    
    conn, cur = opendb()

    cur.execute(sql)
    dbrows = cur.fetchall()

    cur.close()
    conn.close()

    return dbrows

def isResponded(player_id, qid, competionname):
    conn, cur = opendb()
    
    sql = "SELECT * FROM PlayerResponse WHERE PlayerId = " + player_id + " AND QId = " + qid + " AND competitionname = '" + competionname + "'"

    cur.execute(sql)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

    isresp = False

    if len(rows) > 0:
        isresp = True
    
    return isresp

def registerAndSubmitResponse(player_id, competition_name, qid, ans, points, subtime):
    isRegisterOK = True

    try:
        strSql = "INSERT INTO PlayerResponse (PlayerId, CompetitionName, QId, ResponseChoice, Points, SubmittedOn) \
                VALUES (?, ?, ?, ?, ?, ?)"
        data_tuple = (player_id, competition_name, qid, ans, points, str(subtime))
        
        conn, cur = opendb()

        cur.execute(strSql, data_tuple)
        conn.commit()

        cur.close()
        conn.close()
    except Exception as ex:
        print ("registerAndSubmitResponse()", ex)
        isRegisterOK = False
    
    return isRegisterOK

def getScore(playerid, assessment):
    strSql = "SELECT pr.Question, Points, QId \
        FROM PlayerResponse pr, Players p, Competition c \
        WHERE pr.playerid = ? AND \
            pr.competitionName = ? AND \
            pr.PlayerId = p.admissionnumber AND \
            pr.SubmittedOn IS NOT NULL AND \
			pr.competitionname = c.name AND \
			datetime('now', 'localtime') > datetime(c.EndingOn) \
        ORDER BY pr.competitionname, QId"

    data_tuple = (playerid, assessment)

    conn,  cur = opendb()
    cur.execute(strSql, data_tuple)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return rows

def getRanks():
    conn,  cur = opendb()
    sql = "SELECT name, pr.competitionname as competionname, sum(points) as totalpoints, \
        NULL as pointrank,  max(datetime(SubmittedOn)) As submittedon \
        FROM PlayerResponse pr, Players p \
        WHERE pr.PlayerId = p.mobile AND \
            pr.SubmittedOn IS NOT NULL \
        GROUP BY name, pr.competitionname \
        ORDER BY pr.competitionname, sum(Points) DESC, SubmittedOn ASC"

    cur.execute(sql)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()   
    rank_lst = calculateRanks(list(rows))
    # print(rank_lst)
    return rank_lst

def getAccount(playerid):
    strSql = "SELECT name, email, admissionnumber FROM Players WHERE admissionnumber = ?"
    data_tuple = (playerid,)

    conn,  cur = opendb()
    cur.execute(strSql, data_tuple)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    rowDict = {}

    if len(rows) > 0:
        rowDict = {"playername": rows[0][0],
            "email": rows[0][1],
            "playerid": rows[0][2]
            }
    
    return rowDict

def updateProfile(admissionnumber, playername, email):
    isupdateOK = False

    try:
        strSql = "UPDATE Players SET \
                name = ?, \
                email = ? \
            WHERE admissionnumber = ?"
        data_tuple = (playername, email, admissionnumber)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)
        conn.commit()

        cur.close()
        conn.close()

        isupdateOK = True
    except Exception as ex:
        print ("updateProfile():", ex)

    return isupdateOK

def UpdatePassword(admno, npasswd1):
    isUpdateOK = True

    try:
        strSql = "UPDATE Players SET \
                password = ? \
            WHERE admissionnumber = ?"
        data_tuple = (npasswd1, admno)

        conn,  cur = opendb()

        cur.execute(strSql, data_tuple)

        conn.commit()

        cur.close()
        conn.close()
    except Exception as ex:
        print ("UpdatePassword():", ex)
        isUpdateOK = False

    return isUpdateOK

def getAnswer(competition_name, qid):
    conn,  cur = opendb()
    strSql = "SELECT ChoiceAnswer FROM QuestionBank WHERE Qid = ? AND CompetitionName = ?"
    data_tuple = (qid, competition_name)

    cur.execute(strSql, data_tuple)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    answer = ""

    if len(rows) > 0:
        answer = rows[0][0]
    
    return answer

def saveOTP(admno, otpnum, otpvalidtilltime):
    isSaveOK = False
    
    try:
        strSql = "DELETE \
                    FROM PlayerOtp \
                    WHERE PlayerId = ?"
        data_tuple = (admno,)

        conn, cur = opendb()
        print(strSql, data_tuple)
        cur.execute(strSql, data_tuple)
        conn.commit()

        strSql = "INSERT INTO PlayerOtp (PlayerId, OTP, OTPValidTill) \
                    VALUES (?,?,datetime(?))"
        
        data_tuple = (admno, otpnum, otpvalidtilltime)
        print (strSql, data_tuple)

        cur.execute(strSql, data_tuple)
        conn.commit()
    
        cur.close()
        conn.close()

        isSaveOK = True
    except Exception as ex:
        print("saveOTP:", ex)
    
    return isSaveOK

def IsOTPValid(admno, usrotp):
    isOtpOK = False

    try:
        curdatetime =  datetime.datetime.now()

        strSql = "SELECT OTPValidTill \
                FROM PlayerOtp \
                WHERE PlayerId = ? AND \
                    OTP = ? AND \
                    datetime(OTPValidTill) >= datetime(?)"

        data_tuple = (admno, usrotp, curdatetime)

        conn, cur = opendb()

        cur.execute(strSql, data_tuple)
        rows = cur.fetchall()
        
        cur.close()
        conn.close()

        if len(rows) > 0:
            isOtpOK = True
    except Exception as ex:
        print("IsOTPValid():", ex)
    
    return isOtpOK

def import_csv_data(csv_file_name, table_name, isHeaderRowPresent=True):
    isImportOK = False

    try:
        # reading csv file 
        with open(csv_file_name, 'r') as csvfile:
            columnNames = []
            sql = ""

            # creating a csv reader object 
            csvreader = csv.reader(csvfile) 
            
            # extracting field names through first row 
            if isHeaderRowPresent:
                columnNames = next(csvreader) 

            # initializing database
            conn, cur = opendb()
            
            # extracting each data row one by one 
            for row in csvreader:
                sql = "INSERT INTO " + table_name + "(" + ', '.join(column for column in columnNames) + ") \
                            VALUES (" + ', '.join("?" for column in columnNames) + ")"
                
                data_tuple = tuple(row)

                cur.execute(sql, data_tuple)
                    
            conn.commit()

            cur.close()
            conn.close()

            isImportOK = True
    except Exception as e:
        print("csv import error!", e)
    
    return isImportOK

def getRegistrationStatus(admno):
    strSql = "SELECT classid FROM Admissions WHERE admissionnumber = ?"
    data_tuple = (admno,)
    conn, cur = opendb()

    cur.execute(strSql, data_tuple)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    classid = ""
    if len(rows) > 0:
        classid = str(rows[0][0])
    
    return classid

def getRegistrations():
    conn,  cur = opendb()
    sql = "SELECT admissionnumber, name, email, mobile, classid, userconfirmedon FROM Players WHERE adminconfirmedon IS NULL AND NOT EXISTS (SELECT 1 FROM Teachers WHERE teacherid = players.admissionnumber)"
    cur.execute(sql)
    rows = cur.fetchall()
    rowCount = len(rows)
    cur.close()
    conn.close()
    return rows, rowCount

def adminConfirmRegistration(admno, admin_confrm_date):
    isconfrmregOK = False

    try:
        strSql = "UPDATE Players SET \
                adminconfirmedon = datetime(?) \
            WHERE admissionnumber = ?"
        
        data_tuple = (admin_confrm_date, admno)

        conn,  cur = opendb()

        cur.execute(strSql, data_tuple)
        conn.commit()

        cur.close()
        conn.close()
        
        isconfrmregOK = True
    except Exception as ex:
        print ("confirmRegistration()", ex)

    return isconfrmregOK

def userConfirmRegistration(admno, regdate):
    isconfrmregOK = False

    try:
        strSql = "SELECT COUNT(*) \
            FROM Players \
            WHERE admissionnumber = ? \
            AND registeredon = ?"
        
        data_tuple = (admno, regdate)

        conn,  cur = opendb()

        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()
        
        if len(rows) > 0:
            isconfrmregOK = True
    except Exception as ex:
        print ("userConfirmRegistration", ex)

    return isconfrmregOK

def getAssessmentList(admno):
    strSql = "SELECT c.name, StartedOn, EndingOn \
        FROM Competition c \
        WHERE NOT EXISTS (SELECT 1 \
                            FROM PlayerResponse pr \
                            WHERE pr.competitionname = c.name AND \
                            pr. PlayerId = ?) AND \
        datetime(c.EndingOn) >= datetime('now', 'localtime') AND \
        datetime('now', 'localtime') >=  datetime(c.StartedOn)"
    
    data_tuple = (admno,)

    conn,  cur = opendb()
    cur.execute(strSql, data_tuple)

    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows

def authorize(userid, competitionname, authtype):
    isAuthorized = False

    try:
        if authtype == utility.Authorization.TEACHER:
            strSql = "SELECT count(1) \
                        FROM Teachers t, Competition cm \
                        WHERE cm.name = ? AND \
                        t.teacherid = ? AND \
                        cm.classid = t.classid"
            data_tuple = (competitionname, userid)

            conn,  cur = opendb()
            cur.execute(strSql, data_tuple)

            rows = cur.fetchall()

            cur.close()
            conn.close()

            if len(rows) > 0:
                isAuthorized = True
    except Exception as ex:
        print ("Exception: authorize()", ex)

    return isAuthorized

def removeAssessment(assessment):
    isremoved = False

    try:
        strSql = "DELETE \
                    FROM QuestionBank \
                    WHERE CompetitionName = ? \
                    AND NOT EXISTS (SELECT 1 \
                                    FROM PlayerResponse pr \
                                    WHERE QuestionBank.CompetitionName = pr.competitionname)"
        data_tuple = (assessment,)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        strSql = "DELETE \
                    FROM Competition \
                    WHERE name = ? \
                    AND NOT EXISTS (SELECT 1 \
                                    FROM PlayerResponse pr \
                                    WHERE Competition.name = pr.competitionname)"
        cur.execute(strSql, data_tuple)
        conn.commit()

        cur.close()
        conn.close()
        
        isremoved = True
    except Exception as ex:
        print ("Exception: removeAssessment()", ex)

    return isremoved

def getTeacherAssessmentRankReport(teacherid):
    strSql = "SELECT name, pr.competitionname as competionname, sum(points) as totalpoints, \
        NULL as pointrank,  max(datetime(SubmittedOn)) As submittedon \
        FROM PlayerResponse pr, Players p, Teachers t, Class c \
        WHERE t.teacherid = ? AND \
		t.teacherid = c.teacherid AND \
		c.classid = p.classid AND \
		p.admissionnumber = pr.PlayerId AND \
        pr.SubmittedOn IS NOT NULL \
        GROUP BY name, pr.competitionname \
        ORDER BY pr.competitionname, sum(Points) DESC, SubmittedOn ASC"

    data_tuple = (teacherid,)

    conn,  cur = opendb()
    cur.execute(strSql, data_tuple)
    
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

    rank_lst = calculateRanks(list(rows))
    # print(rank_lst)
    return rank_lst

def isTeacher(loginid):
    isteacherfound = False

    try:
        strSql = "SELECT 1 \
            FROM Teachers \
            WHERE teacherid = ?"

        data_tuple = (loginid,)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        if len(rows) > 0:
            isteacherfound = True
    except Exception as ex:
        print ("Exception: isTeacher()", ex)

    return isteacherfound

def getTeacherClasses(loginid):
    try:
        strSql = "SELECT DISTINCT classid \
            FROM ClassTeachers \
            WHERE teacherid = ? AND \
                ClassId <> 'All' \
            ORDER BY classid"

        data_tuple = (loginid,)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows
    except Exception as ex:
        print ("Exception: getTeacherClasses()", ex)

def getClassAssessments(classselected):
    try:
        strSql = "SELECT name \
            FROM Competition \
            WHERE classid = ? \
            ORDER BY name"

        data_tuple = (str(classselected),)
       
        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows
    except Exception as ex:
        print ("Exception: getClassAssessments()", ex)

def getClassAssessmentStudents(classselected, assessmentselected):
    try:
        strSql = "SELECT row_number() OVER (order by p.name) row_num, \
                    p.name, \
                    sum(pr.points) as score, \
                    NULL as pointrank, \
                    max(datetime(pr.SubmittedOn)) As submittedon \
                FROM Players p LEFT JOIN PlayerResponse pr ON \
                pr.PlayerId = p.admissionnumber, Competition c \
                WHERE c.name = ? AND \
                c.classid = ? AND \
                pr.competitionname = c.name AND \
                NOT EXISTS (SELECT 1 FROM Teachers t WHERE t.teacherid = p.admissionnumber) \
                GROUP BY p.name \
                ORDER BY row_num"

        data_tuple = (assessmentselected, str(classselected))

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        rankrows = calculateClassAssessmentStudentRanks(list(rows))

        return rankrows
    except Exception as ex:
        print ("Exception: getClassAssessmentStudents()", ex)

def getClassStudents(classselected):
    try:
        strSql = "SELECT admissionnumber, name \
            FROM Players \
            WHERE classid = ?"

        data_tuple = (str(classselected),)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows
    except Exception as ex:
        print ("Exception: getClassStudents()", ex)

def getClassStudentAssessments(classselected, studentselected):
    try:
        strSql = "SELECT row_number() OVER (order by c.name) row_num, \
                    c.name, \
                    sum(pr.points) as score, \
                    NULL as pointrank, \
                    max(datetime(pr.SubmittedOn)) As submittedon \
                FROM Competition c LEFT JOIN PlayerResponse pr ON \
                    c.name = pr.competitionname	\
                WHERE c.classid = ? AND \
                    pr.PlayerId = ? \
                GROUP BY c.name \
                ORDER BY score DESC"

        data_tuple = (str(classselected), studentselected)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        rankrows = calculateClassAssessmentStudentRanks(list(rows))

        return rankrows
    except Exception as ex:
        print ("Exception: getClassStudentAssessments()", ex)

def getClassStudentAssessmentResponse(classselected, studentselected, assessmentselected):
    try:
        strSql = "SELECT pr.QId, pr.Question, q.ChoiceAnswer, pr.ResponseChoice, pr.Points \
                    FROM QuestionBank q, PlayerResponse pr \
                    WHERE q.classid = ? AND \
                    q.competitionname = ? AND \
                    pr.PlayerId = ? AND \
                    q.competitionname = pr.competitionname AND \
                    q.Qid = pr.QId"

        data_tuple = (str(classselected), assessmentselected, studentselected)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows
    except Exception as ex:
        print ("Exception: getClassStudentAssessmentResponse()", ex)

def unregisterPlayer(playerid, isunconfirmed = False):
    isunregisterok = False

    try:
        strSql = "DELETE \
            FROM Players \
            WHERE admissionnumber = ?"
        
        if isunconfirmed:
            strSql = strSql + " AND userconfirmedon IS NULL"

        data_tuple = (playerid,)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)
        conn.commit()

        rows = cur.fetchall()

        cur.close()
        conn.close()

        if len(rows) > 0:
            isunregisterok = True
    except Exception as ex:
        print ("Exception: unregisterPlayer()", ex)

    return isunregisterok

def getUserEmail(admno):
    emailto = ""

    strSql = "SELECT email FROM Players WHERE admissionnumber = ?"
    data_tuple = (admno,)

    conn,  cur = opendb()

    cur.execute(strSql, data_tuple)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()

    if len(rows) > 0:
        emailto = rows[0][0]

    return emailto

def isUserConfirmation(admno, userconfirmedon):
    isupdateuserreg = False

    try:
        strSql = "UPDATE Players SET \
                userconfirmedon = ? \
            WHERE admissionnumber = ?"

        data_tuple = (str(userconfirmedon), admno)
        
        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)
        conn.commit()

        cur.close()
        conn.close()
        
        isupdateuserreg = True
    except Exception as ex:
        print("isUserConfirmation()", ex)

    return isupdateuserreg

def isAdminConfirmation(admno):
    isupdateadminreg = False

    try:
        strSql = "SELECT 1 \
            FROM Players \
            WHERE admissionnumber = ? AND \
            adminconfirmedon IS NOT NULL"

        data_tuple = (admno,)
        
        conn,  cur = opendb()

        cur.execute(strSql, data_tuple)
        rows = cur.fetchall()

        cur.close()
        conn.close()
        
        if len(rows) > 0:
            isupdateadminreg = True
    except Exception as ex:
        print("isAdminConfirmation()", ex)

    return isupdateadminreg

def getAssessmentToRemove(teacherid):
    strSql = "SELECT name \
        FROM Competition c, Teachers t \
        WHERE c.classid = t.classid AND \
        t.teacherid = ? AND \
        NOT EXISTS (SELECT 1 \
			FROM PlayerResponse pr \
			WHERE pr.competitionname = c.name)"
    
    data_tuple = (teacherid,)

    conn,  cur = opendb()
    cur.execute(strSql, data_tuple)

    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows


def createAssessmentWithFile(classname, assesementname, description, startson, endson, note, filename, imagefilenames):
    isassessmentcreated = False
    try:
        strSql = "INSERT INTO Competition (name, description, startedon, endingon, notes, classid, qpaperfile) \
                        VALUES(?, ?, ?, ?, ?, ?, ?)"

        data_tuple = (assesementname, description, startson, endson, note, classname, filename)
        
        conn, cur = opendb()
    
        cur.execute(strSql, data_tuple)
        conn.commit()

        strSql = "INSERT INTO QuestionPaperFiles (qpaperfile, qpaperimagefile) values (?, ?)"
        
        data_tuple = imagefilenames
        conn.executemany(strSql, data_tuple)

        conn.commit()
        cur.close()
        conn.close()

        isassessmentcreated = True
    except Exception as ex:
        print("createAssessmentWithFile()", ex)
    
    return isassessmentcreated


def getClasses():
    try:
        strSql = "SELECT classid \
            FROM ClassTeachers \
            WHERE ClassId <> 'All'"

        conn,  cur = opendb()
        cur.execute(strSql)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows
    except Exception as ex:
        print ("getClasses()", ex)

def getStudentDetail(studentid):
    try:
        strSql = "SELECT admissionnumber, name, email, mobile \
            FROM Players \
            WHERE admissionnumber = ?"
        
        data_tuple = (studentid,)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows
    except Exception as ex:
        print ("getStudentDetail()", ex)


def getAllCompetitionNames():
    sql = "SELECT Name FROM competition"

    conn, cur = opendb()

    cur.execute(sql)
    dbrows = cur.fetchall()

    cur.close()
    conn.close()

    return dbrows

def updateAssessmentDate(assessment, endson):
    isupdateok = False

    try:
        strSql = "UPDATE Competition \
                    SET EndingOn = datetime(?) \
                    WHERE Name = ?"
        data_tuple = (endson, assessment)

        print (strSql, data_tuple)

        conn,  cur = opendb()

        cur.execute(strSql, data_tuple)

        conn.commit()

        cur.close()
        conn.close()

        isupdateok = True
    except Exception as ex:
        print ("updateAssessmentDate():", ex)

    return isupdateok

def getTeacherAssessment(teacherid):
    strSql = "SELECT name \
        FROM Competition c, Teachers t \
        WHERE c.classid = t.classid AND \
        t.teacherid = ?"
    
    data_tuple = (teacherid,)

    conn,  cur = opendb()
    cur.execute(strSql, data_tuple)

    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows

def getQpaperImages(assessment):
    try:
        strSql = "SELECT qp.qpaperfile, qpaperimagefile \
            FROM QuestionPaperFiles qp, Competition c \
            WHERE name = ? AND \
            qp.qpaperfile = c. qpaperfile"

        data_tuple = (assessment,)

        conn,  cur = opendb()
        cur.execute(strSql, data_tuple)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows
    except Exception as ex:
        print ("getQpaperImages()", ex)

def getStudentExpiredCompetitions(studentid):
    try:
        strSql = "SELECT c.name, datetime(EndingOn), datetime('now', 'localtime') \
                    FROM Competition c, Players p \
                    WHERE p.admissionnumber = ? AND \
                    c.classid = p.classid AND \
                    datetime(endingon) < datetime('now', 'localtime')"
        data_tuple = (studentid,)

        conn, cur = opendb()

        cur.execute(strSql, data_tuple)

        dbrows = cur.fetchall()

        cur.close()
        conn.close()

        return dbrows
    except Exception as ex:
        print ("getStudentExpiredCompetitions():", ex)
