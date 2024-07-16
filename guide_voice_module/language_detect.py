from langdetect import detect

def detect_language(text):
    try:
        lang = detect(text)
        if lang == 'en':
            return "en"
        elif lang == 'ja':
            return "ja"
        elif lang == 'zh-cn' or lang == 'zh-tw':
            return "zh"
        else:
            return "Unknown language"
    except Exception as e:
        return str(e)
