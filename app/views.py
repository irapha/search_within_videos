from flask import redirect, render_template, render_template_string, Blueprint
from flask import request, url_for, flash, Response
import time

import utils.vision as v
from app.init_app import app

@app.route("/")
def home_page():
    return render_template('pages/home_page.html')

@app.route("/add")
def add():
    return render_template('pages/add_video.html')

@app.route("/add_video", methods=['POST'])
def add_video():
    url = request.form["url"]
    frames = v.get_labels_from_url(url)
    return frames

@app.route('/progress')
def progress():
    def generate():
        x = 0
        while x < 100:
            print x
            x = x + 10
            time.sleep(0.2)
            yield "data:" + str(x) + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')
