import argparse
import sys
from src import predict2g, predict3g, train2g, train3g
from tqdm import tqdm
import judge


MODEL_2_GRAM = "2-gram"
MODEL_3_GRAM = "3-gram"


def main():
    parser = argparse.ArgumentParser()
    # default 2-gram model
    parser.add_argument("-2", action="store_true", help="Use 2-gram model")
    # optional 3-gram model
    parser.add_argument("-3", action="store_true", help="Use 3-gram model")
    parser.add_argument("-a", "--alpha", type=float, default=1e-6)

    args = parser.parse_args()
    selected_model = MODEL_2_GRAM
    if args.__dict__["2"] and args.__dict__["3"]:
        print("Please select only one model")
        return
    if args.__dict__["3"]:
        selected_model = MODEL_3_GRAM
        train3g.train()
    else:
        selected_model = MODEL_2_GRAM
        train2g.train()

    output_list = []
    for line in sys.stdin:
        pinyin_text = line.strip()
        if selected_model == MODEL_2_GRAM:
            result = predict2g.predict(pinyin_text, args.alpha)
            print(result)
            output_list.append(result)
        else:
            result = predict3g.predict(pinyin_text, args.alpha)
            print(result)
            output_list.append(result)

    judge.judge(output_list)


if __name__ == "__main__":
    main()
