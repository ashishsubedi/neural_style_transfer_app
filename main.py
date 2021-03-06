from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import os
from os import path
from uuid import uuid4
import json

from tasks import make_celery
from test import perform_ops
from neural_style_transfer import perform_transformation

app = Flask(__name__,
static_folder='uploads',)

UPLOAD_FOLDER = path.abspath('uploads')
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}


#CONFIGS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

celery = make_celery(app)

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
        content_path = path.join(app.config['UPLOAD_FOLDER'],str(uuid4())+secure_filename(content.filename))
        style_path = path.join(app.config['UPLOAD_FOLDER'],str(uuid4())+secure_filename(style.filename))
        content.save(content_path)
        style.save(style_path)
    
        output_path = path.join(app.config['UPLOAD_FOLDER'],str(uuid4())+secure_filename(content.filename))

        task = apply_style_transfer.delay(content_path,style_path,output_path)

        return {
            'status':'success',
            'code': 201,
            'message': f'Here is your id. Search for it later to get your image. {task}'
        }
    else:
        return {
            'status':'fail',
            'code': 501,
        }

@app.route('/status/<id>/',methods=['GET'])
def check_status(id=None):
    print(id)
    if not id:   
        return json.dumps({
            'status':'not done yet',
            'code': 501,
        })

    res = simple_prediction.AsyncResult(id)

    if res.state == 'SUCCESS':

        return {
            'res' : res.result,
            'state': res.state
        }
  

    else:
        return dict(

            state=res.state
        )

    

@celery.task()
def simple_prediction(img):
    res = int(perform_ops(img))
    return {'res': res}

@celery.task(bind=True)
def apply_style_transfer(self,*args):
    self.update_state(state="PROGRESS")
    c,s,output = perform_transformation(*args)
    self.update_state(state="COMPLETE")

    return {'status': "Task Complete",
        'c' :c,
        's':s,
        'output':os.path.relpath(output),
        'url': f'/{os.path.relpath(output)}'
    }


