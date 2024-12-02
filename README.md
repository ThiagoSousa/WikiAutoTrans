# WikiAutoTrans
Wiki translation and verification of content from different wiki projects. 
The goal is to help making accurate translation of wiki content between different languages.
This project is not intended as a replacement of human editing, but as a helper to increase speed in translating 
articles. Every article translated with WikiAutoTrans should undergo post human
checking. 

### Justification of this project
English Wikipedia contains many articles that does not exist in other languages. Wikipedia's official translation tool 
is [Wikipedia's Content translation tool](https://en.wikipedia.org/wiki/Wikipedia:Content_translation_tool) (CTT). 
For a while I have been working in translating Wikipedia's articles, mostly from English to Portuguese using CTT. 
However, I noticed that translating with the Content's translation has some recurrent issues: 
1. When translating with CTT, it is necessary to translate each section of an article manually; 
2. When CTT fails, it does not perform the initial machine translation correctly, specially when 
there are predefinitions or long texts involved. Sometimes the section is not translated at all, which require manual 
translation.
3. Non-prose elements, such as citations and templates, are often broken in the target language.
4. The entire translation process is time inneficient.
5. [CTT](https://www.mediawiki.org/wiki/Special:MyLanguage/Content_translation) seems to be still under 
development (beta version) and is intended to be used to create a first version of the target translation article, 
which can be further improved later on.  

This project aims to solve some of these problems mentioned above and still adhere to Wikipédia's 
[quality translation](https://www.mediawiki.org/wiki/Help:Content_translation/Translating/Translation_quality) 
principles. Articles created in this way are still required to be reviewed by humans before publishing, but the tool is 
intended improve upon CTT, regarding time-efficiency and translation quality of first version 
machine translated text. These are the following improved:

1. The project provides a reliable translation for the entire article automatically, thus improving time efficiency.
2. The project uses reliable state-of-the-art Large Language Models (LLMs) for machine translation. 
3. Non-prose elements are automatically verified in a post-processing step to fix for unexisting templates or citation 
formats. (this feature has not been fully implemented yet)
4. To avoid bad quality translations, LLMs are instructed to create texts in a fluid, natural reading way in the 
target language by paraphrasing the content to avoid common machine translation issues.

### How does it work?

This project leverages the use of LLMs to translate articles. The current implementation uses OpenAI's ChatGPT.
WikiAutoTrans receives a Wikipedia page in its original language (i.e. English) and the target language of translation 
(i.e. Portuguese). It loads the original Wikipedia page's text and prompts a language model to perfom the translation 
to the target language. The LLM is instructed to perform the translation, not modify nor remove citations and links, 
write the translated text in a neutral tone, and finally, paraphrase the text to avoid undesirable machine translated 
texts. The implementation uses pywikibot library as a core for communicating with the Wikipedia API.

The text passes through pre-processing and post-processing steps to ensure the quality of the translation. 

In the pre-processing step, links to other wikipedia articles are masked to avoid being removed when performing the LLM 
translation.

In the post-processing step, links are then inserted back in the text and the tool automatically searches the version 
of wikipedia article in the target language if it exists. The post-processing also removes templates that does not 
exist in the target language and convert them to available ones where possible.

Currently, the pre- and post-processing steps are not fully implemented. In a future version of this implementation, 
reference objects will also be masked the pre-processing step and unmasked in the post-processing step with the proper 
translation of its features. Moreover, the template conversion is not fully working at the moment and requires human 
checking.

### How to run?

This is a python project, implmented using Python 3.9 and it uses poetry. It is designed to work in Unix systems. 
[Poetry](https://python-poetry.org/docs/) setup can be seen here. Dependencies can be installed with `poetry install`. 
The poetry lock file ensure versions of the packages.

To use the implemented wrapper to ChatGPT, setup an environment variable with your OpenAI Api-key, by the following 
command in your terminal: `export OPENAI_API_KEY= ...`

To use the pywikibot library, it is necessary to create files with Wikipedia user credentials called: `user-config.py` 
and `user-password.py`. The recommended directory to create these files is: `src/config/` and sample files are provided.
To ensure the location can be found by pywikibot library, run the following command on the terminal: 
`export PYWIKIBOT_DIR=<your directory>`, where the directory should contain the `user-config.py` 
and `user-password.py`.

As an optional part. The project contains unit tests to ensure the source code can be executed properly, useful for 
those who want to modify and contribute to the project. To run these tests with poetry:

```poetry run pytest tests.translation```

To perform the translation execute the translate_pages.py script:

```poetry run python -m translate_pages --input_file input/pages_to_translate.txt -verbose True -should_save False -destination output```

* **input_file**: the input file containing the pages to be translated one per line. 
The format is: `source_page_title\tsource_language\ttarget_page_title\ttarget_language`, where `\t` is a tab and the 
source language and target language are a 2-letter language code. For example: `Test	en	teste	pt`
* **should_save**: True or False. whether the script should publish the page automatically or not. Currently, this 
option is disabled as the code for publishing the new translated page is commented.
* **destination**: where to save the output file. This parameter expects an output directory to save the file. A JSON 
file will be created in this location named after the given target title.  
* **verbose**: whether to log the information on the terminal or not. Default `False`.