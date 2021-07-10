import requests
from os import path
import os
import pdfplumber
import pke
import speech_recognition as sr
from datetime import datetime
from tinytag import TinyTag
from pydub import AudioSegment
import ray

ray.init(address="auto", _redis_password='5241590000000000')

label_num = 6

@ray.remote
def get_top_keys(key_list: list):
    return key_list[0: min(label_num, len(key_list))]

@ray.remote
def pke_formatter(res, filePath):
    return {
        'labels': [keyword[0] for keyword in ray.get(get_top_keys.remote(res))],
        'property': '{' +
        'name: ' + '\'' + path.split(filePath)[1] + '\'' + ', ' +
        'ext: ' + '\'' + path.splitext(filePath)[-1][1:] + '\'' + ', ' +
        'size: ' + '\'' + str(path.getsize(filePath)) + '\''
        + '}'
    }

@ray.remote
def img_formatter(res, filePath):
    return {
        'labels': [item['tag']['en'] for item in ray.get(get_top_keys.remote(res['result']['tags']))],
        'property': '{' +
        'name: ' + '\'' + path.split(filePath)[1] + '\'' + ', ' +
        'ext: ' + '\'' + path.splitext(filePath)[-1][1:] + '\'' + ', ' +
        'size: ' + '\'' + str(path.getsize(filePath)) + '\''
        + '}'
    }

@ray.remote
def meta_data_formatter(res, filePath):
    return {
        'labels': list(res),
        'property': '{' +
        'name: ' + '\'' + path.split(filePath)[1] + '\'' + ', ' +
        'ext: ' + '\'' + path.splitext(filePath)[-1][1:] + '\'' + ', ' +
        'size: ' + '\'' + str(path.getsize(filePath)) + '\''
        + '}'
    }

@ray.remote
def text_tag_str(text: str):
    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(input=text, language='en')
    extractor.candidate_selection()

    extractor.candidate_weighting()

    keyphrases = extractor.get_n_best(n=10)

    return keyphrases

@ray.remote
def text_tag(filePath: str):

    extractor = pke.unsupervised.TopicRank()

    extractor.load_document(input=filePath, language='en')
    extractor.candidate_selection()

    extractor.candidate_weighting()

    keyphrases = extractor.get_n_best(n=10)

    return ray.get(pke_formatter.remote(keyphrases, filePath))

@ray.remote
def pdf_tag(filePath: str):

    pdf_text = ''

    with pdfplumber.open(filePath) as pdf:
        for page in pdf.pages:

            pdf_text += str(page.extract_text())
    return ray.get(pke_formatter.remote(ray.get(text_tag_str.remote(pdf_text)), filePath))

@ray.remote
def img_tag(image_path: str):

    api_key = 'acc_ff4631a20588abc'

    api_secret = 'e770f0f82791079d06b3cd40301295ee'

    response = requests.post(
        'https://api.imagga.com/v2/tags',
        auth=(api_key, api_secret),
        files={'image': open(image_path, 'rb')})
    return ray.get(img_formatter.remote(response.json(), image_path))

@ray.remote
def speech_to_text(filePath: str):
    audioFile = path.join(path.dirname(path.realpath(__file__)), filePath)
    r = sr.Recognizer()
    with sr.AudioFile(audioFile) as source:
        audio = r.record(source)  # read the entire audio file
    # recognize speech using Sphinx

    return r.recognize_sphinx(audio)

    #! EXCEPTIONS

    # except sr.UnknownValueError:

    #     print("Sphinx could not understand audio")

    # except sr.RequestError as e:

    #     print("Sphinx error; {0}".format(e))

@ray.remote
def wav_tag(filePath: str):
    return ray.get(pke_formatter.remote(ray.get(text_tag_str.remote(ray.get(speech_to_text.remote(filePath)))), filePath))

@ray.remote
def audio_tag(filePath: str):
    dst = filePath + '.tmp.wav'

    # convert wav to mp3
    sound = AudioSegment.from_mp3(filePath)

    sound.export(dst, format="wav")

    return_value = ray.get(pke_formatter.remote(ray.get(text_tag_str.remote(
        ray.get(speech_to_text.remote(dst)), filePath))))
    os.remove(dst)

    return return_value

@ray.remote
def video_tag(filePath: str):

    tag = TinyTag.get(filePath)

    return ray.get(meta_data_formatter.remote((tag.artist, tag.title), filePath))


function_table = {
    'txt': text_tag,

    'md': text_tag,

    'pdf': pdf_tag,

    'jpg': img_tag,

    'jpeg': img_tag,

    'png': img_tag,

    'wav': wav_tag,

    'mp3': audio_tag,

    'mp4': video_tag
}


def tagging(filePath: str):
    filePath = "/root/jfs/" + filePath
    filePath = filePath.lower()
    return ray.get(function_table[path.splitext(filePath)[-1][1:]].remote(filePath))


#print(tagging('text.txt'))



