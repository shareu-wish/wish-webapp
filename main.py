from flask import Flask
from flask import render_template
import json
from flask import url_for
from flask import request

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def index():
    return render_template("work.html")



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')