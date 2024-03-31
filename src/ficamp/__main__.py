import argparse
import json
import os
import shutil

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
import questionary


from ficamp.datastructures import Tx
from ficamp.parsers.abn import AbnParser
from ficamp.classifier.google_apis import query_gmaps_category


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
        "--bank", choices=["abn"], default="abn", help="Specify the bank for the import"
    )
    import_parser.add_argument("filename", help="File to load")
    import_parser.set_defaults(func=import_data)

    # Subparser for the categorize command
    categorize_parser = subparsers.add_parser(
        "categorize", help="Categorize transactions"
    )
    categorize_parser.add_argument("--query-google", action="store_true")
    categorize_parser.set_defaults(func=categorize)

    args = parser.parse_args()

    return args


def import_data(args, engine):
    """Run the parsers."""
    print(f"Importing data from {args.filename} for bank {args.bank}.")
    # TODO: Build enum for banks
    if args.bank == "abn":
        parser = AbnParser()
        parser.load(args.filename)
        transactions = parser.parse()
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


def get_category_dict(categories_database_path="categories_database.json"):
    # FIXME: move categories to SQLITE instead of json file.
    if not os.path.exists(categories_database_path):
        return {}
    with open(categories_database_path, "r") as file:
        category_dict = json.load(file)
    string_to_category = {
        string: category
        for category, strings in category_dict.items()
        for string in strings
    }
    return string_to_category


def revert_and_save_dict(string_to_category, filename="categories_database.json"):
    # Reverting the dictionary
    category_to_strings = {}
    for string, category in string_to_category.items():
        category_to_strings.setdefault(category, []).append(string)

    # Saving to a JSON file
    if os.path.exists(filename):
        shutil.move(filename, "/tmp/categories_db_bkp.json")
    with open(filename, "w") as file:
        json.dump(category_to_strings, file, indent=4)


def query_business_category(tx, categories_dict, query_google=False):
    # first try to get from the category_dict
    category = categories_dict.get(tx.concept)
    if category:
        return category
    # ask the user if we don't know it
    default_choice = None
    if query_google:
        categories_choices = list(set(categories_dict.values()))
        categories_choices.append("Type a new category")
        gmap_category = query_gmaps_category(tx.concept)
        if gmap_category != "Unknown":
            print(f"Google Maps category is {gmap_category}")
            categories_choices.append(gmap_category)
            default_choice = gmap_category
    print(f"{tx.date.isoformat()} {tx.amount} {tx.concept}")
    answer = questionary.select(
        "Please select the category for this TX",
        choices=categories_choices,
        default=default_choice,
        show_selected=True,
    ).ask()
    if answer == "Type a new category":
        print()
        answer = questionary.text("What's the category for the TX above").ask()
        save = questionary.confirm(
            f"Do you want to save the category as: {answer}?"
        ).ask()
    else:
        save = True
    if save:
        categories_dict[tx.concept] = answer
        category = answer
        revert_and_save_dict(categories_dict)
    return category


def categorize(args, engine):
    """Function to categorize transactions."""
    categories_dict = get_category_dict()
    with Session(engine) as session:
        statement = select(Tx).where(Tx.category.is_(None))
        results = session.exec(statement).all()
        for tx in results:
            print(f"Processing {tx}")
            tx_category = query_business_category(
                tx, categories_dict, query_google=args.query_google
            )
            if tx_category:
                print(f"Saving category for {tx.concept}: {tx_category}")
                tx.category = tx_category
                # update DB
                session.add(tx)
                session.commit()
    revert_and_save_dict(categories_dict)


def main():
    # create DB
    engine = create_engine("sqlite:///ficamp.db")
    # create tables
    SQLModel.metadata.create_all(engine)

    args = cli()
    if args.command:
        args.func(args, engine)


if __name__ == "__main__":
    load_dotenv()
    main()
