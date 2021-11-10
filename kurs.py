import requests
import json
from pprint import pprint


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_dir(self, name):
        resource_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        dir_name = 'disk:/' + name + '/'
        params = {"path": dir_name}
        response = requests.put(resource_url, headers=headers, params=params)

        if response.status_code == 201:
            print("Папка " + dir_name + " успешно создана на Яндекс.Диске")
        elif response.status_code == 409:
            print("Папка " + dir_name + " УЖЕ существует на Яндекс.Диске")
        else:
            print("Произошла ошибка при создании папки " + dir_name + "на Яндекс.Диске")
        return dir_name

    def upload_from_url(self, path, url):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": path, "url": url}
        response = requests.post(upload_url, headers=headers, params=params)
        if response.status_code == 202:
            print("Фотография " + path + " успешно загружена на Яндекс.Диск по ссылке " + response.json()['href'])
        else:
            print("Произошла ошибка загрузки фотографии " + path + " на Яндекс.Диск")

    def upload_photo(self, dir_name: str, photos, count=5):
        new_dir = self.create_dir(dir_name)
        i = 0
        for photo in photos:
            if i >= count:
                break
            self.upload_from_url(new_dir + photo, photos[photo][0])
            i += 1


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def load_photos(self, vk_id):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': vk_id,
            'album_id': 'profile',
            'photo_sizes': '1',
            'extended': '1'
        }
        req = requests.get(photos_url, params={**self.params, **photos_params}).json()

        load_photos = {}
        for photo in req['response']['items']:
            temp_data = ''
            for size in photo['sizes']:
                temp_data = size['url'], str(size['height']) + 'x' + str(size['width'])
            name = str(photo['likes']['count']) + '.jpg'
            if name in load_photos.keys():
                name = str(photo['likes']['count']) + '_' + str(photo['date']) + '.jpg'
            load_photos[name] = temp_data

        if load_photos != {}:
            print("Фотографии успешно выгружены из VK для пользователя " + vk_id)
        else:
            print("Нет подходящих фотографий в VK для пользователя " + vk_id)

        return load_photos


def save_file(path_write: str, load_photos):
    name_write = path_write + '/vk_photo.json'
    temp_data = []
    for k in load_photos:
        temp_data.append({'file_name': k, 'size': load_photos[k][1]})
    if temp_data != []:
        with open(name_write, mode='w', encoding="utf8") as f:
            json.dump(temp_data, f)
            f.close()
        print("Информация о фотографиях успешно сохранена в " + name_write)
    else:
        print("Нет информации о фотографиях")

if __name__ == '__main__':
    path_save = "C:/Users/axata/PycharmProjects/pythonProject/res"
    vk_token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

    ya_token = 'AQAAAABTfL9dAADLW4iuuyZ4A0iPlQie49HjMxU'
    vk_id = '552934290'

    vk_client = VkUser(vk_token, '5.131')
    add_photos = vk_client.load_photos(vk_id)
    save_file(path_save, add_photos)
    uploader = YaUploader(ya_token)
    uploader.upload_photo('photo5', add_photos)
