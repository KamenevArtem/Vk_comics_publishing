import requests
import pathlib
import os
import random
from dotenv import load_dotenv
from pathlib import Path


def download_comics():
    url_template = "https://xkcd.com/{}/info.0.json"
    serial_number = random.randint(1, 614)
    url = url_template.format(serial_number)
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    comics_url = response['img']
    author_comment = response['alt']
    return comics_url, author_comment


def saving_img(link, im_path, params=None):
    response = requests.get(link, params)
    response.raise_for_status()
    with open(im_path, "wb") as saved_img:
        saved_img.write(response.content)


def vk_post_photo(access_token, comment, group_id):
    params = {
        'access_token': access_token,
        'group_id': '217905382',
        'v': '5.131'
    }
    upload_server_url = "https://api.vk.com/method/photos.getWallUploadServer"
    response = requests.get(upload_server_url, params)
    response.raise_for_status()
    api_response = response.json()["response"]
    upload_url = api_response['upload_url']
    image = open('0.png', 'rb')
    files = {
        "file": image,
    }
    post_photo = requests.post(upload_url, files=files)
    post_photo.raise_for_status()
    post_photo = post_photo.json()
    save_photo_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    save_request_params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': '5.131',
        'photo': post_photo['photo'],
        'server': post_photo['server'],
        'hash': post_photo['hash'],
    }
    save_posted_photo = requests.post(save_photo_url, data = save_request_params)
    save_posted_photo.raise_for_status()
    saving_response = save_posted_photo.json()['response']
    owner_id = saving_response[0]['owner_id']
    media_id = saving_response[0]['id']
    vk_wall_post_url = 'https://api.vk.com/method/wall.post'
    wall_post_params = {
        'access_token': access_token,
        'v': '5.131',
        'owner_id': '-217905382',
        'from_group': '1',
        'attachments': f'photo{owner_id}_{media_id}',
        'message': comment
    }
    post_to_the_wall = requests.post(vk_wall_post_url, data = wall_post_params)
    post_to_the_wall.raise_for_status()


def main():
    load_dotenv()
    access_token = os.environ["VK_ACCESS_TOKEN"]
    group_id = os.environ["GROUP_ID"]
    comics_url, author_comment = download_comics()
    script_path = pathlib.Path.cwd()
    img_name = f"0.png"
    file_path = Path(script_path).joinpath(img_name)
    saving_img(comics_url, file_path)
    vk_post_photo(access_token, author_comment, group_id)
    os.remove(file_path)


if __name__ == "__main__":
    main()
