import os
import re
import sys


def format_numbers(numbers, size):
    formatted_numbers = []

    for i in range(0, len(numbers), size):
        group = numbers[i : i + size]
        formatted_group = ''.join(group)
        formatted_numbers.append(formatted_group)

    return '-'.join(formatted_numbers)


def extract_numbers(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        result = []
        for line in infile:
            numbers = re.findall(r'\d', line)  # Find individual digits
            formatted_numbers = format_numbers(numbers, 3)
            result.append(formatted_numbers)
        outfile.write('\n'.join(result))


def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    extract_numbers(input_file, output_file)


if __name__ == "__main__":
    main()
