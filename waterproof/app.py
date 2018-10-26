# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect
import json
import util

app = Flask(__name__)

@app.route('/', methods=['GET'])
def show_home():
    return render_template('index.html'), 200

if __name__ == '__main__':
    host = util.get_config()["host"]
    port = int(util.get_config()["port"])
    debug = util.get_config()["debug"]
    if debug == "True":
        debug = True
    else:
        debug = False
    app.run(host=host, port=port, threaded=True, debug=debug)
