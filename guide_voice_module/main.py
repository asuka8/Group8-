from voice import text_to_speech
from language_detect import detect_language
from translation_gpt import Agent

def guide_voice(text, userLang = 'ja'):
    # langSource = ["ja", "en", "zh"]

    # Need translation or not
    if detect_language(text) == userLang:
        text_to_speech(text, userLang)
        return text
    else:
        prompt = f"Help me translate the sentence into '{userLang}'. Directly respond with the translation without any additional text.\n{text}"

        # Place GPT API key here
        Translation = Agent(model = 'gpt-4o', api_key = "sk-")
        response = Translation.communicate(prompt)

        text_to_speech(response, userLang)
        return response

text = "平等院鳳凰堂は京都府宇治市にある寺院で、10円硬貨のデザインにもなっている。平安時代の建築を代表する建物で、ユネスコ世界遺産にも登録されている。"
print(guide_voice(text, 'en')) # ja, en, zh
