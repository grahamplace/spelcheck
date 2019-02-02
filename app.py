from flask import Flask, jsonify, render_template
from suggest import suggest, suggest_list
from define import define

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/suggest/word/<input_word>.json')
def word_suggest(input_word):
    return jsonify(suggest(input_word))


@app.route('/suggest/list/<input_word>.json')
def list_suggest(input_word):
    return jsonify(suggest_list(input_word))


@app.route('/define/<word>.json')
def get_definition(word):
    return jsonify(define(word))
