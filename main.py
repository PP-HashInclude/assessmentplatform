from controllers import login, home, registration, quiz, leaderboard, account, about, competition, admin
from flask import Flask, session
from flask_session import Session
import os
from common import config, utility
from repositories import db

app = Flask(__name__)
app.secret_key = "mysecretkeyforquizapp"
app.config["SESSION_TYPE"] = "filesystem"

sess = Session()
sess.init_app(app)

app.add_url_rule('/', view_func=home.home)
app.add_url_rule('/competitions', view_func=competition.competitions, methods=['GET'])
app.add_url_rule('/competitionanswers', view_func=competition.competitionanswers, methods=['POST'])

app.add_url_rule('/about', view_func=about.about)

app.add_url_rule('/login', view_func=login.login, methods=['GET', 'POST'])
app.add_url_rule('/chklogin', view_func=login.chklogin, methods=['GET', 'POST'])
app.add_url_rule('/forgotpass', view_func=login.forgotpass, methods=['GET'])
app.add_url_rule('/genotp', view_func=login.genotp, methods=['POST'])
app.add_url_rule('/logout', view_func=login.logout, methods=['GET'])

app.add_url_rule("/signup", view_func=registration.signup, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=registration.register, methods=['POST'])
app.add_url_rule('/genpass', view_func=registration.genpass)
app.add_url_rule('/newpassupdate', view_func=registration.newpassupdate, methods=['POST'])
app.add_url_rule('/validateregistration', view_func=registration.validateregistration, methods=['GET', 'POST'])

app.add_url_rule('/question', view_func=quiz.question, methods=['GET'])
app.add_url_rule('/submit', view_func=quiz.submit, methods=['POST'])
app.add_url_rule('/assessment', view_func=quiz.assessment, methods=['GET'])
app.add_url_rule('/savesnap', view_func=quiz.savesnap, methods=['POST'])

app.add_url_rule('/leaderboard', view_func=leaderboard.leaderboard, methods=['GET', 'POST'])

app.add_url_rule('/account', view_func=account.account, methods=['GET'])
app.add_url_rule('/account', view_func=account.updateaccount, methods=['POST'])
app.add_url_rule('/account/resetpass', view_func=account.resetpassword, methods=['GET'])
app.add_url_rule('/account/resetpass', view_func=account.updatepassword, methods=['POST'])
app.add_url_rule('/account/checkregistration', view_func=account.checkregistration, methods=['GET', 'POST'])

app.add_url_rule('/admin/uploadassessment', view_func=admin.uploadassessment, methods=['GET', 'POST'])
app.add_url_rule('/admin/importdata', view_func=admin.importdata, methods=['GET', 'POST'])
app.add_url_rule('/admin/confirmregistration', view_func=admin.confirmregistration, methods=['GET', 'POST'])
app.add_url_rule('/admin/removeassessment', view_func=admin.removeassessment, methods=['POST'])
app.add_url_rule('/admin/classassessmentsum', view_func=admin.classassessmentsum, methods=['GET', 'POST'])
app.add_url_rule('/admin/classstudentsum', view_func=admin.classstudentsum, methods=['GET', 'POST'])
app.add_url_rule('/admin/studentassessmentdet', view_func=admin.studentassessmentdet, methods=['GET', 'POST'])
app.add_url_rule('/admin/updateassessmentdate', view_func=admin.updateassessmentdate, methods=['POST'])

port = int(os.getenv('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True, ssl_context=('adhoc'))
