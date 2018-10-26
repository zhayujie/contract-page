# -*- coding: utf8 -*-
from flask import Flask, render_template, request
import os
import requests
import json
from werkzeug import secure_filename

URL = "http://114.242.26.112:5009/test"
app = Flask(__name__)

@app.route('/', methods=['GET'])
def page():
    return '<h1>hello</h1>'



@app.route('/kun', methods=['GET'])
def hello():
	file_list = os.listdir('./static/kun')
	file_names = []
	for i in range(0, len(file_list)):
		file_name = file_list[i].split('.')[0]
		if file_name:
			file_names.append(file_name)
	return render_template('kun.html', file_names=file_names), 200

@app.route('/evolution', methods=['GET'])
def evolove():
    return render_template('evolve-image.html')

@app.route('/test', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
		
        if file:
            filename = secure_filename(file.filename)
            fp = './static/' + filename
            file.save(fp)
            fileob = {'file': (filename, open(fp, 'rb'),'image/jpeg')}
            l = requests.post(URL, files=({'file': open(fp, 'rb')}))
            l = l.json()
            if len(l) != 3:
            	return "Error"
            else:
                return render_template('result.html', l=l, filename=filename)
        else:
            return "No file"
   
    return render_template('upload.html')



if __name__ == '__main__':
    app.run(port=5000)
