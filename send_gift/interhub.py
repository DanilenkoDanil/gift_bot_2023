import hashlib
import hmac
import time
import requests
import json

import requests
import time


def send_steam(login: str, amount: float, authorization: str) -> dict:
    s = requests.Session()
    s.headers['Accept'] = 'application/json'
    s.headers['Content-Type'] = 'application/json'
    s.headers['authorization'] = 'Bearer ' + authorization
    postjson = {
        'id': "",
        "sum": {
            "amount": "",
            "currency": "398"
        },
        "paymentMethod": {
            "type": "Account",
            "accountId": "398"
        },
        "fields": {
            "account": ""
        }
    }
    postjson['id'] = str(int(time.time() * 1000))
    postjson['sum']['amount'] = str(amount)
    postjson['fields']['account'] = login
    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/31212/payments', json=postjson)
    return res.json()


def check(account: str, amount: float, authorization: str):
    url = "https://api.interhub.uz/api/payment/check"
    timer = time.time()
    payload = {
        "amount": amount,
        "service_id": 92,
        "agent_transaction_id": str(timer + 6668846442),
        "account": account,
        "params": {}
    }
    headers = {
        'token': authorization
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.content)
    print(response.json())

    return response.json()['transaction_id']


def pay(transaction: str, authorization: str):
    url = "https://api.interhub.uz/api/payment/pay"

    payload = {
        "transaction_id": transaction,
        "currencyId": 0,
        "checkTransactionId": transaction
    }
    headers = {
        'token': authorization
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.json())
    return response.json()


def send_steam_ozon(login: str, amount: float, authorization: str) -> bool:
    transaction_id = check(login, amount, authorization)
    pay(transaction_id, authorization)
    return True


def pay_lava(shop_id: str, secret_key: str, wallet_to: str, amount: float):
    key = secret_key
    url = "https://api.lava.ru/business/payoff/create"

    payload = {
        "shopId": shop_id,
        "orderId": 'pay12' + str(time.time()),
        "amount": amount,
        "service": "steam_payoff",
        "subtract": 1,
        "walletTo": f" {wallet_to}"
    }

    json_str = json.dumps(payload).encode()

    sign = hmac.new(bytes(key, 'UTF-8'), json_str, hashlib.sha256).hexdigest()
    print(payload)
    print(sign)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Signature': sign
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.json())
    return response.json()


def get_balance(authorization: str) -> float:
    url = "https://api.interhub.uz/api/agent/deposit"

    payload = {}
    headers = {
        'token': authorization
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return float(response.json()['balance'])


def get_currency():
    API_KEY = '5ea315a93c1fa9a54630a7e01b9f307a'
    response = requests.get(f'http://api.exchangeratesapi.io/v1/latest?access_key={API_KEY}').json()
    uzs = float(response['rates']['UZS'])
    rub = float(response['rates']['RUB'])
    return uzs/rub


# print(get_currency())

# print(get_balance('Bjram6kcMx6jVcRyEtnnEwxxxpb9kqQzJVzcCQmRjh2G8w6WGE'))
# send_steam('sh33shka', 560, '5a6d1dac7d9455bed78462ab4858c8c1')
# send_steam_ozon('sh33shka', 560, '5a6d1dac7d9455bed78462ab4858c8c1')
# send_steam('sh33shka', 560, '5a6d1dac7d9455bed78462ab4858c8c1')
# print(get_balance('yZGqhXRaHeeBH9D1BmV74gm2M2eQoIZt5vjOnUmptIX1NdXJC4'))
# for i in range(1, 3):
# send_steam_ozon('danilenko231', 100000, 'okhwhalpvuf10Y8EEMA-JhBPn1?ckHvZX9vatbpUrGlrB1')
