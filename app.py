# coding=utf8
from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
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

if __name__ == '__main__':
    app.run(port=5000)
