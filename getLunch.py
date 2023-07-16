import json
import re
import datetime
from datetime import timedelta
import urllib.request

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless=new")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)


def neis_menu(date):
    atpt_code = "E10"
    school_code = 7310447
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={atpt_code}&SD_SCHUL_CODE={school_code}&MLSV_YMD={date}&KEY=02d3ebad34ee4f7a90282b2f495c3603&Type=json&pIndex=1&pSize=100"
    response = urllib.request.urlopen(url)
    response_body = response.read()
    data = json.loads(response_body.decode("utf-8"))

    pattern = r"\([\d]*\)"
    p = re.compile("\(([^)]+)")

    text = data["mealServiceDietInfo"][1]["row"][0]["DDISH_NM"]
    m1 = p.findall(text)
    text = text.replace(".", "")
    lunch_menu = (
        re.sub(pattern=pattern, repl="", string=text).replace(" ", "").split("<br/>")
    )
    text = data["mealServiceDietInfo"][1]["row"][1]["DDISH_NM"]
    m2 = p.findall(text)
    text = text.replace(".", "")
    dinner_menu = (
        re.sub(pattern=pattern, repl="", string=text).replace(" ", "").split("<br/>")
    )

    numbers1 = set({})
    for i in m1:
        l = i.split(".")
        for j in l:
            if j.isdigit():
                numbers1.add(j)
    numbers1 = list(numbers1)
    numbers1.sort()
    lunch_al = allergy(numbers1)
    numbers2 = set({})
    for i in m2:
        l = i.split(".")
        for j in l:
            if j.isdigit():
                numbers2.add(j)
    numbers2 = list(numbers2)
    numbers2.sort()
    dinner_al = allergy(numbers2)

    return lunch_menu, lunch_al, dinner_menu, dinner_al


def page_lunch(date):
    url = "http://icpa.icehs.kr/foodlist.do?m=070306&s=icpa"
    # url = "http://icpa.icehs.kr/foodlist.do?year=2023&month=05&m=070306&s=icpa"

    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    return page_meal(soup, date, "중식")


def page_dinner(date):
    global driver

    driver.get("http://icpa.icehs.kr/foodlist.do?m=070306&s=icpa")
    # driver.get("http://icpa.icehs.kr/foodlist.do?year=2023&month=05&m=070306&s=icpa")

    dinner_button = driver.find_element(By.XPATH, '//*[@id="D"]')
    dinner_button.click()

    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")
    return page_meal(soup, date, "석식")


def allergy(numbers):
    for j, i in enumerate(numbers):
        # print(i)
        if i == "1":
            numbers[j] = "난류"
        elif i == "2":
            numbers[j] = "우유"
        elif i == "3":
            numbers[j] = "메밀"
        elif i == "4":
            numbers[j] = "땅콩"
        elif i == "5":
            numbers[j] = "대두"
        elif i == "6":
            numbers[j] = "밀"
        elif i == "7":
            numbers[j] = "고등어"
        elif i == "8":
            numbers[j] = "게"
        elif i == "9":
            numbers[j] = "새우"
        elif i == "10":
            numbers[j] = "돼지"
        elif i == "11":
            numbers[j] = "복숭아"
        elif i == "12":
            numbers[j] = "토마토"
        elif i == "13":
            numbers[j] = "아황산류"
        elif i == "14":
            numbers[j] = "호두"
        elif i == "15":
            numbers[j] = "닭고기"
        elif i == "16":
            numbers[j] = "쇠고기"
        elif i == "17":
            numbers[j] = "오징어"
        elif i == "18":
            numbers[j] = "조개류"
        elif i == "19":
            numbers[j] = "잣"
    # print(numbers)
    return numbers


def page_meal(soup, date, meal_type):
    target_table = soup.find("table", "tb_calendar")
    tds = target_table.find_all("td")

    try:
        td = tds[date]
    except:
        print("meal -> tds error")
        raise ValueError
    finally:
        ul = str(td.find("ul")).split("<br/>")
        meal = ul[:-2]

        if meal == []:
            raise ValueError
        else:
            # print(meal)
            numbers = set({})
            # for i in m1:
            #     l = i.split(".")
            #     for j in l:
            #         if j.isdigit():
            #             numbers1.add(j)
            # numbers1 = list(numbers1)
            # numbers1.sort()
            # lunch_al = allergy(numbers1)

            for i in range(len(meal)):
                for _ in range(meal[i].count(".")):
                    f = meal[i].find(".")
                    if meal[i][f - 2 : f].isdigit():
                        numbers.add(meal[i][f - 2 : f])
                        meal[i] = meal[i][: f - 2] + meal[i][f + 1 :]
                        # print("2digit")
                    elif meal[i][f - 1].isdigit():
                        numbers.add(meal[i][f - 1 : f])
                        meal[i] = meal[i][: f - 1] + meal[i][f + 1 :]
                        # print("1digit")
                    else:
                        meal[i] = meal[i][:f] + meal[i][f + 1 :]
                        # print("0digit")

            for i in range(len(meal)):
                meal[i] = meal[i].replace(" ", "")
                meal[i] = meal[i].replace("OV", "")
                meal[i] = meal[i].replace(".", "")
                meal[i] = meal[i].replace("\n", "")
                meal[i] = meal[i].replace("<ul>", "")

            numbers = list(numbers)
            numbers.sort()
            # print(numbers)
            al = allergy(numbers)
            # print(meal)
            # print(al)

            return_list = [meal, al]
            return return_list


def return_menu(date):
    today = datetime.date.today()
    if date == "오늘":
        day = int(today.strftime("%d"))
        d1 = today.strftime("%y%m") + str(day)
        d2 = day
    elif date == "내일":
        today = today + timedelta(days=1)
        day = int(today.strftime("%d"))
        d1 = today.strftime("%y%m") + str(day)
        d2 = day
    try:
        menu = neis_menu(d1)
        return menu[0], menu[1], menu[2], menu[3]
    except:
        try:
            l = page_lunch(d2)
            d = page_dinner(d2)
            return l[0], l[1], d[0], d[1]
        except:
            return False


print(return_menu("오늘"))
print(return_menu("내일"))
