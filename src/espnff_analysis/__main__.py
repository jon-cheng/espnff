from espnff_analysis import pipeline as pp
import argparse
from espnff_analysis import __version__


def parse_args():
    parser = argparse.ArgumentParser(
        description="ESPN Fantasy Football Analysis Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--year",  # year of interest for FF analysis
        "-y",
        type=str,
        help="Year of interest",
        required=True,
    )

    parser.add_argument(
        "--league-id",
        "l",
        type=str,
        help="League ID",
        required=True,
    )

    parser.add_argument(
        "swid",
        "s",
        type=str,
        help="SWID",
        required=True,
    )

    parser.add_argument(
        "s2",
        "t",
        type=str,
        help="s2",
        required=True,
    )

    parser.add_argument(
        "path",
        "p",
        type=str,
        help="output path",
        required=True,
    )

    parser.add_argument("--version", "-v", action="version", version=__version__)

    return parser


def main():
    parser = parse_args()
    args = parser.parse_args()
    pp.main_pipeline(args.league_id, args.year, args.s2, args.swid, args.path)
    return


if __name__ == "__main__":
    main()
