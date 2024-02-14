from IPython.display import Audio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech
from pydub import AudioSegment
from io import BytesIO
import torch
from time import time
import librosa
import numpy as np
from scipy.io import wavfile
"""
The model can also generate non-verbal communications such as laughing,
sighing and crying. You just have to modify the input text with corresponding cues such as 
[clears throat], [laughter], or ...    
"""

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(DEVICE)

def convert_text_to_mp3(info_str: str):
    inputs = processor(text=info_str, return_tensors="pt")
        
    with torch.no_grad():
        speech_output = model.generate_speech(inputs['input_ids'].to(DEVICE)).cpu().numpy() #.tobytes()
    
    audio_data = librosa.griffinlim(speech_output)
    
    wavfile.write('output.wav', 11000, audio_data)
    
    return audio_data
    

if __name__=="__main__":
    convert_text_to_mp3("hello world! my name is jonghyo")