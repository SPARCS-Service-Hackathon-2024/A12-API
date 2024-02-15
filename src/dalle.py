import os
from openai import OpenAI

import sys
import re
############## this block is just for import moudles ######
current_path = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
###########################################################

from src.env import get_api_key

OPENAI_API_KEY = get_api_key()
client = OpenAI(api_key=OPENAI_API_KEY)

    
def return_dalle_response(info_str:str=None) -> str:
    response = client.images.generate(
    model="dall-e-3",
    prompt=f"a warm fairy tale style. family with 3 members. {info_str}",
    size="1024x1024",
    quality="standard",
    n=1,
    )

    image_url = response.data[0].url
    return image_url



if __name__=="__main__":
    
    prompt = "I am swimming in the blue ocean with my families."

    url = return_dalle_response(prompt)
    print(url)