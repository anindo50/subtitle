from translate import Translator
import srt
from concurrent.futures import ThreadPoolExecutor

language_codes = {
    "Afrikaans": "af",
    "Albanian": "sq",
    "Amharic": "am",
    "Arabic": "ar",
    "Armenian": "hy",
    "Azerbaijani": "az",
    "Basque": "eu",
    "Belarusian": "be",
    "Bangla": "bn",  # Bengali
    "Bosnian": "bs",
    "Bulgarian": "bg",
    "Catalan": "ca",
    "Cebuano": "ceb",
    "Chinese": "zh",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Esperanto": "eo",
    "Estonian": "et",
    "Filipino": "tl",
    "Finnish": "fi",
    "French": "fr",
    "Georgian": "ka",
    "German": "de",
    "Greek": "el",
    "Gujarati": "gu",
    "Hindi": "hi",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Igbo": "ig",
    "Indonesian": "id",
    "Itali": "it",  # Italian
    "Japanese": "ja",
    "Kannada": "kn",
    "Korean": "ko",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Nepali": "ne",
    "Portuguese": "pt",
    "Punjabi": "pa",
    "Russian": "ru",
    "Spanish": "es",
    "Tamil": "ta",
    "Telugu": "te",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Vietnamese": "vi",
    "Zulu": "zu"
}

def trans(sub):
    str_sub = str(sub)
    translator = Translator(from_lang="en", to_lang="bn")
    translation = translator.translate(str_sub)
    return translation

def translate_in_parallel(subtitles):
    with ThreadPoolExecutor() as executor:
    
        translated_contents = list(executor.map(trans, [sub.content for sub in subtitles if sub.start and sub.end]))
    
    
    idx = 0
    for sub in subtitles:
        if sub.start and sub.end:
            sub.content = translated_contents[idx]
            idx += 1



with open('sample.srt', 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the content
subtitles = list(srt.parse(content))
# trans_batch(subtitles)
translate_in_parallel(subtitles)


# for subtitle in subtitles:
#     # print(f"Start: {subtitle.start}, End: {subtitle.end}, Text: {subtitle.content}")
#     if subtitle.start and subtitle.end:
#         subtitle.content = trans(subtitle.content)
#         # print(subtitle.content)
translated_srt = srt.compose(subtitles)
with open('trans_sample.srt', 'w', encoding='utf-8') as file:
    file.write(translated_srt)

print("translated")
