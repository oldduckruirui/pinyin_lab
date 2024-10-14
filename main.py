import argparse
import sys
from src.utils import metric
from src import predict2g, predict3g, train2g, train3g, judge
import logging


MODEL_2_GRAM = "2-gram"
MODEL_3_GRAM = "3-gram"


@metric
def process_input(args):
    output_list = []
    for line in sys.stdin:
        pinyin_text = line.strip()
        if args.selected_model == MODEL_2_GRAM:
            result = predict2g.predict(pinyin_text, args.alpha)
            print(result)
            output_list.append(result)
        else:
            result = predict3g.predict(pinyin_text, args.alpha, args.beta)
            print(result)
            output_list.append(result)

    judge.judge(output_list)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)s] %(message)s')

    parser = argparse.ArgumentParser()
    # default 2-gram model
    parser.add_argument("-2", action="store_true", help="Use 2-gram model")
    # optional 3-gram model
    parser.add_argument("-3", action="store_true", help="Use 3-gram model")
    parser.add_argument("-a", "--alpha", type=float)
    parser.add_argument("-b", "--beta", type=float)

    args = parser.parse_args()
    args.selected_model = MODEL_2_GRAM
    if args.__dict__["2"] and args.__dict__["3"]:
        print("Please select only one model")
        return
    if args.__dict__["3"]:
        args.selected_model = MODEL_3_GRAM
        if args.alpha is None:
            args.alpha = 1e-4
        if args.beta is None:
            args.beta = 1e-1
        train3g.train()
    else:
        args.selected_model = MODEL_2_GRAM
        if args.alpha is None:
            args.alpha = 1e-7
        train2g.train()

    process_input(args)


if __name__ == "__main__":
    main()
