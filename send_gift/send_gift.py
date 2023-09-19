from send_gift.models import get_key
from background_task import background
from send_gift.models import Log

from steam.steamid import from_url
from steam.steamid import SteamID
from steam.client import SteamClient
import requests
import time


def copy_cookies(session):
    source_domain = 'store.steampowered.com'
    source_cookies = session.cookies.get_dict(domain=source_domain)

    target_domain = 'checkout.steampowered.com'
    for name, value in source_cookies.items():
        secure = (name == 'steamLoginSecure')
        session.cookies.set(name, value, domain=target_domain, secure=secure)

    return session


def send_gift(username, password, sub_id, friend_profile_url):
    status = 0
    try:
        client = SteamClient()
        client.login(username=username, password=password)
        session = client.get_web_session()
        session = copy_cookies(session)
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        time.sleep(3)

        cookies = requests.utils.dict_from_cookiejar(session.cookies)
        session_id = cookies['sessionid']
        friend_id = SteamID(from_url(friend_profile_url))
        payload = {
            "snr": "1_5_9__403",
            "originating_snr": "1_store - navigation__",
            "action": "add_to_cart",
            "sessionid": session_id,
            "subid": sub_id
        }
        cart = session.post('https://store.steampowered.com/cart/', data=payload)
        status = 1
        cookies = requests.utils.dict_from_cookiejar(session.cookies)
        shopping_cart_id = cookies['shoppingCartGID']

        session_id = session.cookies.get('sessionid', domain='store.steampowered.com')
        session.cookies.set("beginCheckoutCart", shopping_cart_id, domain="checkout.steampowered.com",
                            path='/checkout/')
        session.cookies.set("gidShoppingCart", shopping_cart_id, domain="checkout.steampowered.com", path='/checkout/')
        payload = {
            "gidShoppingCart": shopping_cart_id,
            "gidReplayOfTransID": -1,
            "PaymentMethod": "steamaccount",
            "abortPendingTransactions": 0,
            "bHasCardInfo": 0,
            "Country": "RU",

            "ShippingCountry": "RU",
            "ScheduledSendOnDate": 0,
            "bSaveBillingAddress": 1,
            "bUseRemainingSteamAccount": 1,
            "bPreAuthOnly": 0,

            "bIsGift": 1,
            "GifteeEmail": "",
            "GifteeAccountID": friend_id.account_id,
            "GifteeName": "ss",
            "GiftMessage": "ss",
            "Sentiment": "Best Wishes",
            "Signature": "ss",

            "sessionid": session_id,
        }
        time.sleep(3)
        result = session.post('https://checkout.steampowered.com/checkout/inittransaction/', data=payload)
        trans_id = result.json()['transid']
        time.sleep(2)
        session.get(
            f'https://checkout.steampowered.com/checkout/getfinalprice/?count=1&transid={trans_id}&purchasetype=gift&microtxnid=-1&cart={shopping_cart_id}&gidReplayOfTransID=-1')
        payload = {
            "transid": trans_id,
            "CardCVV2": ""
        }
        time.sleep(3)
        result = session.post('https://checkout.steampowered.com/checkout/finalizetransaction/', data=payload).json()
        status = 2
        print(result)
        if int(result['success']) == 22:
            return True
        else:
            return False
    except Exception as e:
        cookies = requests.utils.dict_from_cookiejar(session.cookies)
        if status == 2:
            log_message = "Status 2" + str(cookies) + "\n" + str(e) + "\n" + result
        elif status == 1:
            log_message = "Status 1" + str(cookies) + "\n" + str(e) + "\n" + str(cart.content)
        else:
            log_message = "Status 0" + str(cookies) + "\n" + str(e)
        Log.objects.create(message=log_message)
        return False


@background()
def main_gift_send(login, password, sub_id, target_link, code):
    code_obj = get_key(code)

    result = send_gift(login, password, sub_id, target_link)
    if result is True:
        code_obj.status = "Готово!"
        code_obj.save()
    else:
        if code_obj.counter < 1:
            code_obj.counter += 1
            code_obj.status = "Процесс отправки..."
            code_obj.save()
            main_gift_send(login, password, sub_id, target_link, code, schedule=120)
        else:
            code_obj.status = "Ошибка, обратитесь к продавцу!"
            code_obj.save()
        return 'Error'


def add_steam_friend(username, password, friend_profile_url):
    client = SteamClient()
    client.login(username=username, password=password)
    session = client.get_web_session()
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    session_id = cookies['sessionid']
    friend_id = from_url(friend_profile_url)
    payload = {
        "sessionID": session_id,
        "steamid": friend_id,
        "accept_invite": 0
    }
    result = session.post('https://steamcommunity.com/actions/AddFriendAjax', data=payload).json()
    print(result)
    if result['success'] == 1:
        return True
    else:
        return False


@background()
def main_friend_add(login: str, password: str, target_link: str, code):
    code_obj = get_key(code)
    result = add_steam_friend(login, password, target_link)
    if result is True:
        code_obj.status = "Ожидаем принятия запроса"
        code_obj.save()
    else:
        code_obj.status = "Ссылка некорректна ожидаем замены"
        code_obj.save()
        return 'Error'
