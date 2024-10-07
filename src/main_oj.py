import os
import sys
import json
import math


def read_table():
    one_word = {}
    with open("1_word.txt", "r", encoding="utf-8") as f:
        data = json.load(f)
        for pinyin, stat in data.items():
            if pinyin not in one_word:
                one_word[pinyin] = {}
            for word, count in zip(stat["words"], stat["counts"]):
                one_word[pinyin][word] = count

    two_word = {}
    with open("2_word.txt", "r", encoding="utf-8") as f:
        data = json.load(f)
        for pinyin_text, stat in data.items():
            pinyin1, pinyin2 = pinyin_text.split()
            two_word[pinyin_text] = {}
            for word_pair, count in zip(stat["words"], stat["counts"]):
                word1, word2 = word_pair.split()
                two_word[pinyin_text][word1+word2] = count / \
                    one_word[pinyin1][word1]

    for pinyin in one_word:
        total = sum(one_word[pinyin].values())
        for word in one_word[pinyin]:
            one_word[pinyin][word] = one_word[pinyin][word] / total

    return one_word, two_word


def predict(pinyin_text, one_word, two_word, alpha=1e-10, epsilon=1e-233):
    pinyin_list = pinyin_text.split()

    def calc_one_word_prob(pinyin, word):
        return one_word[pinyin].get(word, 0)

    def calc_two_word_prob(pinyin_text, word_pair):
        if pinyin_text not in two_word:
            return 0
        return two_word[pinyin_text].get(word_pair, 0)

    for idx, pinyin in enumerate(pinyin_list):
        if idx == 0:
            path = {word: word for word in one_word[pinyin_list[0]]}
            f_prev = {word: math.log(epsilon + one_word[pinyin_list[0]].get(word, 0))
                      for word in one_word[pinyin_list[0]]}
        else:
            f_cur = {}
            new_path = {}
            pinyin_text = pinyin_list[idx-1] + " " + pinyin
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


def main():
    one_word, two_word = read_table()

    for line in sys.stdin:
        pinyin_text = line.strip()
        print(predict(pinyin_text, one_word, two_word))


if __name__ == '__main__':
    main()
