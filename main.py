import os
import random
import requests
import shutil

from dotenv import load_dotenv
from url_to_file_utils import download_file, get_file_extension

API_VK_VERSION = 5.131


def check_vk_errors(response):
    if 'error' in response:
        print(response.get('error'))
        raise requests.exceptions.HTTPError


def fetch_xkcd_random_comic(folder):
    comic_folder = 'comics/'
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comics_count = response.json()['num']
    random_comic_number = random.randint(1, comics_count)

    url = f'https://xkcd.com/{random_comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic = response.json()
    comic_url = comic['img']
    comic_alt = comic['alt']
    comic_num = comic['num']
    file_path = f'{folder}{comic_num}{get_file_extension(comic_url)}'
    download_file(file_path, comic_url)
    return file_path, comic_alt


def upload_photo_vk(vk_token, file_path):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': vk_token,
        'v': API_VK_VERSION
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    upload_server = response.json()
    check_vk_errors(upload_server)

    with open(file_path, 'rb') as file:
        url = upload_server['response']['upload_url']
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        uploaded_photo = response.json()
        check_vk_errors(uploaded_photo)

    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload['photo'] = uploaded_photo['photo']
    payload['server'] = uploaded_photo['server']
    payload['hash'] = uploaded_photo['hash']
    response = requests.get(url, params=payload)
    response.raise_for_status()
    saved_photo = response.json()
    check_vk_errors(saved_photo)
    return saved_photo['response'][0]['owner_id'], saved_photo['response'][0]['id']


def post_photo_vk_wall(vk_token, group_id, owner_photo_id, photo_id, message):
    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'access_token': vk_token,
        'v': API_VK_VERSION,
        'owner_id': -group_id,
        'from_group': 1,
        'attachments': f"photo{owner_photo_id}_{photo_id}",
        'message': message
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    wall_posted = response.json()
    check_vk_errors(wall_posted)


def main():
    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    group_id = int(os.getenv('VK_GROUP_ID'))
    folder = 'comics/'
    try:
        file_path, comic_alt = fetch_xkcd_random_comic(folder)
        owner_photo_id, photo_id = upload_photo_vk(vk_token, file_path)
        post_photo_vk_wall(vk_token, group_id, owner_photo_id, photo_id, comic_alt)
    except requests.exceptions.HTTPError:
        print('Ошибка ответа сервера')
    except requests.exceptions.ConnectionError:
        print('Нет ответа от сервера')
    except KeyError:
        print('В ответе от сервера нет запрашиваемых данных')
    finally:
        shutil.rmtree(folder, ignore_errors=True)


if __name__ == '__main__':
    main()
