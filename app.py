from flask import Flask, jsonify
from suggest import suggest


app = Flask(__name__)


@app.route('/suggest/<word>')
def suggest_word(word):
    return jsonify(suggest(word))
