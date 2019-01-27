from flask import Flask, jsonify, render_template
from suggest import suggest, suggest_list
import requests
import os

app = Flask(__name__)

MW_KEY = os.getenv('MW_API_KEY')
MW_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={key}'


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
    word = word.lower()
    def_url = MW_URL.format(word = word, key = MW_KEY)
    res = requests.get(def_url)
    matches = [defn for defn in res.json() if defn['hwi']['hw'] == word]
    return jsonify(matches)
