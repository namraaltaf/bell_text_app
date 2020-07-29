import csv
from settings import PHONE_NUMBER_DATA_PATH


class PhoneNumbersCsvOperator:
    """This is the csv file read class which reads Phone Numbers data."""

    def __init__(self, phone_numbers_data):
        """ initialize the Phone Numbers data variable"""
        self.phone_numbers_data = phone_numbers_data

    @classmethod
    def create_phone_numbers_data_obj(cls):
        """ Create Phone Numbers data object containing list of dictionaries"""
        phone_numbers_data = cls.read_phone_numbers_csv_file_by_reader(PHONE_NUMBER_DATA_PATH)
        return cls(phone_numbers_data=phone_numbers_data)

    @classmethod
    def read_phone_numbers_csv_file_by_reader(cls, file_name):
        """
        Read Phone Numbers csv file line by line and return the data.
        Args:
            file_name: file contains different Phone Numbers which is used in sending messages.
        """
        with open(file_name) as csv_file:
            data_reader = csv.DictReader(csv_file)
            return [row for row in data_reader]

    def get_phone_number_data(self):
        """
        Get Phone Numbers list.
        :return: phone number's data.
        """
        return self.phone_numbers_data


phone_number_data = PhoneNumbersCsvOperator.create_phone_numbers_data_obj()
