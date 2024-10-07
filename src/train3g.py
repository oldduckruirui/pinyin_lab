import json
import os
import sys
from glob import glob
from tqdm import tqdm
from . import train2g
from . import stat
from .const import COR_DIR, RES_DIR


def freq_stat_line(freq_three_word, hot2word, word2pinyin, line):
    line = line.strip()
    if len(line) == 0:
        return
    last_words = "##"
    for i, word in enumerate(line):
        if word not in word2pinyin:
            last_words = "##"
            continue

        # count three-word frequency by pinyin tuple
        if last_words in hot2word:
            word_tuple = last_words + word
            for py1 in word2pinyin[last_words[0]]:
                for py2 in word2pinyin[last_words[1]]:
                    for py3 in word2pinyin[word]:
                        py_text = py1 + " " + py2 + " " + py3
                        if py_text not in freq_three_word:
                            freq_three_word[py_text] = {}
                        freq_three_word[py_text][word_tuple] = freq_three_word[py_text].get(
                            word_tuple, 0) + 1

        last_words = last_words[1] + word


def process_single_file(file_name, freq_three_word, hot2word, word2pinyin):
    new_freq_three_word = {}

    try:
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f.readlines():
                freq_stat_line(new_freq_three_word,
                               hot2word, word2pinyin, line)
    except UnicodeDecodeError:
        new_freq_three_word = {}
        with open(file_name, "r", encoding="gbk") as f:
            for line in f.readlines():
                freq_stat_line(new_freq_three_word,
                               hot2word, word2pinyin, line)

    for py_text in new_freq_three_word:
        if py_text not in freq_three_word:
            freq_three_word[py_text] = {}
        for word_tuple, count in new_freq_three_word[py_text].items():
            freq_three_word[py_text][word_tuple] = freq_three_word[py_text].get(
                word_tuple, 0) + count

    return freq_three_word


def process_files(hot2word, word2pinyin):
    file_list = [filename for filename in glob(os.path.join(
        COR_DIR, "**/*"), recursive=True) if os.path.isfile(filename)]

    freq_three_word = {}

    with tqdm(total=len(file_list), desc="Generating 3-word table...", leave=False) as pbar:
        for idx, file in enumerate(file_list):
            pbar.set_description(
                f"Generating 3-word table, processing file: {file}")
            freq_three_word = process_single_file(
                file, freq_three_word, hot2word, word2pinyin)
            pbar.update(1)

    return freq_three_word


def get_hot2word(two_word):
    two_word_list = []
    for py_text in two_word:
        for word_pair, count in two_word[py_text].items():
            two_word_list.append((word_pair, count))
    two_word_list.sort(key=lambda x: x[1], reverse=True)

    hot2word = {}
    for i in range(min(100000, len(two_word_list))):
        hot2word[two_word_list[i][0]] = True

    return hot2word


def load_json():
    with open(os.path.join(RES_DIR, "three_word.json"), "r", encoding="utf-8") as f:
        freq_three_word = json.load(f)

    return freq_three_word


def dump_json(freq_three_word):
    with open(os.path.join(RES_DIR, "three_word.json"), "w", encoding="utf-8") as f:
        json.dump(freq_three_word, f, ensure_ascii=False)


def train():
    if not train2g.is_trained:
        train2g.train()
    freq_two_word = stat.freq_two_word

    hot2word = get_hot2word(freq_two_word)

    try:
        freq_three_word = load_json()
    except FileNotFoundError or json.decoder.JSONDecodeError:
        word2pinyin = train2g.get_word_list()[1]
        freq_three_word = process_files(hot2word, word2pinyin)
        dump_json(freq_three_word)

    stat.freq_three_word = freq_three_word
    stat.prob_first_two_word, stat.prob_three_word = calculate_probability(
        freq_two_word, freq_three_word, hot2word)
    stat.hot2word = hot2word


def calculate_probability(freq_two_word, three_word, hot2word):
    prob_first_two_word = {}
    for py_text in freq_two_word:
        total = sum(freq_two_word[py_text].values())
        if py_text not in prob_first_two_word:
            prob_first_two_word[py_text] = {}
        for word_pair, count in freq_two_word[py_text].items():
            prob_first_two_word[py_text][word_pair] = count / total

    for py_text in three_word:
        first_2_pinyin = " ".join(py_text.split()[:2])
        for word_tuple in three_word[py_text]:
            three_word[py_text][word_tuple] = three_word[py_text][word_tuple] / \
                freq_two_word[first_2_pinyin].get(word_tuple[:2], 1)

    return prob_first_two_word, three_word


if __name__ == "__main__":
    train()
