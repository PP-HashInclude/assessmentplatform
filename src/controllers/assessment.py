from flask import render_template

from common import utility, config

def assessment():
    return render_template("assessment.html")