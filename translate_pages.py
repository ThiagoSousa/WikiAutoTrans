import argparse
from src.config.config import Config
from src.wikipedia_wrapper.wikipedia_translator import WikipediaTranslator
from src.utils.utils import read_input_file
import logging


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Wikipedia Translator',
                                     description='Reads from a file pages that need to be translated')
    parser.add_argument("input_file", type=str, help="Page to translate to another language")
    parser.add_argument("-verbose", type=bool, help="Whether to print or not", default=True)
    parser.add_argument("-should_save", type=bool, help="Whether to print or not", default=True)
    parser.add_argument("-destination", type=str, help="folder destination, a file title.json will be created there",
                        default=None)

    # parse the arguments
    ARGS, _ = parser.parse_known_args()
    input_file = ARGS.input_file
    verbose = ARGS.verbose
    should_save = ARGS.should_save
    destination = ARGS.destination

    # logging the arguments
    if verbose:
        logging.info(f"Input File: {input_file}")
        logging.info(f"Should Save: {should_save}")
        logging.info(f"Destination: {destination}")

    # build the configuration and WikipediaTranslator objects
    config = Config("src/config/config.json")
    wikipedia_translator = WikipediaTranslator(config, config.config["supported_languages"], verbose=verbose, should_save=should_save)

    # read the page titles to process
    page_titles = read_input_file(input_file)

    # process each page titles
    for source_page, source_language, target_page, target_language in page_titles:

        # check if the languages given are supported in the translation
        if source_language not in config.config["supported_languages"]:
            logging.info(f"{source_language} is not a supported language")
        if target_language not in config.config["supported_languages"]:
            logging.info(f"{target_language} is not a supported language")

        # translate the page from source language to target language
        translated_page = wikipedia_translator.translate_page(page_title=source_page, source_language=source_language,
                                                              target_page_title=target_page,
                                                              target_language=target_language)

        # if a path to persist the translation is given, persist it.
        if destination is not None:
            WikipediaTranslator.persist_page(translated_page, destination)
