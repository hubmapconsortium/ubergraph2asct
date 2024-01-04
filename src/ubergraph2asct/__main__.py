import argparse
import pathlib

from .ubergraph2asct import transform


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input", type=pathlib.Path, required=True, help="list of terms"
    )
    parser.add_argument(
        "-p", "--property", type=pathlib.Path, required=True, help="list of properties"
    )
    parser.add_argument(
        "-o", "--output", type=pathlib.Path, required=True, help="path to CSV file"
    )

    args = parser.parse_args()

    transform(args.input, args.property, args.output)


if __name__ == "__main__":
    main()
