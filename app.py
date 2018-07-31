from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def signin_form():
    return render_template('form.html'), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
