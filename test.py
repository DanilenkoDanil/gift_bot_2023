import requests
from bs4 import BeautifulSoup


def get_steam_profile_name(profile_url):
    try:
        # Отправляем GET-запрос на страницу профиля Steam
        response = requests.get(profile_url)

        # Проверяем успешность запроса
        if response.status_code == 200:
            # Создаем объект BeautifulSoup для парсинга HTML-страницы
            soup = BeautifulSoup(response.text, 'html.parser')

            # Находим элемент с ником профиля Steam
            profile_name = soup.find('span', {'class': 'actual_persona_name'})

            if profile_name:
                return profile_name.text.strip()  # Возвращаем ник

    except Exception as e:
        print(f"Ошибка: {e}")

    return None


print(get_steam_profile_name('https://steamcommunity.com/id/4560456/'))
