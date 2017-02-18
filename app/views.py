from flask import redirect, render_template, render_template_string, Blueprint
from flask import request, url_for, flash

import app.utils.vision as v
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
