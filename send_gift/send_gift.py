import time
import random
from send_gift.models import get_key

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from seleniumwire import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from background_task import background


def steam_login(driver, login: str, password: str):
    driver.get('https://steamcommunity.com/login/home/?goto=login%2F')
    time.sleep(2)
    login_input = driver.find_element(
        By.XPATH,
        '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[1]/input'
    )
    for i in login:
        login_input.send_keys(i)
        time.sleep(random.uniform(0, 0.1))
    password_input = driver.find_element(
        By.XPATH,
        '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[2]/input'
    )
    for i in password:
        password_input.send_keys(i)
        time.sleep(random.uniform(0, 0.1))

    driver.find_element(
        By.XPATH,
        '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[4]/button'
    ).click()
    time.sleep(2)
    return True


def add_friend(driver, link: str):
    driver.get(link)
    time.sleep(5)
    driver.find_element(By.XPATH, '//*[@id="btn_add_friend"]/span').click()
    time.sleep(1)
    result = str(driver.page_source)
    print('Добавлен в друзья')
    # На случай сбоя в стиме. Нужно добавить юзера в черный список и обратно, чтобы попробовать ещё раз
    if 'отправлен' not in result.lower() and 'sent' not in result.lower():
        print("Попытка номер 2")
        driver.get(link)
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="profile_action_dropdown_link"]/span').click()
        time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="profile_action_dropdown"]/div[9]/a[1]').click()
        time.sleep(0.5)
        driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/div[2]/div[1]/span').click()
        time.sleep(0.2)
        driver.get(link)
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="profile_action_dropdown_link"]/span').click()
        time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="profile_action_dropdown"]/div[9]/a[2]').click()
        time.sleep(0.2)
        driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/div[2]/div[1]/span').click()
        driver.get(link)
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="btn_add_friend"]/span').click()
        time.sleep(0.5)
        result = str(driver.page_source)
        if 'отправлен' in result.lower() or 'sent' in result.lower():
            print('Успех')


def remove_friend(driver, link: str):
    driver.get(link)
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="profile_action_dropdown_link"]/span').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="profile_action_dropdown"]/div[9]/a[6]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/div[2]/div[1]/span').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[4]/div[3]/div/div[2]/div/span').click()


def gift_game(driver, game_link, sub_id, friend_name):
    driver.get(game_link)
    time.sleep(3)
    try:
        select_element = driver.find_element(By.XPATH, '//*[@id="ageYear"]')
        time.sleep(0.5)
        Select(select_element).select_by_value('2002')
        driver.find_element(By.XPATH, '//*[@id="app_agegate"]/div[1]/div[3]/a[1]/span').click()
        time.sleep(1)
    except NoSuchElementException:
        pass
    # Добавить в корзину

    driver.find_element(By.XPATH, f"//*[contains(@href,'{sub_id});')]").click()

    time.sleep(1)
    # Купить в подарок
    driver.find_element(By.XPATH, '//*[@id="btn_purchase_gift"]/span').click()
    time.sleep(1)
    # Выбрать друга
    friends_table = driver.find_element(By.XPATH, '//*[@id="friends_chooser"]')
    friends = friends_table.find_elements(By.TAG_NAME, 'div')
    for friend in friends:
        if friend.text == friend_name:
            friend.click()
    time.sleep(1)
    # Продолжить
    driver.find_element(By.XPATH, '//*[@id="gift_recipient_tab"]/div[3]/div/a/span').click()
    time.sleep(1)
    # Заполняем письмо
    driver.find_element(By.XPATH, '//*[@id="gift_recipient_name"]').send_keys('Your game')
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="gift_message_text"]').send_keys('....')
    time.sleep(0.3)
    driver.find_element(By.XPATH, '//*[@id="gift_signature"]').send_keys('BBB')
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="submit_gift_note_btn"]/span').click()
    time.sleep(3)
    # Покупка
    try:
        driver.find_element(By.XPATH, '//*[@id="accept_ssa"]').click()
        driver.find_element(By.XPATH, '//*[@id="purchase_button_bottom_text"]').click()
        time.sleep(1)
    except ElementNotInteractableException:
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="accept_ssa"]').click()
        driver.find_element(By.XPATH, '//*[@id="purchase_button_bottom_text"]').click()
        time.sleep(1)


