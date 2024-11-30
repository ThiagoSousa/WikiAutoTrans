from typing import Tuple
import os
import json


def read_input_file(input_file: str) -> list[Tuple]:
    """
    Reads the input file if it exists and convert the format to a list of tuple. File format separated by tabs
    :param input_file: file to read from
    :return: list of tuple containing: (source page, source language, target page, target language).
    """

    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"File {input_file} doesn't exist")

    pages = []
    for line in open(input_file, "r").readlines():
        source_page, source_language, target_page, target_language = line.split("\t")
        pages.append((source_page, source_language, target_page, target_language))
    return pages


def persist_page(page_content: dict, destination_path: str):
    """
    Persist page to a file
    :param page_content: content of the page as a dictionary
    :param destination_path: destination file
    :return:
    """

    if not os.path.isdir(destination_path):
        raise FileNotFoundError(f"{destination_path} doesn't exist")

    title = page_content["title"]
    fout = open(f"{destination_path}/{title}.json", "w")
    fout.write(json.dumps(page_content))
    fout.close()
