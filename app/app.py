from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from os import path
from uuid import uuid4
import json
app = Flask(__name__)

UPLOAD_FOLDER = path.abspath('uploads')
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload/',methods=['POST'])
def upload():
    print(request.files)
    if 'content' not in request.files or 'style' not in request.files:
        return "<h1> You must have both content and style image</h1>"
    content = request.files['content']
    style = request.files['style']
    if content.filename == '' or style.filename=='':
        return "<h1> You must have both content and style image</h1>"

    if content and style and allowed_file(content.filename) and allowed_file(style.filename):
        content.save(path.join(app.config['UPLOAD_FOLDER'],str(uuid4())+secure_filename(content.filename)))
        style.save(path.join(app.config['UPLOAD_FOLDER'],str(uuid4())+secure_filename(style.filename)))

    return json.dumps({
        'status':'success',
        'code': 201,
        'message': 'Will contain content id'
    })