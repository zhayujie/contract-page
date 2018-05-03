from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return render_template('kun.html', n=range(1, 9)), 200

if __name__ == '__main__':
    app.run(port=5000)
