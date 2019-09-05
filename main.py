import pathlib
import csv
import json
import datetime
import argparse
from typing import Optional, Dict, Tuple, List


def parse_date(date_string: str) -> datetime.date:
    return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()


def parse_path(path: str) -> pathlib.Path:
    return pathlib.Path(path)


class DataRow:
    """Stores the individual transaction information as well as typecasts it to the proper type"""
    def __init__(self,  date: str,  shares: str,  price: str,  investor: str):
        self.date = parse_date(date)
        self.shares = int(shares)
        self.price = float(price)
        self.investor = investor


class Investor:
    """Stores a single investor and a list of their transactions"""
    def __init__(self, name: str):
        self.name = name
        self.data = []

    def append(self, data: DataRow) -> None:
        """Adds a new DataRow to the existing history"""
        self.data.append(data)

    def get_totals(self, date: datetime.date) -> Tuple[str, int, float]:
        """Gathers individual totals for the investor disregarding extraneous
        data"""
        data = self.discard_extra_data(date)
        shares = sum([row.shares for row in data])
        paid = sum([row.price for row in data])
        return self.name, shares, paid

    def discard_extra_data(self, date: datetime.date) -> List[DataRow]:
        """Discards any transactions taking place after the provided date"""
        return [row for row in self.data if row.date <= date]


class CapTable:
    """Stores a list of ``Investor``s and supplies functionality to generate reports"""

    def __init__(self, data: csv.DictReader):
        self.investors = self.parse_input(data)

    def generate_report(self, report_date: Optional[datetime.date] = None) -> str:
        """Returns a report in json format specifying:
            * date requested
            * total amount raised
            * total shares
           And for each investor it lists:
            * investor's name
            * amount spent
            * total owned shares
            * percentage of company owned

           If the optional ``report_date`` is supplied, it will only count transactions
           up to cand including this date. It will default to today's date.
        """
        if not report_date:
            report_date = datetime.date.today()

        investor_totals = []
        for investor in self.investors.values():
            investor_totals.append(investor.get_totals(report_date))

        # Pair each type of data together across investors
        paired_data = list(zip(*investor_totals))
        amount_paid = sum(paired_data[2])
        num_of_shares = sum(paired_data[1])
        owners = [
            {
                "investor": investor[0],
                "shares": investor[1],
                "cash_paid": investor[2],
                "ownsership": (investor[1] / num_of_shares) * 100
            } for investor in investor_totals
        ]

        report_date = str(report_date).replace('-', '/')  # Correct date for display
        report = {
            "date": report_date,
            "cash_raised": amount_paid,
            "total_number_of_shares": num_of_shares,
            "ownership": owners,
        }
        return json.dumps(report)

    def parse_input(self, data: csv.DictReader) -> Dict[str, Investor]:
        """Returns a dict of investors each storing their history of transactions as separate
        DataRows with their name as the key"""
        investors = {}
        for row in data:
            investors.setdefault(row["name"], Investor(row["name"])).append(DataRow(*row.values()))
        return investors


def main():
    """Drives the main program"""
    # Sets up argparse to grab a required path and optional date from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to the input file", type=parse_path)
    parser.add_argument("-d", "--date",
                        metavar="YYYY-MM-DD",
                        help="exclude data after this date",
                        type=parse_date)
    args = parser.parse_args()

    # Can't use with open() as here due to csv.DictReader
    input_file = open(args.path, "r")
    data = csv.DictReader(input_file, fieldnames=["date", "shares", "cash", "name"])
    next(data) # Skips the labeling row from input

    table = CapTable(data)

    json_output = table.generate_report(args.date)
    input_file.close()

    with open("output.txt", "w") as output_file:
        output_file.write(json_output)


if __name__ == "__main__":
    main()
