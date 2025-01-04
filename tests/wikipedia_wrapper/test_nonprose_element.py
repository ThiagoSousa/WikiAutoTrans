import pytest
import langdetect
from pywikibot import Page, Site

from src.config.config import Config
from src.wikipedia_wrapper.nonprose_element import HyperLinkElement, ReferenceElement, NonProseElements


@pytest.mark.parametrize(
    "hyperlink_id,hyperlink_text",
    [
        ("LINK0", "[[United States]]"), ("LINK1", "[[United States|USA]]")
    ]
)
def test_create_hyperlink(hyperlink_id, hyperlink_text):
    """
    Test the automatic creation of hyperlinks
    :param hyperlink_id: if of the link
    :param hyperlink_text: text of the hyperlink.
    :return:
    """

    link_element = HyperLinkElement(hyperlink_id, hyperlink_text)
    assert "LINK" in link_element.element_id
    assert hyperlink_text == link_element.text


@pytest.mark.parametrize(
    "reference_id,reference",
    [
        ("REF0", "<ref>{{CIL|14|247}}.</ref>"), ("REF1", "<ref name=\"AE 2005 393\"/>")
    ]
)
def test_create_reference(reference_id, reference):
    """
    Test the automatic creation of references
    :param reference_id: if of the link
    :param reference_text: text of the references.
    :return:
    """

    ref_element = ReferenceElement(reference_id, reference)
    assert "REF" in ref_element.element_id
    assert reference == ref_element.text


@pytest.mark.parametrize(
    "text",
    [
        "Most of the Suellii known from epigraphy lived during [[Roman Empire|imperial times]], when the surnames assumed by the Roman nobility were highly changeable, but a distinct family of the Suellii at [[Ligures Baebiani]], where they bore the cognomina ''Flaccus'' and ''Rufus''.  Both of these belonged to an abundant type of cognomen derived from the physical features of individuals, with ''Flaccus'' designating someone flabby, or with large or floppy ears, while ''Rufus'', \"reddish\", usually referred to someone with red hair.<ref>Chase, pp. 109, 110.</ref><ref>''New College Latin & English Dictionary'', ''s.v. flaccus''.</ref>  This family may have originated at [[Benevento|Beneventum]].<ref name=\"PW Suellius 2\">''PW'', Suellius 2.</ref>  ''Quartus'', the surname of a [[colonia (Roman)|colonial]] family of north Africa, would originally have designated a fourth son or fourth child.<ref>''New College Latin & English Dictionary'', ''s.v. quartus''.</ref>"
    ]
)
def test_find_links(text):
    """
    Test to find the hyperlink in the text
    :param text: given sample text
    :return:
    """

    non_prose_elements = NonProseElements()
    text = non_prose_elements.pre_process_hyperlinks(text)

    assert len(non_prose_elements.hyperlinks) > 0
    assert "[[LINK" in text
    assert non_prose_elements.hyperlinks[0].element_id == "LINK0"
    assert non_prose_elements.hyperlinks[0].text == "Roman Empire"
    assert non_prose_elements.hyperlinks[1].element_id == "LINK1"
    assert non_prose_elements.hyperlinks[1].text == "Ligures Baebiani"


@pytest.mark.parametrize(
    "text",
    [
        "Most of the Suellii known from epigraphy lived during [[Roman Empire|imperial times]], when the surnames assumed by the Roman nobility were highly changeable, but a distinct family of the Suellii at [[Ligures Baebiani]], where they bore the cognomina ''Flaccus'' and ''Rufus''.  Both of these belonged to an abundant type of cognomen derived from the physical features of individuals, with ''Flaccus'' designating someone flabby, or with large or floppy ears, while ''Rufus'', \"reddish\", usually referred to someone with red hair.<ref>Chase, pp. 109, 110.</ref><ref>''New College Latin & English Dictionary'', ''s.v. flaccus''.</ref>  This family may have originated at [[Benevento|Beneventum]].<ref name=\"PW Suellius 2\">''PW'', Suellius 2.</ref>  ''Quartus'', the surname of a [[colonia (Roman)|colonial]] family of north Africa, would originally have designated a fourth son or fourth child.<ref>''New College Latin & English Dictionary'', ''s.v. quartus''.</ref><ref name=\"PW Suellius 2\"/>"
    ]
)
def test_find_references(text):
    """
    Test to find the references in the  text
    :param text: given sample text
    :return:
    """

    non_prose_elements = NonProseElements()
    text = non_prose_elements.pre_process_references(text)

    assert len(non_prose_elements.references) > 0
    assert "REF0" in text
    assert non_prose_elements.references[0].element_id == "REF0"
    assert non_prose_elements.references[0].text == "<ref>Chase, pp. 109, 110.</ref>"
    assert non_prose_elements.references[1].element_id == "REF1"
    assert non_prose_elements.references[1].text == "<ref>''New College Latin & English Dictionary'', ''s.v. flaccus''.</ref>"
    assert non_prose_elements.references[2].element_id == "REF2"
    assert non_prose_elements.references[2].text == "<ref name=\"PW Suellius 2\">''PW'', Suellius 2.</ref>"
    assert non_prose_elements.references[-1].element_id == f"REF{len(non_prose_elements.references)-1}"
    assert non_prose_elements.references[-1].text == "<ref name=\"PW Suellius 2\"/>"
