from logging import exception

import requests
import json
import time
from seleniumwire import webdriver
from PIL import Image
import io
import os
import re
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import asyncio

load_dotenv()


class user_of_course:
    name = ""
    url = []

    def __init__(self, name):
        self.name = name
        self.url = []


async def send_notification(user_name, course_id, url):
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.send(
        f'{user_name}。目前開課序號 {course_id} 有空位!!!\n 請盡快登入選課系統加選。\n 系統僅提醒乙次，如需再次提醒請重新加選。')
    file_path = os.path.dirname(__file__) + '/course_list.json'
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        determined: bool = False
        for course in data:
            if course['name'] == user_name:
                for course_url in course['url']:
                    if course_url == url:
                        course['url'].remove(course_url)
        with open(file_path, 'w', encoding='utf-8') as ff:
            json.dump(data, ff, ensure_ascii=False, indent=4)



async def make_api_request(jsid: str, driver: webdriver.Chrome):
    # define users is the list of User_Of_Course
    users = []
    with open('course_list.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for course in data:
            user = user_of_course(course['name'])
            for course_url in course['url']:
                user.url.append(course_url)
            users.append(user)
            print(user.name, user.url)
    headers = {
        'Cookie': 'JSESSIONID=' + jsid}  # Replace <your_jsessionid_value> with the actual JSESSIONID value
    for user in users:
        # print user name yellow color099
        print("\033[1;33;40m")
        print("--------------------------------------------")
        print("Starting change course id to request api endpoint: user -> ", user.name)
        print("\033[0;37;40m")
        # 這裡可以加上 選課代碼換成 url 的功能
        for url in user.url:
            # 先判斷 user.url 是否為純數字，若是代表還未轉換成 url (亦為 user 新增的課程代碼)
            print("user url:", url)
            print("user url type:", type(url))
            # is url us not string
            if not isinstance(url, str):
                print("課程代碼數字為:", course_id)
                time.sleep(1)
                # 清空課程代碼欄位
                try:
                    driver.find_element('id', 'serialNo-inputEl').clear()
                except Exception as e:
                    print("找不到 serialNo-inputEl")
                    print(e)

                # 輸入課程代碼
                time.sleep(0.2)
                driver.find_element('id', 'serialNo-inputEl').send_keys(course_id)
                time.sleep(0.2)
                # 查詢 按鈕
                driver.find_element('id', 'button-1060').click()
                time.sleep(0.2)
                # 點選 checkbox
                # regex: gridview-(\d+)-record-ext-record-(\d+)
                result = re.search(r'gridview-(\d+)-record-ext-record-(\d+)', driver.page_source)
                driver.find_element('id', str(result.group())).click()
                time.sleep(0.2)
                # 清理 driver request 紀錄
                driver.requests.clear()
                # 課程資訊 按鈕
                driver.find_element('id', 'button-1087').click()
                time.sleep(0.2)
                # 透過截封包的方式取得 url
                url = ""
                for request in driver.requests:
                    if request.response:
                        if 'CourseQueryCtrl' in request.url:
                            url = request.url
                            break
                print("我找到了 course_id:", course_id)
                print("將他改成 url:", url)
                # open id_2_course_name.json 標記 course_id -> url
                with open('id_2_course_name.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    is_found = False
                    for course in data:
                        if course['course_id'] == course_id:
                            is_found = True
                            break
                    if not is_found:
                        print("找不到 course_id", course_id, ", 因此新增")
                        data.append({'course_id': course_id, 'url': url})
                user.url.remove(course_id)
                user.url.append(url)
                print("user url 更改完成 -> ", user.url)
                # 點選 X 按鈕
                driver.find_element('id', 'tool-1132').click()
    for user in users:
        # print user name yellow color099
        print("\033[1;33;40m")
        print("--------------------------------------------")
        print("Requesting API for", user.name)
        print("\033[0;37;40m")
        # 這裡可以加上 選課代碼換成 url 的功能
        for url in user.url:
            # 以下是確定該 user 的 課程代碼 已經轉換成 url 了，可以開始發送 API request
            response = requests.get(url, headers=headers)
            data = ""
            if response.status_code == 200:
                print("API request successful.")
                data = response.text
                # print(data)
                id_of_course = re.search(r"'開課序號',\s*value:\s*'(.+)'", data)
                limit_value = re.search(r"'限修人數',\s*value:\s*'(\d+)'", data)
                print("開課序號:", id_of_course.group(1))
                if limit_value:
                    print("限修人數:", limit_value.group(1))
                else:
                    print("未找到限修人數的值")
                distributed_value = re.search(r"'已分發人數',\s*value:\s*'(\d+)'", data)
                if distributed_value:
                    print("已分發人數:", distributed_value.group(1))
                else:
                    print("未找到已分發人數的值")
                if limit_value and distributed_value:
                    if int(distributed_value.group(1)) < int(limit_value.group(1)):
                        # print light green color
                        print("\033[1;32;40m")
                        print(id_of_course.group(1), " 有名額 !!!!!!!!!!!!!")
                        await send_notification(user.name, id_of_course.group(1), url)
                        print("\033[0;37;40m")
                    else:
                        print("沒名額")
                print("---------------")
            else:
                print("API request failed.")
                print("Status code:", response.status_code)
                print("Response:", response.text)
            await asyncio.sleep(0.5)


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def scrape_website():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options, seleniumwire_options={'verify_ssl': False})
    driver.get('https://cos3s.ntnu.edu.tw/AasEnrollStudent/LoginCheckCtrl?language=TW')
    # find RandImg in request url
    time.sleep(2)
    # driver.wait_for_request('RandImage', timeout=5)

    for request in driver.requests:
        if request.response:
            if 'RandImage' in request.url:
                img = Image.open(io.BytesIO(request.response.body))
                img.save('tmp.png')
                break
    time.sleep(0.2)
    os.system('viu tmp.png')
    validation_code = input("Please input the validation code: ")
    driver.find_element('id', 'userid-inputEl').send_keys(os.getenv('STUDENT_ID'))
    time.sleep(1)
    driver.find_element('id', 'textfield-1017-inputEl').send_keys(os.getenv('PASSWORD'))
    time.sleep(1)
    driver.find_element('id', 'textfield-1019-inputEl').send_keys(validation_code)
    time.sleep(1)
    result = re.search(r'ggghjug67fuhu\d+-btnEl', driver.page_source)
    driver.find_element('id', str(result.group())).click()
    time.sleep(0.8)
    # 課程開始加選時會有一個彈出視窗，點擊確認 ; 非加選時不會有此視窗
    # driver.find_element('id', 'button-1005-btnEl').click()
    # time.sleep(1)
    driver.find_element('id', 'button-1020-btnEl').click()
    time.sleep(1)
    # driver.execute_script("countSecond=-1;")
    session = driver.get_cookie('JSESSIONID')['value']
    # 查詢課程 按鈕
    time.sleep(0.5)
    # 師大的課程資訊查訊是在 iframe 內，所以要先切換到 iframe 內
    iframe_content = driver.find_element('id', 'stfseldListDo')
    driver.switch_to.frame(iframe_content)
    # 課程查詢 按鈕
    driver.find_element('id', 'query').click()
    time.sleep(1.7)
    while True:
        users = []
        with open('course_list.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for course in data:
                user = user_of_course(course['name'])
                for course_url in course['url']:
                    user.url.append(course_url)
                users.append(user)
                print(user.name, user.url)
        headers = {
            'Cookie': 'JSESSIONID=' + session}  # Replace <your_jsessionid_value> with the actual JSESSIONID value
        for user in users:
            # print user name yellow color099
            print("\033[1;33;40m")
            print("--------------------------------------------")
            print("Starting change course id to request api endpoint: user -> ", user.name)
            print("\033[0;37;40m")
            # 這裡可以加上 選課代碼換成 url 的功能
            for url in user.url:
                # 先判斷 user.url 是否為純數字，若是代表還未轉換成 url (亦為 user 新增的課程代碼)
                print("user url:", url)
                print("user url type:", type(url))
                # is url us not string
                if not isinstance(url, str):
                    course_id = url
                    print("課程代碼數字為:", course_id)
                    time.sleep(1)
                    # 清空課程代碼欄位
                    driver.find_element('id', 'serialNo-inputEl').clear()

                    # 輸入課程代碼
                    time.sleep(1)
                    driver.find_element('id', 'serialNo-inputEl').send_keys(course_id)
                    time.sleep(1)
                    # 查詢 按鈕
                    driver.find_element('id', 'button-1060').click()
                    time.sleep(0.2)
                    # 點選 checkbox
                    # regex: gridview-(\d+)-record-ext-record-(\d+)
                    result = re.search(r'gridview-(\d+)-record-ext-record-(\d+)', driver.page_source)
                    driver.find_element('id', str(result.group())).click()
                    time.sleep(0.2)
                    # 清理 driver request 紀錄
                    driver.requests.clear()
                    time.sleep(0.2)
                    # 課程資訊 按鈕
                    driver.find_element('id', 'button-1087').click()
                    time.sleep(0.2)
                    # 透過截封包的方式取得 url

                    # 從最近的 request 中找到 CourseQueryCtrl?year= 的 url，而非直接從頭開始找
                    # 從 driver.requests 反向找尋最近的 request
                    for i in range(len(driver.requests) - 1, -1, -1):
                        if 'CourseQueryCtrl?year=' in driver.requests[i].url:
                            url = driver.requests[i].url
                            break

                    print("我找到了 course_id:", course_id)
                    print("將他改成 url:", url)
                    # find the course id idx
                    idx = -1
                    for i in range(len(user.url)):
                        if user.url[i] == course_id:
                            idx = i
                            break
                    user.url[idx] = url
                    # 點選 X 按鈕
                    result = re.search(r'tool-\d+', driver.page_source)
                    driver.find_element('id', str(result.group())).click()
                    # driver.find_element('id', 'tool-1132').click()
                else:
                    print("user url is already a url")
        # 把上述 user 更動寫入 course_list.json
        with open('course_list.json', 'w', encoding='utf-8') as f:
            data = []
            for user in users:
                user_dict = {'name': user.name, 'url': user.url}
                data.append(user_dict)
            json.dump(data, f, ensure_ascii=False, indent=4)

        for user in users:
            # print user name yellow color099
            print("\033[1;33;40m")
            print("--------------------------------------------")
            print("Requesting API for", user.name)
            print("\033[0;37;40m")
            # 這裡可以加上 選課代碼換成 url 的功能
            for url in user.url:
                # 以下是確定該 user 的 課程代碼 已經轉換成 url 了，可以開始發送 API request
                response = requests.get(url, headers=headers)
                data = ""
                if response.status_code == 200:
                    print("API request successful.")
                    data = response.text
                    # print(data)
                    id_of_course = re.search(r"'開課序號',\s*value:\s*'(.+)'", data)
                    limit_value = re.search(r"'限修人數',\s*value:\s*'(\d+)'", data)
                    print("開課序號:", id_of_course.group(1))
                    if limit_value:
                        print("限修人數:", limit_value.group(1))
                    else:
                        print("未找到限修人數的值")
                    distributed_value = re.search(r"'已分發人數',\s*value:\s*'(\d+)'", data)
                    if distributed_value:
                        print("已分發人數:", distributed_value.group(1))
                    else:
                        print("未找到已分發人數的值")
                    if limit_value and distributed_value:
                        if int(distributed_value.group(1)) < int(limit_value.group(1)):
                            # print light green color
                            print("\033[1;32;40m")
                            print(id_of_course.group(1), " 有名額 !!!!!!!!!!!!!")
                            await send_notification(user.name, id_of_course.group(1), url)
                            print("\033[0;37;40m")
                        else:
                            print("沒名額")
                    print("---------------")
                else:
                    print("API request failed.")
                    print("Status code:", response.status_code)
                    print("Response:", response.text)
                await asyncio.sleep(0.5)
        await say_after(60, "剩下 2 分鐘重新發送請求")
        await say_after(60, "剩下 1 分鐘重新發送請求")


CHANNEL_ID = os.getenv('CHANNEL_ID')
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.send(
        'NTNU-Course-Info-Bot is online!\n Use `!info` to get guidance. \n Use `!help` to get command list.')


@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension} done!')


@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded {extension} done!')


@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'Reloaded {extension} done!')


