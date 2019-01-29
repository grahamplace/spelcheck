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
        CORPUS[word.lower()] = idx
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
            edits.append(word[:i] + letter + word[i+1:])
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
    return two_edits


# For a given input word, suggest a reasonable alternative
def suggest(word: str) -> str:
    word = word.lower()

    # If the word is already "correct", return it
    if word in CORPUS:
        return word

    # Next best is an edit distance of one,
    #   picking the permutation that appears most in corpus
    one_edits = clean_with_corpus(compute_ones(word))
    if one_edits:
        print(f'All options: {one_edits}\n')
        vals = {word: CORPUS[word] for word in one_edits}
        return sorted(vals, key=vals.get, reverse=True)[0]

    # Next best is the same, but with edit distance two from original word
    two_edits = clean_with_corpus(compute_twos(word))
    if two_edits:
        print(f'All options: {two_edits}\n')
        vals = {word: CORPUS[word] for word in two_edits}
        return sorted(vals, key=vals.get, reverse=True)[0]

    # We don't suggest anything if there isn't a word in the corpus with
    #   <= 2 Levenshtein ED from word
    return ''


def suggest_list(word: str) -> list:
    word = word.lower()

    # We don't suggest anything if there isn't a word in the corpus with
    #   <= 2 Levenshtein ED from word
    suggestions = []

    # If the word is already "correct", add to suggestions
    if word in CORPUS:
        suggestions.append(word)

    # Next best is an edit distance of one
    suggestions.extend(clean_with_corpus(compute_ones(word)))

    # Next best is edit distance two from original word
    suggestions.extend(clean_with_corpus(compute_twos(word)))

    # Dedupe
    suggestions = list(set(suggestions))

    return [word] + sorted(suggestions, key=CORPUS.get)



# to run on import
index_corpus('corpus.txt')
