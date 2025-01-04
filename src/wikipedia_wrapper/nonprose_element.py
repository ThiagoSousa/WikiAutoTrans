from abc import ABC, abstractmethod
import re


class NonProseElement(ABC):
    """
    Abstract Class to represent non prose elements such as references, links, templates, etc.
    """

    @abstractmethod
    def get_element_text(self):
        """
        Abstract method to get the element
        :return:
        """

        raise NotImplementedError("Subclasses should implement this!")

    @abstractmethod
    def translate_element(self, target_language: str):
        """
        Abstract method to translate the element, not applicable to all cases.
        :return:
        """

        raise NotImplementedError("Subclasses should implement this!")


class HyperLinkElement(NonProseElement):
    """
    Class to represent Hyperlink elements
    """

    def __init__(self, element_id: str, text: str):
        """
        Hyperlink Element
        :param element_id: masked id of the hyperlink
        :param text: hyperlink itself
        """
        super().__init__()
        self.element_id = element_id
        self.text = text

    def get_element_text(self):
        """
        Getter for the element's text
        :return:
        """

        return self.text

    def translate_element(self, target_language: str):
        """
        Translate the Element to another language
        :param target_language: target language
        :return:
        """
        pass


class ReferenceElement(NonProseElement):
    """
    Class to represent the reference's within a wiki text
    """

    def __init__(self, element_id: str, text: str):
        """
        References element constructor
        :param element_id: masked id of the reference
        :param text: the entire xml containing the reference
        """
        super().__init__()
        self.element_id = element_id
        self.text = text

    def get_element_text(self):
        """
        Getter for the reference object
        :return:
        """
        return self.text

    def translate_element(self, target_language: str):
        """
        Translate the Reference to another language
        :param target_language: target language
        :return:
        """
        pass


class NonProseElements:
    """
    Class to represent the list of non-prose elements of a page
    """

    def __init__(self):
        """
        Instantiate the class and a list of hyperlinks and references
        """

        self.hyperlinks: list[HyperLinkElement] = []
        self.references: list[ReferenceElement] = []

    def add_hyperlink(self, link: str) -> str:
        """
        Add a new link to the list of hyperlinks
        :param link: link content
        :return: the link id
        """

        link_id = f"LINK{len(self.hyperlinks)}"
        self.hyperlinks.append(HyperLinkElement(link_id, link))

        return link_id

    def pre_process_hyperlinks(self, text: str) -> str:
        """
        Preprocess the links to mask them with labels
        text: text to look for the links
        :return: text after preprocessed with the masked links
        """

        # retrieve the links in the text
        links = self.find_hyperlinks(text)

        # build a dictionary and mask the links in the text
        for link in links:

            if "|" in link:
                hyperlink = link.split("|")[0].replace("[[", "")
                link_text = link.split("|")[1].replace("]]", "")
                link_id = self.add_hyperlink(hyperlink)

                text = text.replace(link, f"[[{link_id}|{link_text}]]")
            else:
                link_text = link.replace("[[", "").replace("]]", "")
                link_id = self.add_hyperlink(link_text)

                text = text.replace(link, f"[[{link_id}|{link_text}]]")

        return text

    @staticmethod
    def find_hyperlinks(text: str) -> list[str]:
        """
        Find the hyperlinks in the page
        :param text: text to look for hyperlinks
        :return: list of links matched from the text
        """

        return re.findall(r"\[\[.+?\]\]", text)

    def add_reference(self, reference_text: str) -> str:
        """
        Add a new reference to the list of references
        :param reference_text: the entire xml of a reference
        :return:
        """

        reference_id = f"REF{len(self.references)}"
        self.references.append(ReferenceElement(reference_id, reference_text))

        return reference_id

    def pre_process_references(self, text: str) -> str:
        """
        Preprocess the references within a page
        text: text to look for the references
        :return: text after preprocessed with the masked references
        """

        # retrieve the links in the text
        references = self.find_xml_references(text)

        # build a dictionary and mask the links in the text
        for ref in references:
            ref_id = self.add_reference(ref)
            text = text.replace(ref, f"<{ref_id}>")

        return text

    @staticmethod
    def find_xml_references(text):
        """
        Find the XML references in a wiki page
        :param text: text to look for references
        :return: list of the references
        """

        references = re.findall(r"<ref(?: name=\".+?\")?\/?>(?:.+?<\/ref>)?", text)
        print(references)

        return references

    def post_process_hyperlinks(self, text: str) -> str:
        """
        Post process the hyperlinks
        :param text: masked text
        :return:
        """
