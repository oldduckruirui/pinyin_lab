import os
import math
from . import stats

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(SRC_DIR, 'corpus')
RES_DIR = os.path.join(SRC_DIR, 'res')


def predict(py_text, alpha=1e-7, epsilon=1e-233):
    py_list = py_text.split()

    one_word, two_word = stats.prob_one_word, stats.prob_two_word

    def calc_one_word_prob(py, word):
        return one_word[py].get(word, 0)

    def calc_two_word_prob(word_pair):
        return two_word.get(word_pair, 0)

    for i, py in enumerate(py_list):
        if i == 0:
            path = {word: word for word in one_word[py]}
            f_prev = {word: math.log(epsilon + calc_one_word_prob(py, word))
                      for word in one_word[py]}
        else:
            f_cur = {}
            new_path = {}
            # update f_cur using f_prev
            for word1 in f_prev:
                for word2 in one_word[py]:
                    prob = f_prev[word1] + math.log(epsilon + alpha * calc_one_word_prob(py, word2) +
                                                    (1 - alpha) * calc_two_word_prob(word1+word2))
                    if word2 not in f_cur or prob > f_cur[word2]:
                        f_cur[word2] = prob
                        new_path[word2] = path[word1] + word2
            f_prev = f_cur
            path = new_path
    f_prev["#"] = math.log(epsilon) * len(py_list)
    path["#"] = "#"
    last_choice = max(f_prev, key=f_prev.get)
    return path[last_choice]
