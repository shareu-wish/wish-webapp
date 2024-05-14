from flask import Flask
from flask import render_template
import json
from flask import url_for
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return render_template('registration_2.html')
    else:
        return render_template('home_2.html')

@app.route('/1', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        text = request.form['text']
        return render_template('registration_2.html', text=text)
    else:
        return render_template('registration_2.html')

@app.route('/12')
def main():
    return render_template("home_2.html")


@app.route('/')
@app.route('/warning')
def home():
    return render_template("warning_2.html")


@app.route('/registration')
def to_pay():
    return render_template("registration_2.html")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
