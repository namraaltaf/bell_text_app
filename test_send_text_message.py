import time
import unittest
import spintax
import requests
import datetime
import numpy
import multiprocessing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from constants import (GOOGLE_KEY, REQUEST_API_URL, RESPONSE_API_URL,
                       PAGE_URL, API_KEY, TIME_OUT_LIMIT, INITIAL_WAIT_TIME,
                       SHORT_WAIT_TIME)

from csv_file_operator.phone_numbers_csv_operator import phone_number_data

from settings import driver_path


class TestSendTextMessage(unittest.TestCase):
    """ This class contains test which will send message to provided Phone Number."""
    errors = []
    success = []
    retrieve_captcha_attempt = 0
    captcha_response_token = ''

    # def launch_site(self):
    #     self.driver = webdriver.Chrome()
    #     self.driver.get(PAGE_URL)
    #     self.wait_for_element_visibility(css_selector='[type="submit"]')

    def test_send_text_message(self):
        """ Check messages can be sent to provided phone numbers successfully."""
        try:
            #for i in range(0, len(phone_numbers_data), 10):
            #list = []
            phone_numbers_data = phone_number_data.get_phone_number_data()
            #print(phone_numbers_data)
            # for phone_number_key in phone_numbers_data:
            #     list.append(phone_number_key['phone_number'])
            # print(list)

            numbers_list = [phone_numbers_data[x:x + 10] for x in range(0, len(phone_numbers_data), 10)]
            # list_of_parts = numpy.array_split(phone_numbers_data, 5)
            # print(list_of_parts)
            # print(list_of_parts[0])
            #print(a)
            #print(type(numbers_list))
            a = []
            #thread_pool = multiprocessing.Pool(processes=3)
            thread_pool = multiprocessing.Pool(processes=3)
            print("success")
            for i in range(0, len(numbers_list)):
                for key in numbers_list:
                    print(key)
                    a.append(int(key['phone_number']))

                thread_pool.map(self.enter_and_submit_phone_numbers_data, a)
            #self.enter_and_submit_phone_numbers_data(phone_numbers=phone_numbers_data)
        except Exception as ex:
            print(ex)
        finally:
            if self.success:
                success_file = "messages_success_status_{date}.txt".format(
                    date=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
                file = open(success_file,'w')
                file.write('Messages are sent successfully to following Phone Numbers:\n')
                for success_key in self.success:
                    file.write("{success}\n".format(success=success_key))
                file.close()

            if self.errors:
                error_file = "messages_errors_status_{date}.txt".format(
                    date=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
                file = open(error_file, "w")
                file.write('Messages sending failed to following Phone Numbers:\n')
                for error_key in self.errors:
                    file.write("{error}\n".format(error=error_key))
                file.close()

    def enter_and_submit_phone_numbers_data(self, phone_numbers):
        """ Enter data in text fields appearing on form and submit data."""
        print("inside function")
        self.driver = webdriver.Chrome(driver_path)
        self.driver.get(PAGE_URL)
        self.wait_for_element_visibility(css_selector='[type="submit"]')

        numbers = []
        for i in range(0, len(phone_numbers), 5):
            for phone_number_key in phone_numbers[i:i+5]:
                numbers.append(phone_number_key['phone_number'])

            phone_number_string = ','.join(numbers)
            print("\n****************** Chunk of Phone numbers are: ********************\n", phone_number_string)

            send_to_field = self.find_element(css_selector='#id_Send_to')
            send_to_field.clear()
            message_field = self.find_element(css_selector='#id_Message')
            message_field.clear()

            send_to_field.send_keys(phone_number_string)
            message_field.send_keys(spintax.spin("{Hello|Hi}, how are you?"))

            resp_id = self.solve_captcha()
            self.captcha_response_token = self.get_captcha_token(resp_id=resp_id)
            while self.captcha_response_token == '':
                self.captcha_response_token = self.get_captcha_token(resp_id=resp_id)
                self.retrieve_captcha_attempt += 1

            self.driver.execute_script("document.getElementById('g-recaptcha-response').style.removeProperty('display');")
            captcha_response_field = self.find_element(css_selector='#g-recaptcha-response')
            captcha_response_field.clear()
            captcha_response_field.send_keys(self.captcha_response_token)

            submit_button = self.find_element(css_selector='[type="submit"]')
            submit_button.click()

            try:
                self.captcha_response_token = ''
                self.retrieve_captcha_attempt = 0
                self.wait_for_element_visibility(css_selector='.messages .success')
                message_sent_status = self.find_element(css_selector='.messages .success').text
                if "message(s) successfully sent" in message_sent_status:
                    for phone_number_key in phone_numbers:
                        self.success.append(phone_number_key)
                    print("Message sent successfully to these phone numbers: ", phone_number_string)
            except:
                incorrect_numbers = []
                error_contains_phone_number = False
                message_failure_status = self.find_elements(css_selector='.messages li')

                for error_key in message_failure_status:
                    error_text = error_key.text.split()
                    incorrect_numbers.append(error_text[0])
                    error_contains_phone_number = any(char.isdigit() for char in error_text[0])
                    if error_contains_phone_number:
                        self.errors.append(error_text[0])

                if not error_contains_phone_number:
                    for num_key in phone_numbers:
                        self.errors.append(num_key)

                if error_contains_phone_number and len(incorrect_numbers) != len(phone_numbers):
                    for num_key in phone_numbers:
                        if num_key not in incorrect_numbers:
                            self.success.append(num_key)

                if error_contains_phone_number:
                    print("messages sending failed to these phone numbers: ", ",".join(incorrect_numbers))
                else:
                    print("messages sending failed to these phone numbers: ", ",".join(phone_numbers))


    def solve_captcha(self):
        """ Provide captcha related data to Captcha solver API server and get token."""
        print("Sending request to 2Captcha server to solve Captcha!!!")
        resp = requests.post(url="{url}?key={key}&method=userrecaptcha&googlekey={google_key}&pageurl={p_url}&"
                                "json=1".format(url=REQUEST_API_URL, key=API_KEY, google_key=GOOGLE_KEY,
                                                p_url=PAGE_URL))
        response_json = resp.json()
        return response_json["request"]

    def get_captcha_token(self, resp_id):
        end_time = time.time() + TIME_OUT_LIMIT
        if self.retrieve_captcha_attempt == 0:
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
                    self.captcha_response_token = response['request']
                    print("Captcha is resolved now!")
                    break
            except TimeoutError as e:
                print(e)

        return self.captcha_response_token

    def find_element(self, css_selector=''):
        """
        Find and return element.
        Args:
            css_selector: css selector of particular element is used to get the element.
        """
        return self.driver.find_element_by_css_selector(css_selector)

    def find_elements(self, css_selector=''):
        """
        Find and return element.
        Args:
            css_selector: css selector of particular element is used to get the element.
        """
        return self.driver.find_elements_by_css_selector(css_selector)

    def wait_for_element_visibility(self, css_selector='', wait_time=20):
        """
        Wait and check element is visible or not.
        Args:
            css_selector: css selector of particular element is used to check the element visibility.
            wait_time: driver will wait for element to get it visible
        """
        return WebDriverWait(self.driver, wait_time).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    # def tearDown(self):
    #     """ Quit driver."""
    #     self.driver.quit()
