import json
import os
import requests
from typing import List

def store_data_as_json(data: List[dict], file_name: str) -> None:
    """Saves the given data to a JSON file."""
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)

def retrieve_data_from_json(file_name: str) -> List[dict]:
    """Loads data from a JSON file, or returns an empty list if the file doesn't exist."""
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            return json.load(file)
    return []

def fetch_image(url: str, destination_folder: str) -> str:
    """Downloads an image from the given URL and saves it to the specified folder."""
    image_filename = url.split("/")[-1]
    image_filepath = os.path.join(destination_folder, image_filename)
    os.makedirs(os.path.dirname(image_filepath), exist_ok=True)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(image_filepath, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    return image_filepath
