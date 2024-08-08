#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Tushar Mittal (chiragmittal.mittal@gmail.com)
Flask API to return random meme images
"""
import os
import random
import requests
from PIL import Image
from bs4 import BeautifulSoup
from flask import Flask, send_file
from io import BytesIO

app = Flask(__name__)


def get_new_memes():
    """Scrapers the website and extracts image URLs

    Returns:
        imgs [list]: List of image URLs
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        "Cookie": "PHPSESSID=44ffmkgnot4ihuopf8ot05s1s3; _ga=GA1.2.2105294567.1668857619; "
                  "_gid=GA1.2.1610244212.1668857619; _gat=1",
        'Accept-Language': 'en-US,en;q=0.5'
    }
    url = 'https://www.memedroid.com/memes/tag/programming'
    response = requests.get(url, headers=headers)
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
