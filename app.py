# app.py
import time
from flask import Flask
from flask import make_response
from pipeline import run

app = Flask(__name__)


@app.route("/")
def start():
    # create response
    response = make_response(run())
    # filename
    time_file_name = time.strftime("%Y-%m-%d-%H-%M-%S")
    # set headers
    response.headers.set('Content-Type', 'text/xml')
    response.headers.set('Content-Disposition', 'attachment', filename='trend-seminar-xml-%s.xml' % time_file_name)
    # return response
    return response
