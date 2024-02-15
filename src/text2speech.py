from IPython.display import Audio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, BarkModel, AutoProcessor, VitsModel, VitsTokenizer
from io import BytesIO
import torch
from time import time
import numpy as np
from transformers import pipeline
from pydub import AudioSegment
from scipy.io.wavfile import write

"""
The model can also generate non-verbal communications such as laughing,
sighing and crying. You just have to modify the input text with corresponding cues such as 
[clears throat], [laughter], or ...    
"""

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = BarkModel.from_pretrained("suno/bark").to(DEVICE) #
model =  model.to_bettertransformer()
#model.enable_cpu_offload()

processor = AutoProcessor.from_pretrained("suno/bark") #

def convert_text_to_mp3(info_str: str,
                        save_filename: str="test.wav"):

    start = time()
 
    inputs = processor(info_str, voice_preset="v2/ko_speaker_9").to(DEVICE)
    speech_output = model.generate(**inputs).cpu().numpy()
    
    sampling_rate = model.generation_config.sample_rate

    write(save_filename, sampling_rate, speech_output[0])

    end = time()
    #print(end-start)

    return speech_output[0]
    

if __name__=="__main__":
    convert_text_to_mp3("나는 가족들과 즐거운 시간을 보냈어. 여행을 가족들과 같이 많이 다니지 못해서 아쉬워.")