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
                        save_filename: str="test_new_4.wav"):

    start = time()
    v_p = "v2/ko_speaker_4"
    inputs = processor(info_str, voice_preset=v_p).to(DEVICE) 
    speech_output = model.generate(**inputs).cpu().numpy()
    
    sampling_rate = model.generation_config.sample_rate

    write(save_filename, sampling_rate, speech_output[0])

    end = time()
    #print(end-start)

    return speech_output[0]
    

if __name__=="__main__":
    convert_text_to_mp3("엄마는 아빠의 첫사랑이였대! 아빠는 엄마를 쟁취하기 위해 온갇 노력을 다했다더구나.")