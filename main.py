import requests
import json
import time
from seleniumwire import webdriver
from PIL import Image
import io
import os
import re
from dotenv import load_dotenv

load_dotenv()


class user_of_course:
    name = ""
    url = []

    def __init__(self, name):
        self.name = name
        self.url = []


def make_api_request(jsid: str):
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
        print("Requesting API for", user.name)
        print("\033[0;37;40m")
        for url in user.url:
            response = requests.get(url, headers=headers)
            data = ""
            if response.status_code == 200:
                print("API request successful.")
                data = response.text
                # print(data)
                import re
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
                        print("\033[0;37;40m")
                    else:
                        print("沒名額")
                print("---------------")
            else:
                print("API request failed.")
                print("Status code:", response.status_code)
                print("Response:", response.text)
            time.sleep(0.5)


def time_count():
    t = 5
    for i in range(0, 5):
        print("剩下", t, "分鐘重新發送請求")
        t -= 1
        time.sleep(60)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--headless')
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
    time.sleep(3)
    driver.find_element('id', 'button-1020-btnEl').click()
    time.sleep(3)
    driver.execute_script("countSecond=-1;")
    session = driver.get_cookie('JSESSIONID')['value']

    while True:
        make_api_request(session)
        time_count()

    driver.quit()
