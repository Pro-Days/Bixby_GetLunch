import os
import sys
import urllib.request
import datetime
from datetime import timedelta
import re
import json


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


def neis_menu(date):
    atpt_code = "E10"
    school_code = 7310447
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE={atpt_code}&SD_SCHUL_CODE={school_code}&MLSV_YMD={date}&KEY=02d3ebad34ee4f7a90282b2f495c3603&Type=json&pIndex=1&pSize=100"
    # print(url)
    response = urllib.request.urlopen(url)
    response_body = response.read()
    data = json.loads(response_body.decode("utf-8"))

    pattern = r"\([\d]*\)"
    p = re.compile("\(([^)]+)")
    # print(data)

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


def return_menu(date):
    today = datetime.date.today()
    if date == "내일":
        today = today + timedelta(days=1)
        day = int(today.strftime("%d"))
        d1 = today.strftime("%y%m") + str(day)
        d2 = day
    else:
        day = int(today.strftime("%d"))
        d1 = today.strftime("%y%m") + str(day)
        d2 = day
    try:
        menu = neis_menu(d1)
        datas = []
        if menu[0] == []:
            datas.append(["정보없음"])
        else:
            datas.append(menu[0])
        if menu[1] == []:
            datas.append(["정보없음"])
        else:
            datas.append(menu[1])
        if menu[2] == []:
            datas.append(["정보없음"])
        else:
            datas.append(menu[2])
        if menu[3] == []:
            datas.append(["정보없음"])
        else:
            datas.append(menu[3])
        return datas
    except:
        return ["정보없음" for _ in range(4)]


menu = return_menu("오늘")

lunch_menu = menu[0]
lunch_al = menu[1]
dinner_menu = menu[2]
dinner_al = menu[3]

print(lunch_menu, lunch_al)
# print(dinner_menu, dinner_al)
