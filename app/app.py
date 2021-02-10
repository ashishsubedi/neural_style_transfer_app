from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from os import path
from uuid import uuid4
import json
from .celery import make_celery

from app.neural_style_transfer import perform_transformation

app = Flask(__name__)

UPLOAD_FOLDER = path.abspath('uploads')
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}

#CONFIGS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

celery = make_celery(app)
print(celery)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    task = add.delay(1,2)
    print(task,task.id)
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
        content_path = path.join(app.config['UPLOAD_FOLDER'],str(uuid4())+secure_filename(content.filename))
        style_path = path.join(app.config['UPLOAD_FOLDER'],str(uuid4())+secure_filename(style.filename))
        content.save(content_path)
        style.save(style_path)

        output_path = str(uuid4())+secure_filename(content.filename)

        task = start_style_transfer.delay(content_path,style_path,output_path)

        return json.dumps({
            'status':'success',
            'code': 201,
            'message': f'Here is your id. Search for it later to get your image. {task.id}'
        })
    else:
        return json.dumps({
            'status':'fail',
            'code': 501,
        })


@celery.task()
def add(a,b):
    return a+b

@celery.task(bind=True)
def start_style_transfer(self,*args):
    self.update_state(state='PROGRESS')

