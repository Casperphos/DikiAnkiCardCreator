# Author: Casper
# Date: 24-07-2022
# Version: 1.1

import time
from bs4 import BeautifulSoup
import requests


class DikiParser:
    def __init__(self):
        self.page_url = None
        self.parsed_page = None
        self.parsing_total = 0
        self.parsing_ok = 0
        self.parsing_fail = 0
        self.parsing_fail_list = []

    def parse_page(self):
        if not self.page_url:
            print("Couldn't find page url.")
            return

        self.parsed_page = requests.get(self.page_url)

        if self.parsed_page.status_code != 200:
            print("Couldn't connect to webpage. Retrying...")
            time.sleep(5)
            self.parsed_page = requests.get(self.page_url)

        if self.parsed_page.status_code != 200:
            print("Couldn't connect to webpage.")
            self.parsed_page = None
            self.parsing_fail += 1
            self.parsing_fail_list.append(self.page_url)
            return

        self.parsed_page = BeautifulSoup(
            self.parsed_page.content, 'html.parser')
        parsed_div = self.parsed_page.find('div', 'diki-results-left-column')

        if not parsed_div:
            print("Couldn't find dictionary entity.")
            self.parsed_page = None
            self.parsing_fail += 1
            self.parsing_fail_list.append(self.page_url)
            return

        self.parsing_ok += 1
        self.parsed_page = parsed_div

    def get_expression_list(self):
        if not self.parsed_page:
            print("Parsed webpage couldn't be found.")
            return None

        parsed_expressions = self.parsed_page.select("h1 span.hw")

        if not parsed_expressions:
            print("Couldn't read expressions from parsed webpage.")
            self.parsing_fail += 1
            self.parsing_ok -= 1
            self.parsing_fail_list.append(self.page_url)
            return None

        expression_list = []
        for expression in parsed_expressions:
            expression_list.append(expression.getText().strip())

        return expression_list

    def get_meaning_list(self):
        if not self.parsed_page:
            print("Parsed webpage couldn't be found.")
            return None

        parsed_meanings = self.parsed_page.select(
            'ol.foreignToNativeMeanings span.hw')

        if not parsed_meanings:
            print("Couldn't read meanings from parsed webpage.")
            self.parsing_fail += 1
            self.parsing_ok -= 1
            self.parsing_fail_list.append(self.page_url)
            return None

        meaning_counter = 1
        meaning_list = []
        for meaning in parsed_meanings:
            meaning_list.append(str(meaning_counter) +
                                ". " + meaning.getText().strip())
            meaning_counter += 1

        return meaning_list

    def get_reading_list(self):
        if not self.parsed_page:
            print("Parsed webpage couldn't be found.")
            return None

        parsed_readings = self.parsed_page.select(
            'span.phoneticTranscription img[src]')

        if not parsed_readings:
            print("Couldn't read readings from parsed webpage. Omitting...")
            return None

        reading_list = []
        for reading in parsed_readings:
            reading_list.append(reading['src'])

        return reading_list
