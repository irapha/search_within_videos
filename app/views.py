from flask import redirect, render_template, render_template_string, Blueprint
from flask import request, url_for, flash, Response, jsonify
import time
from app.utils import tag
from app.init_app import app
import random

from celery import Celery

celery = Celery(app.import_name, backend='redis://localhost:6379/0',
                broker='redis://localhost:6379/0')

#taskprogress = {}

@celery.task(bind=True)
def process_video(self, url):
    """Background task that runs a long function with progress reports."""
    def progress_cb(done, total):
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total})
    tag.tag_and_upload(url, progress_cb)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@app.route("/")
def home_page():
    return render_template('pages/home_page.html')

@app.route("/add")
def add():
    return render_template('pages/add_video.html')

@app.route("/add_video", methods=['POST'])
def add_video():
    url = request.form["url"]
    task = process_video.apply_async(args=[url])
    #taskprogress[task.id] = 0
    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

@app.route('/progress')
def progress():
    def generate():
        x = 0
        while x < 100:
            x = x + 10
            time.sleep(0.2)
            yield "data:" + str(x) + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')



@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = process_video.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
