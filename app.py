from flask import Flask, jsonify, render_template
from suggest import suggest

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/suggest/<word>.json')
def suggest_word(word):
    return jsonify(suggest(word))
