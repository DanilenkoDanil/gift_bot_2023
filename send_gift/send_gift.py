from send_gift.models import get_key
from background_task import background
from send_gift.models import Log

from steam.steamid import from_url
from steam.steamid import SteamID
from steam.client import SteamClient
import requests


def send_gift(username, password, sub_id, friend_profile_url):
    try:
        client = SteamClient()
        client.login(username=username, password=password)
        session = client.get_web_session()
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        my_account_id = SteamID(client.session_id).account_id

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
        session.post('https://store.steampowered.com/cart/', data=payload)
        session.get(f"https://store.steampowered.com/dynamicstore/userdata/?id={my_account_id}&cc=RU&v=20")
        cookies = requests.utils.dict_from_cookiejar(session.cookies)
        shopping_cart_id = cookies['shoppingCartGID']

        session.get(
            f'https://checkout.steampowered.com/checkout/?purchasetype=gift&cart={shopping_cart_id}&snr=1_8_4__503')

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

        result = session.post('https://checkout.steampowered.com/checkout/inittransaction/', data=payload)
        trans_id = result.json()['transid']

        session.get(
            f'https://checkout.steampowered.com/checkout/getfinalprice/?count=1&transid={trans_id}&purchasetype=gift&microtxnid=-1&cart={shopping_cart_id}&gidReplayOfTransID=-1')
        payload = {
            "transid": trans_id,
            "CardCVV2": ""
        }
        result = session.post('https://checkout.steampowered.com/checkout/finalizetransaction/', data=payload).json()
        print(result)
        if int(result['success']) == 22:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        Log.objects.create(message=e)
        return False


@background()
def main_gift_send(login, password, sub_id, target_link, code):
    code_obj = get_key(code)

    result = send_gift(login, password, sub_id, target_link)
    if result is True:
        code_obj.status = "Готово!"
        code_obj.save()
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
