#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Tushar Mittal (chiragmittal.mittal@gmail.com)
Flask API to return random meme images
"""
import os
import random
from io import BytesIO

import requests
from PIL import Image
from bs4 import BeautifulSoup
from flask import Flask, send_file

app = Flask(__name__)


def get_new_memes_api():
    url = "https://programming-memes-images.p.rapidapi.com/v1/memes"

    headers = {
        "x-rapidapi-key": os.environ['RAPIDAPI_KEY'],
        "x-rapidapi-host": "programming-memes-images.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    memes = response.json()
    images = [meme['image'] for meme in memes]

    return images


def get_new_memes():
    """Scrapers the website and extracts image URLs

    Returns:
        imgs [list]: List of image URLs
    """
    url = 'https://www.memedroid.com/memes/tag/programming'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'lxml')
    pics = soup.find_all('picture')
    imgs = []
    for pic in pics:
        img = pic.find('img')
        imgs.append(img['src'])
    return imgs


def serve_pil_image(pil_img):
    """Stores the downloaded image file in-memory
    and sends it as response

    Args:
        pil_img: Pillow Image object

    Returns:
        [response]: Sends image file as response
    """
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.after_request
def set_response_headers(response):
    """Sets Cache-Control header to no-cache so GitHub
    fetches new image everytime
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route("/", methods=['GET'])
def return_meme():
    img_url = random.choice(get_new_memes())
    res = requests.get(img_url, stream=True)
    res.raw.decode_content = True
    img = Image.open(res.raw)
    return serve_pil_image(img)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
