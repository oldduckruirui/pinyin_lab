import json
import os
from glob import glob
from tqdm import tqdm
from . import train2g
from . import stats
from .const import COR_DIR, RES_DIR
from .utils import metric


def freq_stat_line(freq_three_word, word_list, line):
    line = line.strip()
    if len(line) == 0:
        return
    last_words = "##"
    for word in line:
        if word not in word_list:
            last_words = "##"
            continue
        # count three-word frequency by pinyin tuple
        if last_words[0] != "#":
            word_tuple = last_words + word
            freq_three_word[word_tuple] = \
                freq_three_word.get(word_tuple, 0) + 1

        last_words = last_words[1] + word


def process_single_file(file_name, freq_three_word, word_list):
    new_freq_three_word = {}

    try:
        with open(file_name, "r", encoding="utf-8") as f:
            for line in tqdm(f.readlines(), desc="Processing file...", leave=False):
                freq_stat_line(new_freq_three_word, word_list, line)
    except UnicodeDecodeError:
        new_freq_three_word = {}
        with open(file_name, "r", encoding="gbk") as f:
            for line in tqdm(f.readlines(), desc="Processing file...", leave=False):
                freq_stat_line(new_freq_three_word, word_list, line)

    for word_tuple in new_freq_three_word:
        freq_three_word[word_tuple] = freq_three_word.get(
            word_tuple, 0) + new_freq_three_word[word_tuple]

    return freq_three_word


def process_files():
    _, word2pinyin = train2g.get_word_list()
    word_list = set(word2pinyin.keys())

    file_list = [filename for filename in glob(os.path.join(
        COR_DIR, "**/*"), recursive=True) if os.path.isfile(filename)]

    freq_three_word = {}

    with tqdm(total=len(file_list), desc="Generating 3-word table...", leave=True) as pbar:
        for file in file_list:
            pbar.set_description(
                f"Generating 3-word table, processing file: {file}")
            freq_three_word = process_single_file(
                file, freq_three_word, word_list)
            pbar.update(1)

    return freq_three_word


@metric
def load_json():
    with open(os.path.join(RES_DIR, "three_word.json"), "r", encoding="utf-8") as f:
        freq_three_word = json.load(f)

    return freq_three_word


@metric
def dump_json(freq_three_word):
    with open(os.path.join(RES_DIR, "three_word.json"), "w", encoding="utf-8") as f:
        json.dump(freq_three_word, f, ensure_ascii=False)


@metric
def train():
    if not train2g.IS_TRAINED:
        train2g.train()
    freq_two_word = stats.freq_two_word

    try:
        freq_three_word = load_json()
    except FileNotFoundError or json.decoder.JSONDecodeError:
        freq_three_word = process_files()
        dump_json(freq_three_word)

    stats.freq_three_word = freq_three_word
    stats.prob_three_word = \
        calculate_probability(freq_two_word, freq_three_word)


@metric
def calculate_probability(freq_two_word, three_word):
    _, word2py = train2g.get_word_list()
    prob_first_two_word = {}
    freq_two_word_by_py = {}

    for word_pair in freq_two_word:
        word1, word2 = word_pair
        for py1 in word2py[word1]:
            for py2 in word2py[word2]:
                freq_two_word_by_py[py1+" "+py2] = freq_two_word_by_py.get(
                    py1+" "+py2, 0) + freq_two_word[word_pair]

    for word_pair in freq_two_word:
        word1, word2 = word_pair
        for py1 in word2py[word1]:
            for py2 in word2py[word2]:
                prob_first_two_word[py1+" "+py2] = freq_two_word[word_pair] / \
                    freq_two_word_by_py[py1+" "+py2]

    prob_three_word = {}
    for word_tuple in three_word:
        prob_three_word[word_tuple] = three_word[word_tuple] / \
            freq_two_word.get(word_tuple[:2], 1)

    return prob_three_word


if __name__ == "__main__":
    train()