def check_gift_status(login: str, password: str, shared_secret: str, proxy: str, nickname: str, game_name: str):
    print('!!!!!!!!!!!!!!!!!!!!')
    print('Прокси тут')
    print(proxy)
    # options = {
    #     'proxy': {
    #         'http': f'http://{proxy}',
    #         'https': f'https://{proxy}',
    #         'no_proxy': 'localhost,127.0.0.1'  # excludes
    #     }
    # }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    try:
        steam_login(driver, login, password, shared_secret)
        time.sleep(3)

        steam_id = driver.current_url.split('id/')[1]
        driver.get(f'https://steamcommunity.com/id/{steam_id}/inventory/')
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="inventory_more_link"]').click()
        time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="inventory_more_dropdown"]/div/a[3]').click()
        gifts = driver.find_element(By.XPATH, '//*[@id="tabcontent_pendinggifts"]').find_element(By.TAG_NAME, 'div')
        for i in gifts:
            try:
                status_area = i.find_element(By.CLASS_NAME, 'gift_status_area')
            except NoSuchElementException:
                continue
            print(status_area.text)
            if nickname in status_area.find_element(By.TAG_NAME, 'a').text and game_name in i.text:
                if 'Redeemed' in i.text:
                    driver.quit()
                    return 'Received'
                elif 'Sent' in i.text:
                    driver.quit()
                    return 'Submitted'
    except Exception as e:
        print(e)
        driver.quit()
        return 'Error'
    driver.quit()
    return 'Rejected'


@background()
def main_gift_send(login, password, target_name, game_link, sub_id, proxy, target_link, code):
    code_obj = get_key(code)
    print('!!!!!!!!!!!!!!!!!!!!')
    print('Прокси тут')
    print(proxy)
    # options = {
    #     'proxy': {
    #         'http': f'http://{proxy}',
    #         'https': f'https://{proxy}',
    #         'no_proxy': 'localhost,127.0.0.1'  # excludes
    #     }
    # }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)
    try:
        steam_login(driver, login, password)
        time.sleep(3)
        gift_game(driver, game_link, sub_id, target_name)
        code_obj.status = "Готово!"
        code_obj.save()
        try:
            remove_friend(driver, target_link)
        except Exception as e:
            print(e)
            driver.quit()
            return 'Error Remove'
    except Exception as e:
        print(e)
        driver.quit()
        code_obj.status = "Ошибка, обратитесь к продавцу!"
        code_obj.save()
        return 'Error'
    driver.quit()


@background()
def main_friend_add(login: str, password: str,  proxy: str, target_link: str, code):
    print('start')
    code_obj = get_key(code)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # chrome_options.add_argument('--proxy-server=%s' % proxy)
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)

    try:
        steam_login(driver, login, password)
        time.sleep(3)
        add_friend(driver, target_link)
        code_obj.status = "Ожидаем принятия запроса"
        code_obj.save()
    except Exception as e:
        print(e)
        driver.quit()
        code_obj.status = "Ссылка некорректна ожидаем замены"
        code_obj.save()
        return 'Error'

    driver.quit()


# check_gift_status('raibartinar1970', 'LHtsrneGns1976', '6772uh:WHd7M4@5.101.83.130:8000', 'enormously', 'SUPERHOT VR')
# main_friend_add('ningendo771', 'vfczyz5391321212123456789S', '', 'https://steamcommunity.com/id/4560456/')
# main('ningendo771', 'vfczyz5391321212123456789S', '_TiTaN_BaLLs_', 'https://store.steampowered.com/app/1110910/Mortal_Shell/', '614771',
 #    '', 'https://steamcommunity.com/id/4560456/')
