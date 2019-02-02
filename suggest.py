import re
from collections import defaultdict

CORPUS = defaultdict(int)
ALPHA = 'abcdefghijklmnopqrstuvwxyz'


# Parse the corpus file into a dict that maps word: # occurences in corpus
def index_corpus(filename: str) -> dict:
    with open(filename) as f:
        corpus = f.read()
    corpus.replace('\n', ' ')
    corpus = re.sub('[^a-zA-Z ]+', ' ', corpus)
    corpus = corpus.split(' ')
    for idx, word in enumerate(corpus):
        CORPUS[word.lower()] = min(idx, CORPUS[word.lower()])
    CORPUS.pop('')


# clean a list of words by keeping only those present
#   in the corpus at least once
def clean_with_corpus(words: list) -> list:
    return [w for w in words if w in CORPUS]


# For a given input word, compute the set of permutations
#   made by deleting 1 character
def compute_deletions(word: str) -> list:
    edits = []
    for i in range(len(word)):
        edits.append(word[:i] + word[i+1:])
    return edits


# For a given input word, compute the set of permutations
#   made by inserting 1 character
def compute_insertions(word: str) -> list:
    edits = []
    for i in range(len(word)):
        for letter in ALPHA:
            edits.append(word[:i] + letter + word[i:])
    return edits


# For a given input word, compute the set of permutations made
#   by substituting 1 char with 1 other char
def compute_substitutions(word: str) -> list:
    edits = []
    for i in range(len(word)):
        for letter in ALPHA:
            new_word = word[:i] + letter + word[i+1:]
            if new_word != word:
                edits.append(new_word)
    return edits


# For a given input word, compute the set of all possible strings
#   with edit distance 1 from word
def compute_ones(word: str) -> list:
    edits = []
    edits.extend(compute_deletions(word))
    edits.extend(compute_insertions(word))
    edits.extend(compute_substitutions(word))
    edits = list(set(edits))  # dedupe
    return edits


# For a given input word, compute the set of all possible strings
#   with edit distance 1 from word
def compute_twos(word: str) -> list:
    two_edits = []
    one_edits = compute_ones(word)
    for edit in one_edits:
        two_edits.extend(compute_ones(edit))
    two_edits = list(set(two_edits))  # dedupe
    two_edits.remove(word)
    return two_edits


def suggest_list(word: str, limit=10) -> list:
    word = word.lower()

    suggestions = {}

    # Next best is an edit distance of one
    ones = clean_with_corpus(compute_ones(word))
    for sugg in ones:
        if len(sugg) > 2:
            suggestions[sugg] = (1, CORPUS[sugg])

    # Next best is edit distance two from original word
    twos = clean_with_corpus(compute_twos(word))
    for sugg in twos:
        if not suggestions.get(sugg, False) and len(sugg) > 2:
            suggestions[sugg] = (2, CORPUS[sugg])

    return sorted(suggestions, key=suggestions.get)[:limit]



# to run on import
index_corpus('corpus.txt')
