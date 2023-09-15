from rest_framework import status, generics, permissions
from rest_framework.response import Response
from send_gift.models import Code, Interhub, get_setting, get_key, get_game, get_account
from send_gift.api import check_code
from django.http import JsonResponse
from datetime import date, timedelta
from rest_framework.views import APIView
from send_gift.interhub import send_steam_ozon
from django.shortcuts import render
from bs4 import BeautifulSoup
from send_gift.send_gift import main_friend_add, main_gift_send
import re
import requests


def get_steam_profile_name(profile_url):
    try:
        response = requests.get(profile_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            profile_name = soup.find('span', {'class': 'actual_persona_name'})

            if profile_name:
                return profile_name.text.strip()

    except Exception as e:
        print(f"Ошибка: {e}")

    return None


def convert_game_link_game_img(link: str):
    match = re.search(r'/app/(\d+)/', link)

    if match:
        steam_id = match.group(1)
        print(steam_id)
        return f"https://cdn.akamai.steamstatic.com/steam/apps/{steam_id}/header.jpg?t=1682652141"
    else:
        print('None')
        return None


def balance_up(username: str, amount: float):
    interhub = Interhub.objects.all().last()
    send_steam_ozon(username, amount, interhub.token)


class CheckFriendAPIView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        setting = get_setting()
        code = request.query_params.get('uniquecode')
        key = get_key(code)
        if key is False:
            return Response(f"Ваш код не действителен", status=status.HTTP_200_OK)

        if 'ожидаем' not in key.status.lower():
            return Response(f"Ваш код не действителен", status=status.HTTP_200_OK)

        key.status = "Отправляем подарок..."
        key.save()

        username = get_steam_profile_name(key.link)
        if username is None:
            key.status = "Ссылка некорректна ожидаем замены"
            key.save()
            return Response(f"Ссылка не подходит", status=status.HTTP_200_OK)

        # try:
        #     new_amount = key.game.amount * setting.course
        #     balance_up(key.account.login, new_amount)
        # except Exception as e:
        #     print(e)
        #     key.status = "Ошибка, обратитесь к продавцу!"
        #     key.save()
        #     return Response(f"Error", status=status.HTTP_200_OK)

        key.account.counter += 1
        key.account.save()
        main_gift_send(
            key.account.login,
            key.account.password,
            key.game.game_sub_id,
            key.link,
            key.code
        )
        return Response(f"Успех", status=status.HTTP_200_OK)


class ChangeLinkAPIView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        code = request.query_params.get('uniquecode')
        link = request.query_params.get('link')
        key = get_key(code)
        if key is False:
            return Response(f"Ваш код не действителен", status=status.HTTP_200_OK)
        if link is None:
            return Response(f"Ссылка не предоставлена", status=status.HTTP_200_OK)
        if key.counter < 1:
            key.status = "Ссылка заменена, ожидаем ответа на запрос в друзья..."
            key.link = link
            key.counter += 1
            key.save()
            main_friend_add(key.account.login, key.account.password, key.link, code)
            return Response(f"Успех", status=status.HTTP_200_OK)
        else:
            return Response(f"Недоступно", status=status.HTTP_200_OK)


class SendGiftAPIView(generics.RetrieveAPIView):
    @staticmethod
    def process_code(request, code):
        setting = get_setting()
        key = get_key(code)

        if key is False:
            try:
                info = check_code(code=code, guid=setting.digi_code, seller_id=setting.seller_id)
            except Exception as e:
                print(e)
                print('no info')
                return render(request, 'main/403_error.html')

            if info['retval'] == 0:
                game = get_game(info['value'])
                account = get_account(game.type)
                if account is False:
                    return render(request, 'main/403_error.html')

                code_obj = Code.objects.create(
                    code=code,
                    status="Отправляем запрос на добавление в друзья...",
                    game=game,
                    link=info['username'],
                    error='',
                    account=account
                )
                try:
                    main_friend_add(account.login, account.password, info['username'], code)
                    code_obj.status = "Отправляем запрос в друзья..."
                    code_obj.save()
                    image_link = convert_game_link_game_img(game.game_link)
                    context = {
                        'image_link': image_link,
                        'game_name': game.name,
                        'login': info['username'],
                        'code': code,
                        'status': code_obj.status
                    }
                    return render(request, 'main/account.html', context)
                except Exception as e:
                    print(e)
                    code_obj.error = 'User not found'
                    code_obj.save()
                    return render(request, 'main/403_error.html')
            else:
                return render(request, 'main/403_error.html')
        else:
            image_link = convert_game_link_game_img(key.game.game_link)
            context = {
                'image_link': image_link,
                'game_name': key.game.name,
                'login': key.link,
                'code': key.code,
                'status': key.status
            }
            return render(request, 'main/account.html', context)

    def retrieve(self, request, *args, **kwargs):
        code = request.query_params.get('uniquecode')
        return self.process_code(request, code)

    def post(self, request, *args, **kwargs):
        code = request.query_params.get('uniquecode')
        return self.process_code(request, code)
