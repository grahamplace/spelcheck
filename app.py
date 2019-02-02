from flask import Flask, jsonify, render_template, request
from suggest import suggest_list
from define import define
from loguru import logger

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/suggest/list/<input_word>.json')
def list_suggest(input_word):
    limit = request.args.get('limit', default=10, type=int)
    suggestions = suggest_list(input_word, limit)
    logger.info(f"{len(suggestions)} suggestions for {input_word}")
    logger.info(f"{input_word} suggestions: {suggestions}")
    return jsonify(suggestions)


@app.route('/define/<word>.json')
def get_definition(word):
    defs = define(word)
    logger.info(f"{len(defs)} matching definitions returned for {word}.")
    logger.info(f"{word} definitions: {defs}")
    return jsonify(defs)
