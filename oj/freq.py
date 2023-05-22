import re
from collections import Counter
import sys
import json


def word_frequency(input_file):
    word_counter = Counter()

    with open(input_file, 'r') as infile:
        for line in infile:
            words = re.findall(r'\b\w+\b', line.lower())
            word_counter.update(words)

    return dict(word_counter)


def main():
    input_file = sys.argv[1]
    word_freq = word_frequency(input_file)
    print(json.dumps(word_freq))


if __name__ == "__main__":
    main()
