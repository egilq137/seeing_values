import requests
import logging
import random
import json
import os
import time
from dataclasses import dataclass

# ACCESS_CODE = "513bc59a2e454510"
# SECRET_CODE = "a38c651aabdcd237"
# BASE_URL = "https://www.wikiart.org/en/Api/2"


@dataclass
class Painting:
    artist: str
    title: str
    completion_year: int
    response: requests.Response


def get_url(url: str):
    
    MAX_ATTEMPTS = 3 
    for attempt in range(MAX_ATTEMPTS):

        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            logging.info(f'Server problems at attempt {attempt} out of {MAX_ATTEMPTS}')

    return None


def get_list_of_wiki_artists(cache_file='artists_cache.json', max_age_days=7) -> list[dict]:
    if os.path.exists(cache_file):
        age = time.time() - os.path.getmtime(cache_file)
        if age < max_age_days * (24 * 3600):
            with open(cache_file) as f:
                return json.load(f)
            
    list_of_artists_url = "http://www.wikiart.org/en/App/Artist/AlphabetJson?v=new&inPublicDomain=true"
    response = get_url(list_of_artists_url)
    if response is None:
        raise Exception('Max retries reached')

    with open(cache_file, 'w') as f:
        json.dump(response, f)

    return response


def get_paintings_by_artist_url(artist_url: str):
    """ Retrieves full list of paintings given the artist url"""
    url = f"http://www.wikiart.org/en/App/Painting/PaintingsByArtist?artistUrl={artist_url}&json=2"
    paintings = get_url(url)  
    return paintings


def pick_random_painting_from_paintings_by_artist(list_of_paintings: list) -> Painting:
    """ Returns the response object of the selected image"""
    MAX_ATTEMPTS = 3
    for attempt in range(MAX_ATTEMPTS):
        painting = pick_random_element(list_of_paintings)
        painting_response = requests.get(painting['image'])

        if painting_response.status_code == 200: 
            break
        else:
            print(f'not found, attempt {attempt} out of {MAX_ATTEMPTS}')

    return Painting(
        painting['artistName'],
        painting['title'],
        painting['completitionYear'],
        painting_response
        )
    

def pick_random_element(from_list: list):
    return random.choice(from_list)


