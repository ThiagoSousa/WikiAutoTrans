import pytest
import langdetect
from pywikibot import Page, Site

from src.config.config import Config
from src.wikipedia_wrapper.page_doesnt_exist_error import PageDoesntExistError
from src.wikipedia_wrapper.wikipedia_translator import WikipediaTranslator


@pytest.mark.parametrize(
    "page_title,language",
    [
        ("Brasil", "pt"), ("United_States", "en")
    ]
)
def test_retrieve_page_shouldpass(page_title, language):
    config = Config("src/config/config.json")
    wikipedia_translator = WikipediaTranslator(config, ["en", "pt"])

    page = wikipedia_translator.retrieve_page(page_title, language)

    assert len(page.text) > 0
    assert type(page.text) == str
    assert langdetect.detect(page.text) == language


@pytest.mark.parametrize(
    "page_title,language",
    [
        ("balblals", "pt")
    ]
)
def test_retrieve_page_shouldfail(page_title, language):
    config = Config("src/config/config.json")
    wikipedia_translator = WikipediaTranslator(config, ["en", "pt"])

    try:
        wikipedia_translator.retrieve_page(page_title, language)
    except PageDoesntExistError as e:
        assert str(e) == f"Page doesn't exist in the {language} wikipedia"


@pytest.mark.parametrize(
    "text,language",
    [
        ("""Banhado pelo [[Oceano Atlântico]], o Brasil tem um [[Litoral do Brasil|litoral]] ...""", "pt")
    ]
)
def test_preprocess_text(text, language):
    """
    Test to preprocess the text before calling translation
    :param text:
    :param language:
    :return:
    """

    config = Config("src/config/config.json")
    wikipedia_translator = WikipediaTranslator(config, ["en", "pt"])

    page = Page(source=Site(language, 'wikipedia'), title="Test")
    page.text = text

    page, hyperlinks_dict = wikipedia_translator.pre_process_text(page)
    assert "Oceano Atlântico" in hyperlinks_dict.values()
    assert "Litoral do Brasil" in hyperlinks_dict.values()
    assert hyperlinks_dict["LINK0"] == "Oceano Atlântico"
    assert "[[Oceano Atlântico]]" not in page.text
    assert "[[LINK0|Oceano Atlântico]]" in page.text


@pytest.mark.parametrize(
    "text,language",
    [
        ("""Banhado pelo [[Oceano Atlântico]], o Brasil tem um [[Litoral do Brasil|litoral]] ...""", "pt")
    ]
)
def test_find_hyperlinks(text, language):
    """
    Test to find Hyperlinks
    :param text:
    :return:
    """

    config = Config("src/config/config.json")
    wikipedia_translator = WikipediaTranslator(config, ["en", "pt"])

    links = wikipedia_translator.find_hyperlinks(text)
    assert type(links) == list
    assert len(links) == 2
    assert "[[Oceano Atlântico]]" in links and "[[Litoral do Brasil|litoral]]" in links


@pytest.mark.parametrize(
    "text,source_language,target_language",
    [
        ("""Bathed by the [[Atlantic Ocean]], Brazil has a [[Coastline_of_Brazil|coastline]] ...""", "en", "pt")
    ]
)
def test_postprocess_text(text, source_language, target_language):
    """
    Test to post process the text
    :param text:
    :param source_language:
    :param target_language:
    :return:
    """

    config = Config("src/config/config.json")
    wikipedia_translator = WikipediaTranslator(config, ["en", "pt"])

    page = Page(source=Site(source_language, 'wikipedia'), title="Test")
    page.text = text

    page, hyperlinks_dict = wikipedia_translator.pre_process_text(page)

    new_page = wikipedia_translator.post_process(page, hyperlinks_dict, source_language, target_language)
    assert "[[LINK" not in new_page.text
    assert "[[Oceano Atlântico|" in new_page.text
    assert "[[Litoral do Brasil|" in new_page.text


@pytest.mark.parametrize(
    "page_title,source_language,target_page_tile,target_language",
    [
        ("Brazil", "en", "Brasil", "pt")
    ]
)
def test_get_page_target_language(page_title, source_language, target_page_tile, target_language):
    """
    To test the
    :param page_title:
    :param source_language:
    :param target_page_tile:
    :param target_language:
    :return:
    """

    config = Config("src/config/config.json")
    wikipedia_translator = WikipediaTranslator(config, ["en", "pt"])

    page = wikipedia_translator.retrieve_page(page_title, source_language)

    target_page = wikipedia_translator.get_page_target_language(page, target_language)
    assert target_page.title == target_page_tile
