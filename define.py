import os
import re
import requests

MW_KEY = os.getenv('MW_API_KEY')
MW_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={key}'


def get_mw_response(word: str):
    word = word.lower()
    def_url = MW_URL.format(word = word, key = MW_KEY)
    return requests.get(def_url)


def get_res_matches(word: str, res) -> list:
    matches = []
    for defn in res.json():
        # no result found returns a list of strings
        if not isinstance(defn, dict):
            return jsonify([])
        if not defn['shortdef']:
            continue
        elif (defn['meta']['id']).split(':')[0] == word:
            matches.append(defn)

    # fallback on everything with a def
    if not matches:
        matches = [m for m in res.json() if m['shortdef']]

    return matches


def clean_matches(matches):
    defs = []

    for m in matches:
        defn = {}

        # add a cleaned 'word' to each defn dict
        defn['word'] = m['meta']['id'].split(':')[0]

        # cleanup shortdef
        shortdefs = m['shortdef']
        def_str = ''
        for i, sd in enumerate(shortdefs):
            def_str += f'{i+1}. {sd}<br><br>'
        defn['definition_str'] = def_str

        # add part of speech
        defn['part_of_speech'] = m['fl']

        defs.append(defn)

    return defs


def define(word: str) -> list:
    res = get_mw_response(word)
    matches = get_res_matches(word, res)
    defs = clean_matches(matches)
    return defs
