from flask import Flask
from flask import render_template
import json
from flask import url_for
from flask import request

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template("klim's_test_logpage.html")

@app.route('/main')
def main():
    return render_template("klim's_main.html")

@app.route('/to_pay')
def to_pay():
    return render_template("klim's_bofore_pay.html")

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')