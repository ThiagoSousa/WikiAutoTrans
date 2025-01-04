# import pytest
# from src.translation_engine.translation import ChatGPTTranslator
# import langdetect
#
#
# @pytest.mark.parametrize(
#     "text, source_language, target_language",
#     [
#         ("'''Starship flight test 5''' was the fifth [[flight test]] of a [[SpaceX Starship]] launch vehicle. The [[test article (aerospace)|prototype]] vehicles flown were the Starship [[Starship Ship 30|Ship 30]] upper-stage and Super Heavy [[Super Heavy Booster 12|Booster 12]]. This launch is notable for being the first time an orbital-class rocket has been caught out of mid air.", 'english', 'portuguese')
#     ]
# )
# def test_translation(text, source_language, target_language):
#     translator = ChatGPTTranslator()
#
#     result = translator.perform_translation(text, source_language, target_language, "text")
#
#     print(result)
#
#     assert len(result) > 0
#     assert langdetect.detect(result) == "pt"
#
#
# @pytest.mark.parametrize(
#     "text, source_language, target_language",
#     [
#         ("'''Starship flight test 5'''", 'english', 'portuguese')
#     ]
# )
# def test_title_translation(text, source_language, target_language):
#     translator = ChatGPTTranslator()
#
#     result = translator.perform_translation(text, source_language, target_language, "title")
#
#     print(result)
#
#     assert len(result) > 0
#     assert langdetect.detect(result) == "pt"
