import configparser
import requests
from pprint import pprint
import json
from tqdm import tqdm


config = configparser.ConfigParser()
config.read("settings.ini")

vk_token = config["Tokens"]["vk_token"]


class VK:
    """
    Класс взаимодействия API VK.
    """
    def __init__(self, token: str, version: str = "5.199") -> None:
        """
        Инициализирует экземпляр класса VK с заданными параметрами токена и версии API.
        Устанавливает параметры для запросов к API и базовый URL.
        :param token: токен доступа к API ВКонтакте.
        :param version: (по умолчанию “5.199”) версия API ВКонтакте.
        """
        self.params = {
            "access_token": token,
            "v": version,
        }
        self.base = 'https://api.vk.com/method/'

    def get_photo(self, user_id: str, count: int = 5, album_id: str = "profile") -> dict:
        """
        Отправляет запрос к API ВКонтакте для получения фотографий пользователя.
        Проверяет ответ на наличие ошибок и возвращает JSON-ответ от API.
        В случае ошибки выбрасывает исключение с кодом ошибки и сообщением.
        :param user_id: ID пользователя ВКонтакте.
        :param count: (по умолчанию 5) количество фотографий для загрузки.
        :param album_id: (по умолчанию “profile”) ID альбома, из которого загружаются фотографии.
        :return: JSON с информацией по фото.
        """
        url = f'{self.base}photos.get'
        params = {
            'owner_id': user_id,
            'count': count,
            'album_id': album_id,
            'extended': 1
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        json_from_vk = response.json()
        if "error" in json_from_vk:
            error_code = json_from_vk["error"]["error_code"]
            error_msg = json_from_vk["error"]["error_msg"]
            raise ValueError(f"Произошла ошибка. Код ошибки: {error_code} {error_msg}.")
        return json_from_vk


class Photo:
    """
    Класс для обработки JSON результата запроса VK.
    """
    def __init__(self, json_from_vk: dict) -> None:
        """
        Инициализирует экземпляр класса Photo с переданным JSON-ответом от API ВКонтакте.
        Сохраняет ответ в атрибуте json_from_vk и инициализирует пустой список result
        для хранения информации о фотографиях.
        :param json_from_vk: JSON-ответ от API VK
        """
        self.json_from_vk = json_from_vk
        self.result = []

    def get_photo_info(self) -> list:
        """
        Извлекает информацию о фотографиях из JSON-ответа и сохраняет её в атрибуте result.
        Проверяет наличие фотографий в ответе; если фотографий нет, выбрасывает исключение ValueError.
        Возвращает список с информацией о каждой фотографии:
        - название (количество лайков);
        - размер файла;
        - URL.
        :return: список словарей с информацией о каждой фотографии.
        """
        if self.json_from_vk["response"]["count"] == 0:
            raise ValueError("Ошибка. Фото отсутвует.")
        for photo in self.json_from_vk["response"]["items"]:
            info = {
                "file_name": photo["likes"]["count"],
                "size": photo["sizes"][-1]["type"],
                "url": photo["sizes"][-1]["url"]
            }
            self.result.append(info)
        return self.result


class YD:
    """
    Этот класс отвечает за взаимодействие с API Яндекс.Диска для управления папками и загрузки фотографий.
    """
    def __init__(self, token: str, folder_name: str = "VK photo") -> None:
        """
        Инициализирует экземпляр класса YD с заданными параметрами токена и имени папки.
        Устанавливает заголовки для запросов и базовый URL для работы с API Яндекс.Диска.
        :param token: токен авторизации для доступа к API Яндекс.Диска.
        :param folder_name: имя папки (по умолчанию “VK photo”).
        """
        self.headers = {
            'Authorization': token
        }
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.folder_name = folder_name

    def add_folder(self) -> None:
        """
        Яндекс.Диске с использованием указанного пути.
        Использует метод requests.put для выполнения HTTP-запроса.
        Вызывает метод response_validate для проверки статуса ответа.
        """
        params = {
            "path": self.folder_name
        }
        response = requests.put(self.base_url, params=params, headers=self.headers)
        self.response_validate(response, "folder")

    def add_photo(self, json_photo_info: list) -> None:
        """
        Загружает фотографии на Яндекс.Диск, используя информацию, полученную из JSON-ответа.
        Использует tqdm для отображения прогресса загрузки.
        Перебирает каждую фотографию в списке и отправляет POST-запрос с помощью requests.post.
        Вызывает метод response_validate для проверки статуса ответа.
        :param json_photo_info: список с информацией о фотографиях, полученный из API ВКонтакте.
        """
        with tqdm(total=len(json_photo_info), desc="Загрузка фото на Яндекс.Диск") as pbar:
            for photo in json_photo_info:
                params = {
                    "path": f"{self.folder_name}/{photo['file_name']}",
                    "url": photo["url"]
                }
                response = requests.post(self.base_url + "/upload", params=params, headers=self.headers)
                self.response_validate(response, "photo")
                pbar.update()

    def response_validate(self, response, type: str) -> None:
        """
        Проверяет статус ответа от API Яндекс.Диска.
        В зависимости от статуса и типа операции (папка или фото),
        выбрасывает исключение ValueError с описанием ошибки.
        :param response: объект ответа от API
        :param type: строка, указывающая тип операции (“folder” или “photo”).
        """
        status = response.status_code
        response_json = json.loads(response.text)
        if status not in range(200, 300):
            if type == "folder" and status != 409:
                raise ValueError(f"Не удалось создать папку! Код ошибки: {status}. {response_json["message"]}")
            if type == "photo":
                raise ValueError(f"Не удалось загрузить фото! Код ошибки: {status}. {response_json["message"]}")


class Interface:
    """
    Класс отвечает за интерфейс взаимодействия с пользователем и исполнение программы.
    """
    def __init__(self, vk_token: str) -> None:
        """
        Инициализирует экземпляр класса Interface с заданным токеном доступа к API ВКонтакте.
        Сохраняет токен в приватном атрибуте __vk_token.
        :param vk_token: токен доступа к API ВКонтакте.
        """
        self.__vk_token = vk_token

    def run(self) -> None:
        """
        Этот класс координирует весь процесс загрузки фотографий с ВКонтакте на Яндекс.Диск,
        обеспечивая взаимодействие с пользователем для ввода необходимых данных и обработку возможных ошибок.
        1. Получает ID пользователя ВКонтакте.
        2. Получает токен Яндекс.Диска.
        3. Получает ID альбома.
        4. Получает количество фотографий для загрузки.
        5. Создает экземпляры классов VK и Photo, загружает фотографии.
        6. Использует экземпляр класса YD для добавления папки и загрузки фотографий на Яндекс.Диск.
        7. Отображает результаты и сообщения об ошибках.
        """
        user_id = self.set_user_id()
        yd_token = self.set_yd_token()
        album_id = self.set_album_id()
        count = self.set_count()

        try:
            vk = VK(self.__vk_token)
            photo = Photo(vk.get_photo(user_id, count, album_id))

            yd = YD(yd_token, user_id)
            yd.add_folder()
            yd.add_photo(photo.get_photo_info())

            print("\nЗагрузка завершена успешно.")
            print("На ваш яндекс диск добавлены файлы:")
            print(self.get_result(photo))

        except ValueError as message:
            print("\n\t*** ERROR ***")
            print(message)

    def get_result(self, photo: Photo) -> str:
        """
        Форматирует и объединяет имена файлов загруженных фотографий, возвращая их в виде строки, разделенной запятыми.
        :param photo: экземпляр класса Photo, содержащий информацию о фотографиях.
        :return: строка с именами файлов.
        """
        return ", ".join([str(d["file_name"]) for d in photo.result])

    def set_info(self, type: str, info: str, exception: str) -> str:
        """
        Вводит данные с клавиатуры до тех пор, пока не будет введен корректный ввод.
        Используется для получения обязательных данных: ID пользователя ВКонтакте, токена Яндекс.Диска.
        На каждый запрос данных даётся 5 попыток. Если их исчерпать программа завершится.
        :param type: тип ввода (“vk” или “yd”)
        :param info: информационное сообщение.
        :param exception: сообщение об ошибке.
        :return: введенные данные или None, если попытки исчерпаны.
        """
        count = 4
        while True:
            inp = input(f"{info}: ")
            if type == "vk" and inp.isdigit():
                return inp
            if type == "yd" and inp != "":
                return inp
            else:
                if count == 0:
                    print("Вы исчерпали попытки ввода")
                    break
                print(f"{exception}, осталось попыток: {count}")
                count -= 1

    def set_user_id(self) -> str:
        """
        Получает ID пользователя ВКонтакте с помощью метода set_info.
        :return: ID пользователя или None при неудаче
        """
        info = "Введите id пользователя VK"
        exception = "Некорректный id пользователя"
        return self.set_info("vk", info, exception)

    def set_yd_token(self) -> str:
        """
        Получает токен Яндекс.Диска с помощью метода set_info.
        :return: токен Яндекс.Диска или None при неудаче.
        """
        info = "Введите токен Яндекс.Диска"
        exception = "Некорректный токен"
        return self.set_info("yd", info, exception)

    def set_album_id(self) -> str:
        """
        Получает ID альбома для загрузки фотографий, предлагая пользователю выбрать альбом (стена, профиль, сохраненные фотографии)
        или по умолчанию использовать фото в профиле.
        :return: ID альбома или “profile” при неудаче.
        """
        print("\nВыберите альбом: \n1 - фото со стены\n2 - фото в профиле\n3 - сохраненные фотографии")
        print("Шаг можно пропустить, по умолчанию фото в профиле.")
        inp = input("Введите номер: ")
        if inp == "":
            return "profile"
        if inp.isdigit() and 1 <= int(inp) <= 3:
            number = int(inp) - 1
        else:
            print("Некорректный ввод, выбрано значение по умолчанию.")
            return "profile"
        return ["wall", "profile", "saved"][number]

    def set_count(self) -> int:
        """
        Получает количество фотографий для загрузки, предлагая пользователю ввести число или используя значение по умолчанию 5.
        :return: количество фотографий или 5 при неудаче.
        """
        print("\nВыбор количества фотографий для загрузки. Шаг можно пропустить, по умолчанию 5.")
        inp = input("Укажите количество: ")
        if inp == "":
            return 5
        if inp.isdigit():
            return int(inp)
        else:
            print("Некорректный ввод, выбрано значение по умолчанию.")
            return 5

# Запуск с помощью интерфейса
inter = Interface(vk_token)
inter.run()



