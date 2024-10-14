import os
import logging
from .const import DAT_DIR


def check(std_file, output_list):
    with open(std_file, "r", encoding="utf-8") as f:
        total_word = 0
        correct_word = 0
        total_sentence = 0
        correct_sentence = 0
        for line in output_list:
            line = line.strip()
            if not line:
                continue
            std_line = f.readline().strip()
            total_word += len(line)
            for i in range(0, len(line)):
                correct_word += (line[i] == std_line[i])
            correct_sentence += (line == std_line)
            total_sentence += 1
    return correct_word / total_word, correct_sentence / total_sentence


def judge(output_list):
    std_file = os.path.join(DAT_DIR, "answer.txt")

    try:
        word_accuracy_rate, sentence_accuracy_rate = check(
            std_file, output_list)
        logging.info("-  word accuracy: {:.2f}%".format(
            word_accuracy_rate * 100))
        logging.info("-  sentence accuracy: {:.2f}%".format(
            sentence_accuracy_rate * 100))
        word_accuracy_rate_str = "{:.2f}".format(word_accuracy_rate * 100)
        sentence_accuracy_rate_str = "{:.2f}".format(
            sentence_accuracy_rate * 100)
        return word_accuracy_rate_str, sentence_accuracy_rate_str
    except Exception as e:
        logging.error("can't calculate accuracy: {}".format(e))
        return "0.00", "0.00"


if __name__ == "__main__":
    output_file = os.path.join(DAT_DIR, "output.txt")
    with open(output_file, "r", encoding="utf-8") as f:
        output_list = f.readlines()
        judge(output_list)
