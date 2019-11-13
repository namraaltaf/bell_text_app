# Bell Text App

Bell Text App - Bell text APP Automation script is implemented with the Python and Selenium.

## Getting Started (First time only)

Before you start working, you first need to setup your environment. Make sure you have the following installed:

1: Chrome Browser

2: Python3 (To install Python3, follow these steps.)

- Go to ``` https://www.python.org/downloads/```.
- Scroll down the page. and find ```Looking for a specific release?``` section.
- Find ```python 3.6.4``` version in the list and download it.
- Once downloaded, go to ```Downloads``` folder and install this downloaded file by clicking on it.
- While running setup, make sure to select ```Add Python3.6 to PATH``` check box appearing at first page.
- Click on ```Install now``` option.
- Complete setup.

Note: If Python3 is already installed on your system, skip this ```2``` step.

3: chromedriver (To install chromedriver, follow ```7``` step mentioned below.)



Now follow these steps:

1: Open cmd/terminal in your computer.

2: Use ```cd Documents``` to go to Documents (or any other directory where you want to clone this project).

3: Clone project in your computer
- Run ```git clone https://github.com/namrahaltaf/bell_text_app.git``` command.

4: Select project
- Run ```cd bell_text_app``` command.

5: Create Virtual environment.
- Run ```pip install virtualenv``` to install virtual environments.
- To create virtual environment with python 3, run ```virtualenv -p python belltextenv```
- To start virtual environment, run ```belltextenv\Scripts\activate```

6: Install Requirements.
- Run ```pip3 install -r reqs/requirements.txt``` command.
(If it gives error, run ```pip install -r reqs/requirements.txt``` command)

7: Skip this step if you have Chrome Browser version 78.0.3904.70.
(If Chrome Browser version is different than the 78.0.3904.70 version, you need to download chromedriver version
compatible to your Chrome Browser.)

Note: This project folder already has chromedriver version compatible to Chrome Browser version 78.0.3904.70

To install chrome driver follow these steps:

- go to ```https://sites.google.com/a/chromium.org/chromedriver/downloads``` and download chromedriver according to
your browser version.
- Copy the ```chromedriver``` file from Downloads folder.
- Go to `Documents` folder (or other directory where you have copied this script).
- Open ```bell_text_app``` folder.
- Place your copied chromedriver here and replace the previous one.

8: In case if you have skipped step ```7``` then:
- Go to `Documents` folder (or other directory where you have copied this project).

9 - If you are already in ```Documents``` folder then:
- Open ```csv_file``` folder.
- Replace ```phone_numbers.csv``` file with new ```phone_numbers.csv``` file.
(Current file contains dummy data for Phone Numbers)

10: If you have large number of data then
- Open ```config.py``` file in notepad appearing under this ```bell_text_app``` folder.
- Replace 5 with 10.
- Save the file.

11: Run Script
- Run ```nosetests test_send_text_message.py``` command. (# This will run the script)


## Running test

To run test in future, first access project folder by following these steps:
- Open project folder under Documents/other directory where it exists.
- Open ```csv_file``` folder.
- Replace ```phone_numbers.csv``` file with new ```phone_numbers.csv``` file. (# when you need to add new Phone Numbers)
- Now open terminal/cmd
- Execute ```cd Documents``` command.
(# Note: if project is under another directory, add name of that directory instead of Documents.)
- Execute ```cd bell_text_app``` command.
- Execute ```belltextenv\Scripts\activate``` command
- Execute ```nosetests test_send_text_message.py``` command. (# This will run the script)

## Check Results

Once script run, to check results:
- Open project folder under Documents/other directory where it exists.
- Open ```messages_success_status...``` file in notepad to see for which phone numbers, message have been sent successfully.
- Open ```messages_errors_status...``` file in notepad to see for which phone numbers, message have not been sent.

## Guidelines

Make sure to follow this:
- CSV file should contain only one column i.e. ```phone_number```.
- CSV file name should always be ```phone_numbers``` and it should have ```.csv``` extension.
And file should always be placed under ```csv_file``` folder which is available inside this Project.
- All Phone Numbers should be under same one column.
