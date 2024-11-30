from abc import ABC, abstractmethod
from openai import OpenAI
from typing import Optional
from src.config.config import Config


class Translator(ABC):
    """
    Translation class
    """

    @abstractmethod
    def perform_translation(self, text: str, source_language: str = "english", target_language: str = "portuguese",
                            translation_type: str = "text") -> str:
        """
        Execute the translation
        :param text: given text
        :param source_language: source language, default is english
        :param target_language: target language, default is portuguese
        :param translation_type: content to translate
        :return: translated text
        """

        raise NotImplementedError("Subclasses should implement this!")


class ChatGPTTranslator(Translator):
    """
    Chat GPT Translator class
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: int = 0, timeout: float = 300,
                 config: Optional[Config] = None):
        """
        Constructor class
        :param model: model name
        :param temperature: temperature value
        :param timeout: timeout for connecting to openai
        """

        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.client = OpenAI()

        self.translation_prompt = {}
        if config is not None:
            self.translation_prompt = config.config["translation_prompt"]

        self.default_behaviour = "Translate the text from {source_language} to {target_language}."

    def perform_translation(self, text: str, source_language: str = "english", target_language: str = "portuguese",
                            translation_type: str = "text") -> str:
        """
        Execute the translation
        :param text: given text
        :param source_language: source language, default is english
        :param target_language: target language, default is portuguese
        :param translation_type: content to translation
        :return: translated text
        """

        # build the prompt  message for translation
        messages = []
        context = self.translation_prompt.get(translation_type, self.default_behaviour).\
            replace("{source_language}", source_language).\
            replace("{target_language}", target_language)
        messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": text})

        # response message
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            timeout=self.timeout
        )

        # output message
        return response.choices[0].message.content
