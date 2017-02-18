import io
import os
from flask import Flask
app = Flask(__name__)
from google.cloud import vision

@app.route("/")
def hello_world():
    client = vision.Client('search-within-video')
    
    img = client.image(filename='img/dood.png')
    
    labels = img.detect_labels()
    
    returnStr = "";
    for label in labels:
        returnStr += str(label.description) + " - " + str(label.score) + '\n'
    return returnStr
