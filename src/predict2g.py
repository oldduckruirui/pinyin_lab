import os
import sys
import math
import json
from . import stat

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(SRC_DIR, 'corpus')
RES_DIR = os.path.join(SRC_DIR, 'res')


def predict(pinyin_text, alpha=1e-6, epsilon=1e-233):
    pinyin_list = pinyin_text.split()

    one_word, two_word = stat.prob_one_word, stat.prob_two_word

    def calc_one_word_prob(pinyin, word):
        return one_word[pinyin].get(word, 0)

    def calc_two_word_prob(pinyin_text, word_pair):
        if pinyin_text not in two_word:
            return 0
        return two_word[pinyin_text].get(word_pair, 0)

    for i, pinyin in enumerate(pinyin_list):
        if i == 0:
            path = {word: word for word in one_word[pinyin]}
            f_prev = {word: math.log(epsilon + calc_one_word_prob(pinyin, word))
                      for word in one_word[pinyin]}
        else:
            f_cur = {}
            new_path = {}
            pinyin_text = pinyin_list[i-1] + " " + pinyin
            # update f_cur using f_prev
            for word1 in f_prev:
                for word2 in one_word[pinyin]:
                    prob = f_prev[word1] + math.log(epsilon + alpha * calc_one_word_prob(pinyin, word2) +
                                                    (1 - alpha) * calc_two_word_prob(pinyin_text, word1+word2))
                    if word2 not in f_cur or prob > f_cur[word2]:
                        f_cur[word2] = prob
                        new_path[word2] = path.get(word1, "") + word2
            f_prev = f_cur
            path = new_path

    last_choice = max(f_prev, key=f_prev.get)
    return path[last_choice]
