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

def convert_text_to_mp3(user:str,
                        info_str: str,
                        cnt: int=0):

    start = time()
    
   
    v_p = "v2/ko_speaker_0" # Korean Female Voice : https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683?v=bc67cff786b04b50b3ceb756fd05f68c 
    inputs = processor(info_str, voice_preset = v_p).to(DEVICE)
    speech_output = model.generate(**inputs).cpu().numpy() 
    
    sampling_rate = model.generation_config.sample_rate
    
    save_url = f"/home/elicer/src/A12-API/wav_disk/{user}_{cnt}"
    write(save_url, sampling_rate, speech_output[0])

    end = time()
    #print(end-start)

    return save_url
    

if __name__=="__main__":
    output = convert_text_to_mp3("jonghyo","나는 가족들과 즐거운 시간을 보냈어. 여행을 가족들과 같이 많이 다니지 못해서 아쉬워.",0)
    # print(f'shape ={output.shape}') # shape =(297600,)
    # print(output) #[7.8684650e-04 3.9406144e-04 5.0455559e-04 ... 7.6108990e-05 8.5913998e-05 8.5368316e-05]