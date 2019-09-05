import pathlib
import csv
import json
import datetime
import argparse

from typing import Optional


def parse_date(date_string: str) -> datetime.date:
     return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()


def parse_path(path: str) -> pathlib.Path:
    return pathlib.Path(path)


class CapTable:
    def __init__(self, data: csv.DictReader):
        self.investors = self.parse_input(data)


    def generate_report(self, report_date: Optional[datetime.date] = None) -> str:
        if not report_date:
            report_date = datetime.date.today()
        investor_totals = []
        for investor in self.investors.values():
            investor_totals.append(investor.get_totals(report_date))
        report_date = str(report_date).replace('-', '/')

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

        report = {
            "date": report_date,
            "cash_raised": amount_paid,
            "total_number_of_shares": num_of_shares,
            "ownership": owners,
        }

        return json.dumps(report)

    def parse_input(self, data: csv.DictReader) -> list:
        investors = {}
        for row in data:
            investors.setdefault(row["name"], Investor(row["name"])).append_data(DataRow(*row.values()))
        return investors


class DataRow:
    def __init__(self,  date: str,  shares: str,  price: str,  investor: str):
        self.date = parse_date(date)
        self.shares = int(shares)
        self.price = float(price)
        self.investor = investor


class Investor:
    def __init__(self, name: str):
        self.name = name
        self.data = []

    def append_data(self, data: DataRow) -> None:
        self.data.append(data)

    def get_totals(self, date: datetime.date) -> tuple:
        data = self.discard_extra_data(date)
        shares = sum([row.shares for row in data])
        paid = sum([row.price for row in data])
        return self.name, shares, paid

    def discard_extra_data(self, date: datetime.date) -> list:
        return [row for row in self.data if row.date <= date]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to the input file", type=parse_path)
    parser.add_argument("-d", "--date", metavar="YYYY-MM-DD", help="exclude data after this date", type=parse_date)
    args = parser.parse_args()

# TODO: figure out why with open as file didn't work here
    input_file = open(args.path, "r")
    data = csv.DictReader(input_file, fieldnames=["date", "shares", "cash", "name"])
    next(data)

    table = CapTable(data)

    json_output = table.generate_report(args.date)

    with open("output.txt", "w") as output_file:
        output_file.write(json_output)

    input_file.close()

if __name__ == "__main__":
    main()