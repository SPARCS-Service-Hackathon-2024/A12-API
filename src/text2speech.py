from IPython.display import Audio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech
from pydub import AudioSegment
from io import BytesIO
"""
The model can also generate non-verbal communications such as laughing,
sighing and crying. You just have to modify the input text with corresponding cues such as 
[clears throat], [laughter], or ...    
"""

def return_mp3_respone(info_str: str):
    pass

processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")

# add a speaker embedding
print("start")

inputs = processor(text="Don't count the days, make the days count.", return_tensors="pt")

speech_output = model.generate_speech(inputs['input_ids'])

#print("generated end")
#audio = AudioSegment.from_wav(BytesIO(speech_output.cpu().numpy()))
#audio.export("chatbot_response.mp3", format="mp3")

print("audio start")
Audio(speech_output, rate=16000)
print("audio end")