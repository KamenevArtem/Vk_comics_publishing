import requests
import pathlib
import os
import random
import certifi
from dotenv import load_dotenv
from pathlib import Path
from requests import HTTPError


def raise_vk_error(api_response):
    if "error" in api_response:
        error_response = api_response["error"]
        error_code = error_response["error_code"]
        error_msg = error_response["error_msg"]
        raise HTTPError(error_code, error_msg)


def get_random_comic_description():
    current_comic_url = "https://xkcd.com/info.0.json"
    current_comic_response = requests.get(
        current_comic_url,
        verify=certifi.where()
        )
    current_comic_response.raise_for_status()
    current_comic_description = current_comic_response.json()
    total_number_of_comics = current_comic_description['num']
    url_template = "https://xkcd.com/{}/info.0.json"
    random_comic_number = random.randint(1, total_number_of_comics)
    url = url_template.format(random_comic_number)
    response = requests.get(url)
    response.raise_for_status()
    comic_description = response.json()
    comic_url = comic_description['img']
    author_comment = comic_description['alt']
    return comic_url, author_comment


def save_img(link, img_path, params=None):
    response = requests.get(
        link,
        params
        )
    response.raise_for_status()
    with open(img_path, "wb") as saved_img:
        saved_img.write(response.content)


def get_upload_url(access_token, group_id):
    params = {
            'access_token': access_token,
            'group_id': group_id,
            'v': '5.131'
        }
    upload_server_url = "https://api.vk.com/method/photos.getWallUploadServer"
    response = requests.get(
        upload_server_url,
        params
        )
    response.raise_for_status()
    api_response = response.json()
    raise_vk_error(api_response)
    return api_response["response"]["upload_url"]


def upload_comic_to_server(upload_url):
    with open('0.png', 'rb') as image_to_send:
        files = {
           "file": image_to_send,
        }
        posting_response = requests.post(
            upload_url,
            files=files
            )
    posting_response.raise_for_status()
    posting_response = posting_response.json()
    comic_photo = posting_response['photo']
    comic_server = posting_response['server']
    comic_hash = posting_response['hash']
    return comic_photo, comic_server, comic_hash


def save_photo_to_album(access_token, group_id,
                        comic_params, comic_server, comic_hash):
    save_photo_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    save_request_params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': '5.131',
        'photo': comic_params,
        'server': comic_server,
        'hash': comic_hash,
    }
    saving_response = requests.post(
        save_photo_url,
        data=save_request_params
        )
    saving_response.raise_for_status()
    saving_response = saving_response.json()
    raise_vk_error(saving_response)
    owner_id = saving_response['response'][0]['owner_id']
    media_id = saving_response['response'][0]['id']
    return owner_id, media_id


def post_comic_to_wall(access_token, group_id,
                       comment, owner_id, media_id):
    vk_wall_post_url = 'https://api.vk.com/method/wall.post'
    wall_post_params = {
        'access_token': access_token,
        'v': '5.131',
        'owner_id': f"-{group_id}",
        'from_group': '1',
        'attachments': f'photo{owner_id}_{media_id}',
        'message': comment
    }
    posting_response = requests.post(
        vk_wall_post_url,
        data=wall_post_params
        )
    posting_response.raise_for_status()
    posting_response = posting_response.json()
    raise_vk_error(posting_response)
    return posting_response


def main():
    try:
        script_path = pathlib.Path.cwd()
        img_name = "0.png"
        file_path = Path(script_path).joinpath(img_name)
        load_dotenv()
        access_token = os.environ["VK_ACCESS_TOKEN"]
        vk_group_id = os.environ["VK_GROUP_ID"]
        comic_url, author_comment = get_random_comic_description()
        save_img(
            comic_url,
            file_path
            )
        upload_url = get_upload_url(
            access_token,
            vk_group_id
            )
        comic_photo, comic_server, comic_hash = upload_comic_to_server(
            upload_url
            )
        owner_id, media_id = save_photo_to_album(
            access_token,
            vk_group_id,
            comic_photo,
            comic_server,
            comic_hash
            )
        post_comic_to_wall(
            access_token,
            vk_group_id,
            author_comment,
            owner_id,
            media_id)
    finally:
        os.remove(file_path)


if __name__ == "__main__":
    main()
