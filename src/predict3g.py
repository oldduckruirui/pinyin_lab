import math
from . import stats


def predict(pinyin_text, alpha=1e-4, beta=1e-1, epsilon=1e-233):
    py_list = pinyin_text.split()

    one_word, two_word, first_two_word, three_word = stats.prob_one_word, stats.prob_two_word, stats.prob_first_two_word, stats.prob_three_word

    def calc_one_word_prob(py, word):
        return one_word[py].get(word, 0)

    def calc_two_word_prob(word_pair):
        return two_word.get(word_pair, 0)

    def calc_first_two_word_prob(py_text, word_pair):
        if py_text not in first_two_word:
            return 0
        return first_two_word[py_text].get(word_pair, 0)

    def calc_three_word_prob(word_tuple):
        return three_word.get(word_tuple, 0)

    # 2-gram
    f_path = {}
    f_prev = {}

    # 3-gram
    g_path = {}
    g_prev = {}

    for i, py in enumerate(py_list):
        if i == 0:
            for word in one_word[py]:
                f_prev[word] = math.log(epsilon + calc_one_word_prob(py, word))
                f_path[word] = word
        else:
            f_cur = {}
            f_new_path = {}
            if i == 1:
                # update f_cur using f_prev
                for word1 in f_prev:
                    for word2 in one_word[py]:
                        word_pair = word1+word2
                        p = f_prev[word1] + math.log(epsilon + alpha * calc_one_word_prob(py, word2) +
                                                     (1 - alpha) * calc_two_word_prob(word_pair))
                        if word_pair in two_word:
                            g_prev[word_pair] = p
                            g_path[word_pair] = word_pair
                        elif word2 not in f_cur or p > f_cur[word2]:
                            f_cur[word2] = p
                            f_new_path[word2] = word_pair

                py_text = py_list[i-1]+" "+py
                for word_pair in first_two_word.get(py_text, {}):
                    g_prev[word_pair] = math.log(epsilon +
                                                 calc_first_two_word_prob(py_text, word_pair))
                    g_path[word_pair] = word_pair
            else:
                g_cur = {}
                g_new_path = {}
                # update f_cur and g_cur using f_prev
                for word1 in f_prev:
                    for word2 in one_word[py]:
                        word_pair = word1+word2
                        p = f_prev[word1] + math.log(epsilon + beta * (alpha * calc_one_word_prob(py, word2)
                                                                       + (1 - alpha) * calc_two_word_prob(word_pair)))
                        if word_pair in two_word:
                            g_cur[word_pair] = p
                            g_new_path[word_pair] = f_path[word1] + word2
                        elif word2 not in f_cur or p > f_cur[word2]:
                            f_cur[word2] = p
                            f_new_path[word2] = f_path[word1] + word2
                # update f_cur and g_cur using g_prev
                for word_pair in g_prev:
                    for word3 in one_word[py]:
                        new_word_pair = word_pair[1]+word3
                        p = g_prev[word_pair] + math.log(epsilon + beta * (alpha * calc_one_word_prob(py, word3)
                                                                           + (1-alpha) * calc_two_word_prob(new_word_pair))
                                                         + (1 - beta) * calc_three_word_prob(word_pair+word3))
                        if new_word_pair in two_word:
                            if new_word_pair not in g_cur or p > g_cur[new_word_pair]:
                                g_cur[new_word_pair] = p
                                g_new_path[new_word_pair] = g_path[word_pair] + word3
                        elif word3 not in f_cur or p > f_cur[word3]:
                            f_cur[word3] = p
                            f_new_path[word3] = g_path[word_pair] + word3
                g_prev, g_path = g_cur, g_new_path
            f_prev, f_path = f_cur, f_new_path

    f_last_choice = max(f_prev.items(), key=lambda x: x[1])[0]
    # in case that g_prev is empty
    g_prev[''] = math.log(epsilon)
    g_last_choice = max(g_prev.items(), key=lambda x: x[1])[0]
    if f_prev[f_last_choice] > g_prev[g_last_choice]:
        return f_path[f_last_choice]
    else:
        return g_path[g_last_choice]
