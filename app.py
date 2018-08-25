# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect
import json
import util
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

@app.route('/user', methods=['POST'])
def login_success():
    username = request.form.get('username', default='user')
    return render_template('user.html', username=username), 200

@app.route('/file', methods=['POST'])
def show_file():
    username = request.form.get('username', default='user')
    contracts = db.get_user_contracts(username)
    return render_template('file.html', username=username, contracts=contracts), 200

@app.route('/contract', methods=['POST'])
def contract_form():
    username = request.form.get('username', default='user')
    return render_template('contract.html', username=username), 200

@app.route('/save', methods=['POST'])
def save():
    args = request.get_json() 
    db.save_contract(args['username'], args['contract_name'], args['contract_id'], args['party_a'], args['sig_a'],
        args['party_b'], args['sig_b'], args['valid_time'], json.dumps(args['content']))
    return 'success'

@app.route('/query', methods=['POST'])
def query():
    username = request.form.get('username', default='user')
    contract_id = request.form.get('contract_id', default='id')
    contract = db.get_contract(username, contract_id)
    l = json.loads(contract[9])
    return render_template('contract-content.html', contract=contract, list=l), 200


if __name__ == '__main__':
    host = util.get_config()["host"]
    port = int(util.get_config()["port"])
    debug = util.get_config()["debug"]
    if debug == "True":
        debug = True
    else:
        debug = False
    print(debug)
    app.run(host=host, port=port, threaded=True, debug=debug)
