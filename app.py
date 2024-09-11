# from flask import Flask, request, send_file, jsonify
# from flask_cors import CORS
# import srt
# from translate import Translator
# # from googletrans import Translator
# from concurrent.futures import ThreadPoolExecutor
# from download import download
# import requests
# import httpx


# app = Flask(__name__)
# CORS(app)  # Enable CORS for cross-origin requests

# # Translation function
# def trans(sub,tolang):
#     str_sub = str(sub)
#     tolang = str(tolang)
#     translator = Translator(from_lang="en", to_lang=tolang)
#     translation = translator.translate(str_sub)
#     return translation


# # def trans(sub, tolang):
# #     str_sub = str(sub)
# #     tolang = str(tolang)
    
# #     url = "https://api.translate.com/translate"  # Replace with the correct URL for your translation service
# #     headers = {
# #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",

# #         "Content-Type": "application/x-www-form-urlencoded"
# #     }
# #     data = {
# #         "text": str_sub,
# #         "to": tolang,
# #         "from": "en"
# #     }
    
# #     response = httpx.post(url, headers=headers, data=data)
    
# #     if response.status_code == 200:
# #         # Parse the response to get the translated text
# #         translation = response.json().get("translatedText", "")
# #         return translation
# #     else:
# #         raise Exception(f"Failed to translate text. Status code: {response.status_code}, Response: {response.text}")

# # Parallel translation function
# def translate_in_parallel(subtitles, tolang):
#     with ThreadPoolExecutor() as executor:
        
#         translated_contents = list(executor.map(lambda sub: trans(sub.content, tolang), 
#                                                 [sub for sub in subtitles if sub.start and sub.end]))


#     idx = 0
#     for sub in subtitles:
#         if sub.start and sub.end:
#             sub.content = translated_contents[idx] 
#             idx += 1


# def download_file(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         file_path = 'downloaded.srt'
#         with open(file_path, 'wb') as f:
#             f.write(response.content)
#         return file_path
#     else:
#         raise Exception(f"Failed to download file. Status code: {response.status_code}")


# file_path = ""
# file_name = ""
# srt_content = ""
# @app.route('/trans', methods=['POST'])
# def translate_srt():
    
#     if 'to_lang' not in request.form:
#         return jsonify({"error": "target language not provided"}), 400
    
#     if request.form['file_url'] and request.files['file'] == "":
#         return jsonify({"error": "provide srt file or link"}), 400
    
#     if request.form['file_url'] != "":
#         url = request.form['file_url']
#         file_name = "web_sub.srt"
#         url = str(url)
#         file_path = download(url,file_name)
#         print(file_path)
#         with open(file_path, 'r', encoding='utf-8') as f:
#             srt_content = f.read() 
#         subtitles = list(srt.parse(srt_content))
#         print(file_path)

#     elif 'file' in request.files:
#         file = request.files['file']
#         srt_content = file.read().decode('utf-8')
#         subtitles = list(srt.parse(srt_content))
    

    
#     to_lang = request.form['to_lang']

#     # Parse the content using the `srt` library
    
#     # Translate the subtitles
#     translate_in_parallel(subtitles,to_lang)

#     # Create a translated SRT file
#     translated_srt = srt.compose(subtitles)

#     translated_file_path = "translated_b.srt"
#     with open(translated_file_path, 'w', encoding='utf-8') as f:
#         f.write(translated_srt)

#     return send_file(translated_file_path, as_attachment=True)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
import srt
from googletrans import Translator
from concurrent.futures import ThreadPoolExecutor
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Translation function
def trans(sub, tolang):
    try:
        translator = Translator()  # Initialize the Translator
        # Translate the subtitle content
        translated = translator.translate(text=sub, dest=tolang)
        return translated.text  # Return the translated text
    except Exception as e:
        raise Exception(f"Failed to translate text: {str(e)}")

# Parallel translation function
def translate_in_parallel(subtitles, tolang):
    with ThreadPoolExecutor() as executor:
        translated_contents = list(
            executor.map(
                lambda sub: trans(sub.content, tolang),
                [sub for sub in subtitles if sub.start and sub.end]
            )
        )

    idx = 0
    for sub in subtitles:
        if sub.start and sub.end:
            sub.content = translated_contents[idx]
            idx += 1

# Function to download file from URL
def download_file(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join('temp', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    else:
        raise Exception(f"Failed to download file. Status code: {response.status_code}")

@app.route('/trans', methods=['POST'])
def translate_srt():
    print("In the API route")

    # Get JSON data from the request
    data = request.json

    # Debugging: Print the received data
    print("Received data:", data)

    # Check if 'to_lang' is provided in the request
    if 'to_lang' not in data:
        return jsonify({"error": "Target language not provided"}), 400
    
    to_lang = data['to_lang']
    srt_content = ""
    subtitles = []

    # Handle file URL
    if 'file_url' in data and data['file_url']:
        file_url = data['file_url']
        file_name = "downloaded.srt"
        file_path = download_file(file_url, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        subtitles = list(srt.parse(srt_content))
        os.remove(file_path)  # Clean up the downloaded file
        print(f"Downloaded file: {file_path}")

    # Handle file upload
    elif 'file' in request.files:
        file = request.files['file']
        srt_content = file.read().decode('utf-8')
        subtitles = list(srt.parse(srt_content))
    else:
        return jsonify({"error": "Provide either an SRT file or file URL"}), 400

    # Translate subtitles
    try:
        translate_in_parallel(subtitles, to_lang)
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

    # Create translated SRT content
    translated_srt = srt.compose(subtitles)

    # Return translated SRT content as JSON
    return jsonify({"translatedSubtitle": translated_srt})

if __name__ == '__main__':
    app.run(debug=True)