import speech_recognition as sr
from pydub import AudioSegment
import os
import sys
import soundfile

r = sr.Recognizer()

def convert_mp3_to_text(path:str): #현재는 path로, 이후 wav 파일로 변경 필요
    
    data, samplerate = soundfile.read(path)
    soundfile.write(path, data, samplerate, subtype='PCM_16')

    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        # try converting it to text
        text = r.recognize_google(audio_listened, language='ko-KR')

    return text


if __name__=="__main__":
    convert_mp3_to_text("test.wav")