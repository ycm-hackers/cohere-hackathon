import argparse


def create_arg_parser():
    r"""Get arguments from command lines."""
    parser = argparse.ArgumentParser(description="Commandline Parser")
    parser.add_argument(
        "--schema",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="Creates the new schema.",
    )
    parser.add_argument(
        "--store",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="Storing new embeddings.",
    )
    parser.add_argument(
        "--delete",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="Delete all data objects.",
    )

    return parser
