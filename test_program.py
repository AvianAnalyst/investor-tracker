import unittest
from main import *


class TestDataRow(unittest.TestCase):
    def test_unpacks_and_type_casts_data_correctly(self):
        data = ('2018-5-5', '234', '234.23', 'john')
        data_row = DataRow(*data)
        assert type(data_row.date) == datetime.date
        assert type(data_row.investor) == str
        assert type(data_row.price) == float
        assert type(data_row.shares) == int


class TestInvestor(unittest.TestCase):
    def test_constructor_sets_name_but_no_transactions(self):
        investor = Investor("John")
        assert investor.name == "John"
        assert investor.data == []

    def test_succesfully_appends_new_data(self):
        investor = Investor("John")
        data = ('2018-5-5', '234', '234.23', 'john')
        investor.append(DataRow(*data))
        assert len(investor.data) == 1
        investor.append(DataRow(*data))
        assert len(investor.data) == 2