@bot.command()
async def start_scrapping(ctx):
    await ctx.send("Starting scraping...")
    await scrape_website()
    await ctx.send("Scraping finished.")


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def start():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(start())
    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')
    # options.add_argument('--headless')
    # driver = webdriver.Chrome(options=options, seleniumwire_options={'verify_ssl': False})
    # driver.get('https://cos3s.ntnu.edu.tw/AasEnrollStudent/LoginCheckCtrl?language=TW')
    # # find RandImg in request url
    # time.sleep(2)
    # # driver.wait_for_request('RandImage', timeout=5)
    #
    # for request in driver.requests:
    #     if request.response:
    #         if 'RandImage' in request.url:
    #             img = Image.open(io.BytesIO(request.response.body))
    #             img.save('tmp.png')
    #             break
    # time.sleep(0.2)
    # os.system('viu tmp.png')
    # validation_code = input("Please input the validation code: ")
    # driver.find_element('id', 'userid-inputEl').send_keys(os.getenv('STUDENT_ID'))
    # time.sleep(1)
    # driver.find_element('id', 'textfield-1017-inputEl').send_keys(os.getenv('PASSWORD'))
    # time.sleep(1)
    # driver.find_element('id', 'textfield-1019-inputEl').send_keys(validation_code)
    # time.sleep(1)
    # result = re.search(r'ggghjug67fuhu\d+-btnEl', driver.page_source)
    # driver.find_element('id', str(result.group())).click()
    # time.sleep(3)
    # driver.find_element('id', 'button-1020-btnEl').click()
    # time.sleep(3)
    # driver.execute_script("countSecond=-1;")
    # session = driver.get_cookie('JSESSIONID')['value']
    #
    # while True:
    #     make_api_request(session)
    #     time_count()
    #
    # driver.quit()
