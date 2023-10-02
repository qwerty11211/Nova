import requests
import os
import openai

def download_image_from_url(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any errors during the request

        with open(save_path, 'wb') as file:
            file.write(response.content)

        print(f"Image downloaded successfully and saved at '{save_path}'")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during image download: {e}")

def generate_new_image():
    openai.api_key = os.environ['openai_token']
    response = openai.Image.create(
    prompt="colorful NFT vibrant painting about famous women scientist in blockchain field",
    n=1,
    size="1024x1024"
    )
    image_url = response['data'][0]['url']
    print(image_url)
    return image_url