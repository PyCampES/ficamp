import argparse
import json
import os
import shutil
from enum import StrEnum

import questionary
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select

from ficamp.classifier.infer import infer_tx_category
from ficamp.classifier.preprocessing import preprocess
from ficamp.datastructures import Tx
from ficamp.parsers.abn import AbnParser
from ficamp.parsers.bbva import AccountBBVAParser, CreditCardBBVAParser
from ficamp.parsers.bsabadell import AccountBSabadellParser, CreditCardBSabadellParser
from ficamp.parsers.caixabank import CaixaBankParser
from ficamp.parsers.enums import BankParser


def cli() -> argparse.Namespace:
    """Creates a command line interface with subcommands for import and categorize."""

    # Create the main parser
    parser = argparse.ArgumentParser(
        prog="ficamp", description="Parse and categorize your expenses."
    )

    # Create subparsers for the two subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for the import command
    import_parser = subparsers.add_parser("import", help="Import a Transactions")
    import_parser.add_argument(
        "--bank",
        choices=[e.value for e in BankParser],
        default="abn",
        help="Specify the bank for the import",
    )
    import_parser.add_argument("filename", help="File to load")
    import_parser.set_defaults(func=import_data)

    # Subparser for the categorize command
    categorize_parser = subparsers.add_parser(
        "categorize", help="Categorize transactions"
    )
    categorize_parser.add_argument("--infer-category", action="store_true")
    categorize_parser.set_defaults(func=categorize)

    args = parser.parse_args()

    return args


def import_data(args, engine):
    """Run the parsers."""
    print(f"Importing data from {args.filename} for bank {args.bank}.")
    parser = BankParser(args.bank).get_parser()
    parser.load(args.filename)
    save_transactions_to_db(parser.parse(), engine)


def save_transactions_to_db(transactions, engine):
    for tx in transactions:
        with Session(engine) as session:
            # Assuming 'date' and 'amount' can uniquely identify a transaction
            statement = select(Tx).where(
                Tx.date == tx.date, Tx.amount == tx.amount, Tx.concept == tx.concept
            )
            result = session.exec(statement).first()
            if result is None:  # No existing transaction found
                session.add(tx)
                session.commit()
            else:
                print(f"Transaction already exists in the database. {tx}")


class DefaultAnswers:
    SKIP = "Skip this Tx"
    NEW = "Type a new category"


def query_business_category(tx, session, infer_category=False):
    # first try to get from the category_dict
    tx.concept_clean = preprocess(tx.concept)
    statement = select(Tx.category).where(Tx.concept_clean == tx.concept_clean)
    category = session.exec(statement).first()
    if category:
        return category
    # ask the user if we don't know it
    # query each time to update
    statement = select(Tx.category).where(Tx.category.is_not(None)).distinct()
    categories_choices = session.exec(statement).all()
    categories_choices.extend([DefaultAnswers.NEW, DefaultAnswers.SKIP])
    default_choice = DefaultAnswers.SKIP
    if infer_category:
        inferred_category = infer_tx_category(tx)
        if inferred_category:
            categories_choices.append(inferred_category)
            default_choice = inferred_category
    print(f"{tx.date.isoformat()} {tx.amount} {tx.concept_clean}")
    answer = questionary.select(
        "Please select the category for this TX",
        choices=categories_choices,
        default=default_choice,
        show_selected=True,
    ).ask()
    if answer == DefaultAnswers.NEW:
        answer = questionary.text("What's the category for the TX above").ask()
    if answer == DefaultAnswers.SKIP:
        return None
    if answer is None:
        # https://questionary.readthedocs.io/en/stable/pages/advanced.html#keyboard-interrupts
        raise KeyboardInterrupt
    return answer


def categorize(args, engine):
    """Function to categorize transactions."""
    try:
        with Session(engine) as session:
            statement = select(Tx).where(Tx.category.is_(None))
            results = session.exec(statement).all()
            print(f"Got {len(results)} Tx to categorize")
            for tx in results:
                print(f"Processing {tx}")
                tx_category = query_business_category(
                    tx, session, infer_category=args.infer_category)
                if tx_category:
                    print(f"Saving category for {tx.concept}: {tx_category}")
                    tx.category = tx_category
                    # update DB
                    session.add(tx)
                    session.commit()
                else:
                    print("Not saving any category for thi Tx")
    except KeyboardInterrupt:
        print("Closing")


def main():
    # create DB
    engine = create_engine("sqlite:///ficamp.db")
    # create tables
    SQLModel.metadata.create_all(engine)

    try:
        args = cli()
        if args.command:
            args.func(args, engine)
    except KeyboardInterrupt:
        print("\nClosing")


if __name__ == "__main__":
    load_dotenv()
    main()
