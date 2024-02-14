import os
from openai import OpenAI

OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

    
def return_dalle_response(info_str:str=None) -> str:
    response = client.images.generate(
    model="dall-e-3",
    prompt=f"a warm cartoon style. {info_str}",
    size="1024x1024",
    quality="standard",
    n=1,
    )

    image_url = response.data[0].url
    return {"respone": image_url}