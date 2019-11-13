import time
import unittest
import spintax
import requests
import datetime
import logging
import multiprocessing

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from constants import (GOOGLE_KEY, REQUEST_API_URL, RESPONSE_API_URL,
                       PAGE_URL, API_KEY, TIME_OUT_LIMIT, INITIAL_WAIT_TIME,
                       SHORT_WAIT_TIME, ELEMENT_WAIT_TIME)

from csv_file_operator.phone_numbers_csv_operator import phone_number_data

from config import THREADS
from settings import driver_path


errors = []
success = []

class TestSendTextMessage(unittest.TestCase):
    """ This class contains test which will send message to provided Phone Number."""

    retrieve_captcha_attempt = 0
    captcha_response_token = ''
    success_file = ''
    error_file = ''
    data = {}

    def test_send_text_message(self):
        """ Check messages can be sent to provided phone numbers successfully."""
        try:
            phone_numbers_data = phone_number_data.get_phone_number_data()
            print(phone_numbers_data)

            numbers_list = [phone_numbers_data[x:x + 10] for x in range(0, len(phone_numbers_data), 10)]

            with multiprocessing.Pool(THREADS) as thread_pool:
                try:
                    TestSendTextMessage.data = thread_pool.map(TestSendTextMessage.enter_and_submit_phone_numbers_data,
                                                               numbers_list)
                    thread_pool.close()
                    thread_pool.join()
                except Exception as ex:
                    print(ex)
        except Exception as ex:
            print(ex)
        finally:
            success_list = []
            errors_list = []

            if TestSendTextMessage.data:
                for data_key in TestSendTextMessage.data:
                    if 'success' in data_key:
                        for success_key in data_key['success']:
                            success_list.append(success_key)
                    elif 'errors' in data_key:
                        for errors_key in data_key['errors']:
                            errors_list.append(errors_key)

            if success_list:
                success_file = "messages_success_status_{date}.txt".format(
                    date=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
                success_file_handler = open(success_file, 'w')
                success_file_handler.write('Messages are sent successfully to following Phone Numbers:\n')
                for success_key in success_list:
                    success_file_handler.write("{success}\n".format(success=success_key))
                success_file_handler.close()

            if errors_list:
                error_file = "messages_errors_status_{date}.txt".format(
                    date=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
                error_file_handler = open(error_file, "w")
                error_file_handler.write('Messages sending failed to following Phone Numbers:\n')
                for error_key in errors_list:
                    error_file_handler.write("{error}\n".format(error=error_key))
                error_file_handler.close()

    @classmethod
    def enter_and_submit_phone_numbers_data(cls, phone_numbers):
        """ Enter data in text fields appearing on form and submit data."""
        print("inside function")
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        cls.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
        cls.driver.get(PAGE_URL)

        for i in range(0, len(phone_numbers), 10):
            numbers = []
            for phone_number_key in phone_numbers[i:i+10]:
                numbers.append(phone_number_key['phone_number'])

            phone_number_string = ','.join(numbers)
            print("\n****************** Chunk of Phone numbers are: ********************\n", phone_number_string)

            WebDriverWait(cls.driver, ELEMENT_WAIT_TIME).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[type="submit"]'))
            )
            send_to_field = cls.driver.find_element_by_css_selector('#id_Send_to')
            send_to_field.clear()
            message_field = cls.driver.find_element_by_css_selector('#id_Message')
            message_field.clear()

            send_to_field.send_keys(phone_number_string)
            message_field.send_keys(spintax.spin("{Hello|Hi}, how are you?"))

            resp_id = cls.solve_captcha()
            captcha_response_token = cls.get_captcha_token(resp_id=resp_id)
            while captcha_response_token == '' and cls.retrieve_captcha_attempt < 5:
                captcha_response_token = cls.get_captcha_token(resp_id=resp_id)
                cls.retrieve_captcha_attempt = cls.retrieve_captcha_attempt + 1

            if captcha_response_token:
                cls.driver.execute_script("document.getElementById('g-recaptcha-response').style.removeProperty('display');")
                captcha_response_field = cls.driver.find_element_by_css_selector('#g-recaptcha-response')
                captcha_response_field.clear()
                captcha_response_field.send_keys(captcha_response_token)
            else:
                print("Did not get Captcha solved response from 2Captcha Server so leaving this chunks of Phone Numbers")

            submit_button = cls.driver.find_element_by_css_selector('[type="submit"]')
            submit_button.click()
            time.sleep(2)

            try:
                cls.captcha_response_token = ''
                cls.retrieve_captcha_attempt = 0

                WebDriverWait(cls.driver, ELEMENT_WAIT_TIME).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.messages .success'))
                )

                message_sent_status = cls.driver.find_element_by_css_selector('.messages .success').text

                if "message(s) successfully sent" in message_sent_status:
                    for phone_number_key in numbers:
                        success.append(phone_number_key)
                    print("Message sent successfully to these phone numbers: ", phone_number_string)

            except:
                incorrect_numbers = []
                error_contains_phone_number = False

                WebDriverWait(cls.driver, ELEMENT_WAIT_TIME).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.messages li'))
                )
                message_failure_status = cls.driver.find_elements_by_css_selector('.messages li')

                for error_key in message_failure_status:
                    error_contains_phone_number = any(char.isdigit() for char in error_key.text)

                    if error_contains_phone_number:
                        error_text = error_key.text.split()
                        incorrect_numbers.append(error_text[0])
                        errors.append(error_text[0])

                if not error_contains_phone_number:
                    for num_key in numbers:
                        errors.append(num_key)

                if error_contains_phone_number and len(incorrect_numbers) != len(numbers):
                    for num_key in numbers:
                        if num_key not in incorrect_numbers:
                            success.append(num_key)

                if error_contains_phone_number:
                    print("messages sending failed to these phone numbers: ", ",".join(incorrect_numbers))
                else:
                    print("messages sending failed to these phone numbers: ", ",".join(numbers))

            cls.driver.quit()

            if success:
                return {"success": success}
            elif errors:
                return {"errors": errors}

    @classmethod
    def solve_captcha(cls):
        """ Provide captcha related data to Captcha solver API server and get token."""
        print("Sending request to 2Captcha server to solve Captcha!!!")
        resp = requests.post(url="{url}?key={key}&method=userrecaptcha&googlekey={google_key}&pageurl={p_url}&"
                                 "json=1".format(url=REQUEST_API_URL, key=API_KEY, google_key=GOOGLE_KEY,
                                                 p_url=PAGE_URL))
        response_json = resp.json()
        return response_json["request"]

    @classmethod
    def get_captcha_token(cls, resp_id):
        end_time = time.time() + TIME_OUT_LIMIT
        if cls.retrieve_captcha_attempt == 0:
            time.sleep(INITIAL_WAIT_TIME)
        else:
            time.sleep(SHORT_WAIT_TIME)
        while time.time() < end_time:
            try:
                resp = requests.get(url="{url}?key={key}&action=get&id={id}&json=1".format(
                    url=RESPONSE_API_URL, key=API_KEY, id=resp_id))
                response = resp.json()
                print("Getting response from 2Captcha Server.")
                if response["status"] == 0 and response["request"] == "CAPCHA_NOT_READY":
                    print("Captcha is not resolved yet. So waiting for it...")
                elif response['status'] == 1:
                    cls.captcha_response_token = response['request']
                    print("Captcha is resolved now!")
                    break
            except TimeoutError as e:
                print(e)

        return cls.captcha_response_token
