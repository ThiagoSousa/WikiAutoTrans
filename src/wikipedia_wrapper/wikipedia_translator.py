import pywikibot
from pywikibot.page import Page, Link

from src.config.config import Config
from src.translation_engine.translation import ChatGPTTranslator

from typing import Optional, Tuple
import re

from src.utils.utils import persist_page
from src.wikipedia_wrapper.page_doesnt_exist_error import PageDoesntExistError
from src.wikipedia_wrapper.wiki_not_available_error import WikiNotAvailableError


class WikipediaTranslator:
    """
    Class to wrap the pywikibot
    """

    def __init__(self, config: Config, wiki_languages=None, verbose: bool = True, should_save: bool = True):
        """
        Constructor for the wikipedia wrapper
        :param config: configuration object
        :param wiki_languages: list of wikilanguages
        :param verbose: Verbose or not
        """

        # if no languages are informed, then the default is en, pt
        if wiki_languages is None:
            wiki_languages = ["en", "pt"]

        # set up the summary
        self.translation_summary = config.config["translation_summary"]
        self.wikidata_summary = config.config["wikidata_summary"]
        self.wikidata_sitelink = config.config["wikidata_sitelink"]
        self.print_template = config.config["print_template"]
        self.wikipedia_linksite = config.config["wikipedia_linksite"]
        self.language_dict = config.config["language_dict"]

        # predefinitions
        self.non_existing_predefinitions = config.config["non_existing_predefinitions"]

        # create the wikipedia object and login on it
        self.wiki = dict()
        for language in wiki_languages:
            self.wiki[language] = pywikibot.Site(language, config.config["wikiproject"])

        # translator object
        self.translator = ChatGPTTranslator(model="gpt-4o-mini", config=config)

        # verbose parameter
        self.verbose = verbose
        self.should_save = should_save

    def retrieve_page(self, page_title: str, wiki_language: str = "en") -> pywikibot.Page:
        """
        Retrieve the page
        :param page_title: title of the page
        :param wiki_language: which language to retrieve the page from
        :return: pywikibot page object
        """

        if wiki_language not in self.wiki:
            raise WikiNotAvailableError("Wiki language not aviable")

        page = pywikibot.Page(self.wiki[wiki_language], page_title)
        if page.exists():
            return page
        else:
            raise PageDoesntExistError(f"Page doesn't exist in the {wiki_language} wikipedia")

    def translate_page(self, page_title: str, source_language: str = "en", target_language: str = "pt",
                       target_page_title: Optional[str] = None) -> Optional[Page]:
        """
        Translate a given page
        :param page_title: name of the page in the source language
        :param source_language: original language
        :param target_language: target language
        :param target_page_title: name of the page to be created in the target language
        :return: True or False it was translated correctly.
        """

        # get the wikipedia page
        original_page = self.retrieve_page(page_title, source_language)
        if self.verbose:
            self.print_page(original_page)

        # check if translation already exists
        link = self.get_page_target_language(original_page, target_language)

        # if page in the target language doesn't exist yet.
        if link is None:

            # preprocess the page to deal with hyperlinks
            original_page, hyperlinks_dict = self.pre_process_text(original_page)

            # translate text and title
            translated_text = self.translator.perform_translation(original_page.text, source_language, target_language,
                                                                  translation_type="text")
            if target_page_title is None:
                target_page_title = self.translator.perform_translation(original_page.title(), source_language, target_language,
                                                                        translation_type="title")

            # create a new page and set the text
            new_page = Page(source=self.wiki[target_language], title=target_page_title)
            new_page.text = translated_text
            if self.verbose:
                self.print_page(new_page)

            # post process the links to deal with them
            new_page = self.post_process(new_page, hyperlinks_dict, source_language, target_language)
            if self.verbose:
                self.print_page(new_page)

            # save the page and update the language link in wikidata
            # if self.should_save:
            #     new_page.save(self.generate_summary(page_title, source_language))
            #     self.set_language_link(original_page, new_page, target_language)
            return new_page
        return None

    def pre_process_text(self, page: Page) -> Tuple[Page, dict]:
        """
        v2 of how to preprocess hyperlinks
        :param page: page object
        :return: tuple containing the page after processing and the hyperlinks dictionary
        """

        # retrieve the links in the text
        text = page.text
        links = self.find_hyperlinks(text)

        # build a dictionary and mask the links in the text
        hyperlinks_dict = {}
        for i, link in enumerate(links):

            if "|" in link:
                hyperlink = link.split("|")[0].replace("[[", "")
                link_name = link.split("|")[1].replace("]]", "")

                text = text.replace(link, f"[[LINK{i}|{link_name}]]")

                hyperlinks_dict[f"LINK{i}"] = hyperlink
            else:
                link_name = link.replace("[[", "").replace("]]", "")
                text = text.replace(link, f"[[LINK{i}|{link_name}]]")

                hyperlinks_dict[f"LINK{i}"] = link_name

        # put the text back in the page and return the page with hyperlinks
        page.text = text
        return page, hyperlinks_dict

    @staticmethod
    def find_hyperlinks(text: str) -> list[str]:
        """
        Find the hyperlinks in the text
        :param text:
        :return: list of links matched from the text
        """

        return re.findall("\[\[.+?\]\]", text)

    def post_process(self, page: Page, hyperlinks_dict: dict[str, str], source_language: str = "en",
                     target_language: str = "pt") -> Page:
        """
        Post process the wiki page after the translation is done
        :param page:
        :param hyperlinks_dict: dictionary of the links, built in the preprocess function
        :param source_language: source language
        :param target_language: target language
        :return: page
        """

        # retrieve the page's text
        text = page.text

        # iterate through the hyperlinks to replace the links in the text
        for code, page_name in hyperlinks_dict.items():

            # retrieve the linked page in the hyperlink, get its equivalent in the target language. If it doesn't exist
            try:
                linked_page = self.retrieve_page(page_name, source_language)
                target_page = self.get_page_target_language(linked_page, target_language)
            except WikiNotAvailableError:
                target_page = None
            except PageDoesntExistError:
                target_page = None

            # replace the target links with the correct code
            if target_page is not None:
                target_link = str(target_page).replace(f"{target_language}:", "").replace("[[", "").replace("]]", "")
                text = text.replace(code+"|", target_link+"|")
            else:
                text = re.sub(f"\[\[{code}\|(.+?)\]\]", r"\1", text)
        page.text = text

        # post process the predefinitions
        page = self.post_process_predefinitions(page, target_language)

        return page

    def post_process_predefinitions(self, page: Page, language: str) -> Page:
        """
        Post process the nonexisting predefinition and incorrect translations
        :param page: pywikibot page object
        :param language: target language
        :return: pywikibot page object with fixed predefinitons
        """

        text = page.text
        for predefinition in self.non_existing_predefinitions[language]:
            text = text.replace(predefinition, "")
        page.text = text
        return page

    def get_page_target_language(self, page: Page, target_language: str = "pt") -> Optional[Link]:
        """
        Get the page in the target language
        :param page: source page
        :param target_language: target language to check
        :return: the page in the target language
        """

        # iterate through the links looking for the language of the page.
        for link in page.langlinks():
            if str(link.site) == self.wikipedia_linksite.replace("{target_language}", target_language):
                return link
        return None

    def generate_summary(self, page_title: str, source_language: str) -> str:
        """
        Generate Summary to Publish/save the page in the wiki project
        :param page_title: title of the source page.
        :param source_language: source language
        :return: summary for saving in the wiki project
        """

        summary_template = self.translation_summary[source_language]
        summary_template = summary_template.replace("{long_source_language}", self.language_dict[source_language])
        summary_template = summary_template.replace("{source_language}", source_language)
        summary_template = summary_template.replace("{page_title}", page_title)

        return summary_template

    def set_language_link(self, page: Page, new_page: Page, target_language: str):
        """
        Update the language link
        :param page: original Page object
        :param new_page: newly created page translated from the original page
        :param target_language: target language
        :return:
        """

        item = pywikibot.ItemPage.fromPage(page)
        item.get()
        item.setSitelink(sitelink={'site': self.wikidata_sitelink.replace("{target_language}", target_language),
                                   'title': new_page.title()},
                         summary=self.wikidata_summary.replace("{target_language}", target_language))

    def print_page(self, page: Page) -> None:
        """
        Print a pywikibot page
        :param page: pywikibot page object
        :return:
        """

        page_str = self.print_template.replace("{title}", page.title()).replace("{text}", page.text)

        print(page_str)

    @staticmethod
    def persist_page(page: Page, destination_path: str):
        """
        Persist page to a local file
        :param page: page object
        :param destination_path: where to save the page
        :return:
        """

        persist_page({"title": page.title(), "text": page.text}, destination_path)
