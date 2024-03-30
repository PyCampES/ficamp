import argparse

from dotenv import load_dotenv

from ficamp.parsers.abn import AbnParser
from ficamp.parsers.bsabadell import AccountBSabadellParser
from ficamp.parsers.bsabadell import CreditCardBSabadellParser
from ficamp.parsers.bbva import AccountBBVAParser
from ficamp.parsers.bbva import CreditCardBBVAParser


def cli() -> argparse.Namespace:
    """Parses the first argument from the command line and prints it."""

    # Create an argument parser
    parser = argparse.ArgumentParser(
        prog="ficamp", description="Print the first argument from the CLI"
    )

    parser.add_argument("--bank", choices=[
        "abn", "bbva-account", "bbva-credit-card", "bsabadell-account", "bsabadell-credit-card"
    ], default="abn")
    parser.add_argument("filename", help="The spreadsheet to load")

    # Parse the arguments
    args = parser.parse_args()

    # Print the first argument
    return args


def main():
    args = cli()
    args.filename
    args.bank

    # TODO: Build enum for banks
    if args.bank == "abn":
        parser = AbnParser()
        parser.load(args.filename)
        transactions = parser.parse()
        print(transactions)
        # TODO: Add categorizer!

    if args.bank == "bsabadell-account":
        parser = AccountBSabadellParser()
        parser.load(args.filename)
        transactions = parser.parse()
        print(transactions)

    if args.bank == "bsabadell-credit-card":
        parser = CreditCardBSabadellParser()
        parser.load(args.filename)
        transactions = parser.parse()
        print(transactions)

    if args.bank == "bbva-account":
        parser = AccountBBVAParser()
        parser.load(args.filename)
        transactions = parser.parse()
        print(transactions)

    if args.bank == "bbva-credit-card":
        parser = CreditCardBBVAParser()
        parser.load(args.filename)
        transactions = parser.parse()
        print(transactions)


load_dotenv()
main()
