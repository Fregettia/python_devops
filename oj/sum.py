import sys


def main():
    binary_numbers = sys.argv[1:]

    result = bin(sum(int(b, 2) for b in binary_numbers))[2:]

    print(result)


if __name__ == "__main__":
    main()
