import os
from flask import Flask
from waitress import serve
from common import utility
from controllers import assessment, admin

app = Flask(__name__)

app.add_url_rule('/', view_func=assessment.assessment, methods=['GET', 'POST'])

#app.add_url_rule('/admin/assessments/<filename>', view_func=admin.post_assessment, methods=['POST'])
#app.add_url_rule('/admin/classes', view_func=admin.get_classes, methods=['GET'])

port = int(os.getenv('PORT', 5000))

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=port, debug=False)
    #opfile = utility.convert_pdf3("C:\\data\\PP\\Project\\Python\\ksoas\\src\\templates\\class12-csc-mt3.pdf", "C:\\data\\PP\\Project\\Python\\ksoas\\src\\static\\image")
    #print (opfile)
    serve(app, host='0.0.0.0', port=port)
