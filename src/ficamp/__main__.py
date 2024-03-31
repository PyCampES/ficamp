from collections import defaultdict
import argparse

import questionary
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select

from ficamp.classifier.infer import infer_tx_category
from ficamp.classifier.keywords import sort_by_keyword_matches
from ficamp.classifier.preprocessing import preprocess
from ficamp.datastructures import Tx
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
    import_parser.add_argument("--filename", help="File to load")
    import_parser.set_defaults(func=import_data)

    # Subparser for the categorize command
    categorize_parser = subparsers.add_parser(
        "categorize", help="Categorize transactions"
    )
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


def make_map_cat_to_kws(session):
    statement = select(Tx).where(Tx.category.is_not(None))
    known_cat_tx = session.exec(statement).all()
    keywords = defaultdict(list)
    for tx in known_cat_tx:
        keywords[tx.category].extend(tx.concept_clean.split())
    return keywords


def query_business_category(tx, session):
    # Clean up the transaction concept string
    tx.concept_clean = preprocess(tx.concept)

    # If there is an exact match to the known transactions, return that one
    statement = select(Tx.category).where(Tx.concept_clean == tx.concept_clean)
    category = session.exec(statement).first()
    if category:
        return category

    # Build map of category --> keywords
    cats = make_map_cat_to_kws(session)
    cats_sorted_by_matches = sort_by_keyword_matches(cats, tx.concept_clean)
    # Show categories to user sorted by keyword criterion
    categories_choices = [cat for _, cat in cats_sorted_by_matches]
    categories_choices.extend([DefaultAnswers.NEW, DefaultAnswers.SKIP])
    default_choice = categories_choices[0]

    print(f"{tx.date.isoformat()} | {tx.amount} | {tx.concept_clean}")
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


def categorize(engine):
    """Classify transactions into categories"""
    try:
        with Session(engine) as session:
            statement = select(Tx).where(Tx.category.is_(None))
            results = session.exec(statement).all()
            print(f"Got {len(results)} Tx to categorize")
            for tx in results:
                print(f"Processing {tx}")
                tx_category = query_business_category(tx, session)
                if tx_category:
                    print(f"Saving category for {tx.concept}: {tx_category}")
                    tx.category = tx_category
                    # update DB
                    session.add(tx)
                    session.commit()
                else:
                    print("Not saving any category for thi Tx")
    except KeyboardInterrupt:
        print("Session interrupted. Closing.")


def main():
    engine = create_engine("sqlite:///ficamp.db")  # create DB
    SQLModel.metadata.create_all(engine)  # create tables
    try:
        args = cli()
        if args.command:
            args.func(engine)
    except KeyboardInterrupt:
        print("\nClosing")


if __name__ == "__main__":
    load_dotenv()
    main()
