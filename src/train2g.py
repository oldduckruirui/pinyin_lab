import json
import os
import sys
from tqdm import tqdm
from glob import glob
from . import stat


from .const import COR_DIR, RES_DIR, SRC_DIR

is_trained = False


def freq_stat_line(freq_1_word, freq_2_word, word2pinyin, line):
    line = line.strip()
    if len(line) == 0:
        return
    last_word = "#"
    for i, word in enumerate(line):
        if word not in word2pinyin:
            last_word = "#"
            continue
        # count 1-word frequency by pinyin
        for pinyin in word2pinyin[word]:
            if pinyin not in freq_1_word:
                freq_1_word[pinyin] = {}
            freq_1_word[pinyin][word] = freq_1_word[pinyin].get(word, 0) + 1

        # count 2-word frequency by pinyin pair
        if last_word != "#":
            word_pair = last_word + word
            for pinyin1 in word2pinyin[last_word]:
                for pinyin2 in word2pinyin[word]:
                    pinyin_text = pinyin1 + " " + pinyin2
                    if pinyin_text not in freq_2_word:
                        freq_2_word[pinyin_text] = {}
                    freq_2_word[pinyin_text][word_pair] = freq_2_word[pinyin_text].get(
                        word_pair, 0) + 1

        last_word = word


def process_single_file(file_name, freq_one_word, freq_two_word, word2pinyin):
    new_freq_one_word = {}
    new_freq_two_word = {}

    try:
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f.readlines():
                freq_stat_line(new_freq_one_word,
                               new_freq_two_word, word2pinyin, line)
    except UnicodeDecodeError:
        new_freq_one_word = {}
        new_freq_two_word = {}
        with open(file_name, "r", encoding="gbk") as f:
            for line in f.readlines():
                freq_stat_line(new_freq_one_word,
                               new_freq_two_word, word2pinyin, line)

    for pinyin in new_freq_one_word:
        if pinyin not in freq_one_word:
            freq_one_word[pinyin] = {}
        for word in new_freq_one_word[pinyin]:
            freq_one_word[pinyin][word] = freq_one_word[pinyin].get(
                word, 0) + new_freq_one_word[pinyin][word]

    for pinyin_text in new_freq_two_word:
        if pinyin_text not in freq_two_word:
            freq_two_word[pinyin_text] = {}
        for word_pair, count in new_freq_two_word[pinyin_text].items():
            freq_two_word[pinyin_text][word_pair] = freq_two_word[pinyin_text].get(
                word_pair, 0) + count

    return freq_one_word, freq_two_word


def get_word_list():
    pinyin2word = {}
    word_list = []
    word2pinyin = {}

    with open(os.path.join(SRC_DIR, 'alphabet', '拼音汉字表.txt'), "r", encoding="gbk") as f:
        for line in f.readlines():
            data = line.split()
            pinyin2word[data[0]] = data[1:]

    with open(os.path.join(SRC_DIR, 'alphabet', '一二级汉字表.txt'), "r", encoding="gbk") as f:
        data = f.read()
        word_list = list(data)

    for pinyin, words in pinyin2word.items():
        for word in words:
            if word not in word2pinyin:
                word2pinyin[word] = [pinyin]
            else:
                word2pinyin[word].append(pinyin)

    # check if the word list is consistent with the pinyin list
    assert (all([word in word2pinyin for word in word_list]))
    assert (all([word in word_list for word in word2pinyin]))

    return pinyin2word, word2pinyin


def process_files():
    pinyin2word, word2pinyin = get_word_list()

    file_list = [filename for filename in glob(os.path.join(
        COR_DIR, "**/*"), recursive=True) if os.path.isfile(filename)]

    freq_one_word = {}
    for pinyin in pinyin2word:
        freq_one_word[pinyin] = {}
        for word in pinyin2word[pinyin]:
            freq_one_word[pinyin][word] = 1

    freq_two_word = {}

    with tqdm(total=len(file_list), desc="Generating 2-word table...", leave=False) as pbar:
        for idx, file in enumerate(file_list):
            pbar.set_description(
                f"Generating 2-word table, processing file: {file}")
            freq_one_word, freq_two_word = process_single_file(
                file, freq_one_word, freq_two_word, word2pinyin)
            pbar.update(1)

    return freq_one_word, freq_two_word


def dump_json(freq_one_word, freq_two_word):
    with open(os.path.join(RES_DIR, "one_word.json"), "w", encoding="utf-8") as f:
        json.dump(freq_one_word, f, ensure_ascii=False)

    with open(os.path.join(RES_DIR, "two_word.json"), "w", encoding="utf-8") as f:
        json.dump(freq_two_word, f, ensure_ascii=False)


def load_json():
    with open(os.path.join(RES_DIR, "one_word.json"), "r", encoding="utf-8") as f:
        freq_one_word = json.load(f)

    with open(os.path.join(RES_DIR, "two_word.json"), "r", encoding="utf-8") as f:
        freq_two_word = json.load(f)

    return freq_one_word, freq_two_word


def train():
    try:
        freq_one_word, freq_two_word = load_json()
    except FileNotFoundError or json.decoder.JSONDecodeError:
        freq_one_word, freq_two_word = process_files()
        dump_json(freq_one_word, freq_two_word)

    stat.freq_one_word, stat.freq_two_word = freq_one_word, freq_two_word
    stat.prob_one_word, stat.prob_two_word = calculate_probability(
        freq_one_word, freq_two_word)
    is_trained = True


def calculate_probability(one_word, two_word):
    prob_two_word = {}
    for pinyin_text in two_word:
        pinyin1 = pinyin_text.split()[0]
        prob_two_word[pinyin_text] = {}
        for word_pair, count in two_word[pinyin_text].items():
            prob_two_word[pinyin_text][word_pair] = count / \
                one_word[pinyin1][word_pair[0]]

    prob_one_word = {}
    for pinyin in one_word:
        total = sum(one_word[pinyin].values())
        prob_one_word[pinyin] = {}
        for word, count in one_word[pinyin].items():
            prob_one_word[pinyin][word] = count / total

    return prob_one_word, prob_two_word
