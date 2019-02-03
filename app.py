from flask import Flask, jsonify, render_template, request
from suggest import suggest_list
from define import define
from loguru import logger

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/suggest/list/<input>.json')
def list_suggest(input):
    limit = request.args.get('limit', default=10, type=int)
    suggestions = suggest_list(input, limit)
    if suggestions:
        logger.info(f"{len(suggestions)} suggestions for {input}")
        logger.info(f"{input} suggestions: {suggestions}")
    else:
        logger.debug(f"No suggestions returned for {input}")
    return jsonify({'input': input, 'suggestions': suggestions})


@app.route('/define/<word>.json')
def get_definition(word):
    defs = define(word)
    if defs:
        logger.info(f"{len(defs)} matching definitions returned for {word}.")
        logger.info(f"{word} definitions: {defs}")
    else:
        logger.debug(f"No definitions found for {word}")

    return jsonify(defs)
