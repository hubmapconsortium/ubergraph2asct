import argparse
import pathlib

from .ubergraph2asct import transform

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        required=True,
        help="NT file with axioms"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        required=True,
        help="path to CSV file"
    )

    args = parser.parse_args()

    transform(args.input, args.output)


if __name__ == "__main__":
    main()
