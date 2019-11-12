import os

# Get Base directory path.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


driver_path = os.path.join(BASE_DIR, 'chromedriver')

# CSV file path
PHONE_NUMBER_DATA_PATH = os.path.join(BASE_DIR,'csv_file/phone_numbers.csv')
