from IPython.display import Audio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, BarkModel, AutoProcessor, VitsModel, VitsTokenizer, AutoTokenizer
from io import BytesIO
import torch
from time import time
import numpy as np
from transformers import pipeline
from pydub import AudioSegment
from scipy.io.wavfile import write
import scipy 

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = VitsModel.from_pretrained("facebook/mms-tts-kor")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kor")

text = "안녕 나는 너무 피곤하다 으악"
inputs = tokenizer(text, return_tensors="pt")
print(inputs)
with torch.no_grad():
    output = model(**inputs).waveform ##

# WAV 파일 작성
scipy.io.wavfile.write("techno.wav", rate=model.config.sampling_rate, data=output_np_int16)
