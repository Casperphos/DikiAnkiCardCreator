# Author: Casper
# Date: 24-07-2022
# Version: 1.1

import pprint
import re
import shutil

import requests
import DikiParser
import os
import time


def generate_cards(optional_path=None):
    diki_parser = DikiParser.DikiParser()
    path_to_file = initialize_files(optional_path)

    with open(path_to_file, 'r') as f:
        diki_parser.parsing_total = len(f.readlines())

    pages = get_url_list_from_file_containing_webpages(path_to_file)

    if not pages:
        print("Couldn't read file.")
        return None

    generate_csv(diki_parser, pages)
    strip_file("anki_cards.csv")

    #############
    # Info Dump #
    print(f"\nParsed {diki_parser.parsing_total} pages in total.")
    print(f"{diki_parser.parsing_ok} pages were OK.")
    print(f"{diki_parser.parsing_fail} pages failed.")

    if diki_parser.parsing_fail:
        print(f"Pages that failed to be parsed: ")
        pprint.pp(diki_parser.parsing_fail_list)
        print("\n")
    #############


def generate_csv(diki_parser, pages):
    csv_headers = 'Expression;Meaning;Reading\n'

    if os.path.exists("anki_cards.csv"):
        os.remove("anki_cards.csv")

    with open('anki_cards.csv', 'a', encoding="utf-8") as f:
        f.write(csv_headers)

    for page in pages:
        diki_parser.page_url = page
        diki_parser.parse_page()
        time.sleep(2)

        print(f"\nParsing page: "
              f"{diki_parser.page_url} "
              f"[{diki_parser.parsing_fail + diki_parser.parsing_ok}/{diki_parser.parsing_total}]")

        if not diki_parser.parsed_page:
            print(f"Couldn't parse {diki_parser.page_url}.")
            continue

        expression_list = diki_parser.get_expression_list()
        meaning_list = diki_parser.get_meaning_list()
        reading_list = get_images_from_reading_list(
            diki_parser.get_reading_list())

        if not expression_list:
            expression_list = ['NO_EXPRESSIONS_FOUND']

        if not meaning_list:
            meaning_list = ['NO_MEANINGS_FOUND']

        if not reading_list:
            reading_list = ['']     # No reading is OK

        expressions = " | ".join(expression_list) + ';'
        meanings = "\"" + "\n".join(meaning_list) + "\"" + ';'
        readings = " ".join(reading_list) + '\n'

        with open('anki_cards.csv', 'a', encoding="utf-8") as f:
            f.write(expressions)
            f.write(meanings)
            f.write(readings)


def strip_file(file):
    export = ""
    with open(file, 'r') as f:
        for line in f:
            if not line.isspace():
                export += line

    with open(file, "w") as f:
        f.write(export)

###########
# File IO #
###########


def initialize_files(optional_path=None):
    if os.path.isdir('anki_media'):
        print("Found anki_media folder. Cleaning...")
        shutil.rmtree('anki_media')

    os.mkdir('anki_media')
    print("Created directory anki_media.")

    if optional_path:
        path_to_file = optional_path

    if os.path.isfile('_dk.txt') and os.path.getsize('_dk.txt') and not optional_path:
        print("Found file _dk.txt. Omitting input...")
        path_to_file = '_dk.txt'
    elif not optional_path:
        path_to_file = input(
            "Please input path to file containing diki.pl webpages: ")

    if not os.path.isfile(path_to_file) or not os.path.getsize(path_to_file):
        print("File doesn't exist or path to file is wrong.")
        return None

    return path_to_file


def get_url_list_from_file_containing_webpages(path_to_file):
    if not os.path.isfile(path_to_file) or not os.path.getsize(path_to_file):
        print("File doesn't exist.")
        return None

    with open(path_to_file, 'r') as f:
        file_lines = f.read().splitlines()

    r = re.compile(r'www\.diki\.pl')

    for line in file_lines:
        match = re.search(r, line)

        if not match:
            print(f"Line {line} doesn't match regex.")
            return None

    file_lines_seen = set()
    with open(path_to_file, 'r') as f:
        for line in file_lines:
            if line in file_lines_seen:
                print("File contains duplicate lines.")
                return None

            file_lines_seen.add(line)

    return file_lines

####################
# Image downloader #
####################


def get_images_from_reading_list(reading_list):
    if not reading_list:
        print("The reading list is empty. Will not download images.")
        return None

    r = re.compile(r"[^\/]*\.png")

    image_list = []
    for image in reading_list:
        image_url = image
        image = re.search(r, image)

        save_image_from_url(image_url, image.group())
        image_list.append(f"<img src=\"{image.group()}\">")

    return image_list


def save_image_from_url(image_url, image_name):
    image_data = requests.get(image_url).content

    with open('./anki_media/' + image_name, 'wb') as handler:
        handler.write(image_data)
        print(f"Downloaded img: {image_name}")
