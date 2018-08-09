# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect
import db

app = Flask(__name__)

@app.route('/', methods=['GET'])
def form():
    return render_template('index.html'), 200

@app.route('/signup', methods=['GET', 'POST'])
def enroll():
    if request.method == 'GET':
        return render_template('enroll.html'), 200
    else:
        username = request.form.get('form-username', default='user')
        password = request.form.get('form-password', default='pass')
        if db.get_pass(username):
            return 'existed'
        else:
            db.save_user(username, password)
            return 'ok'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html'), 200
    else:
        username = request.form.get('form-username', default='user')
        password = request.form.get('form-password', default='pass')
        db_pass = db.get_pass(username)
        if not db_pass:
            return 'none'
        elif db_pass != password:
            return 'wrong'
        else:
            return 'right'

@app.route('/user', methods=['GET', 'POST'])
def login_success():
    username = request.args.get('name', default='user')
    return render_template('user.html', username=username), 200

@app.route('/file', methods=['GET'])
def show_file():
    username = request.args.get('name', default='user')
    return render_template('file.html', username=username), 200

@app.route('/contract', methods=['GET'])
def contract_form():
    username = request.args.get('name', default='user')
    return render_template('contract.html', username=username), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
