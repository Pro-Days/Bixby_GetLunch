import json
import re
import datetime
from datetime import timedelta
import urllib.request

import boto3

client = boto3.resource("dynamodb")
table = client.Table("Menu_dinner")


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


def return_menu(date):
    today = datetime.datetime.now()
    today = today + timedelta(hours=9)
    print(today)
    if date == "내일":
        today = today + timedelta(days=1)
        day = int(today.strftime("%d"))
        d1 = today.strftime("%y%m") + str(day)
    else:
        day = int(today.strftime("%d"))
        d1 = today.strftime("%y%m") + str(day)
    try:
        menu = neis_menu(d1)
        if menu[2] == []:
            data1 = ["정보없음"]
            print("메뉴 정보없음")
        else:
            data1 = menu[2]
        if menu[3] == []:
            data2 = ["정보없음"]
            print("알레르기 정보없음")
        else:
            data2 = menu[3]
        return data1, data2
    except:
        print(date + "오류")
        return ["정보없음"], ["정보없음"]


def lambda_handler(event, context):
    items = return_menu("오늘")
    today = datetime.datetime.now()
    today = today + timedelta(hours=9)
    date_today = today.strftime("%y년 %m월 %d일")

    dinner_menu = ",".join(items[0])
    dinner_al = ",".join(items[1])

    table.update_item(
        Key={"date": "오늘"},
        UpdateExpression="SET menu = :menu, allergy = :allergy, meal_type = :meal_type, ymd = :ymd",
        ExpressionAttributeValues={
            ":menu": dinner_menu,
            ":allergy": dinner_al,
            ":meal_type": "석식",
            ":ymd": date_today,
        },
    )

    items = return_menu("내일")
    today = datetime.datetime.now()
    today = today + timedelta(hours=9)
    today = today + timedelta(days=1)
    date_tomorrow = today.strftime("%y년 %m월 %d일")

    dinner_menu = ",".join(items[0])
    dinner_al = ",".join(items[1])

    table.update_item(
        Key={"date": "내일"},
        UpdateExpression="SET menu = :menu, allergy = :allergy, meal_type = :meal_type, ymd = :ymd",
        ExpressionAttributeValues={
            ":menu": dinner_menu,
            ":allergy": dinner_al,
            ":meal_type": "석식",
            ":ymd": date_tomorrow,
        },
    )

    return {"statusCode": 200, "body": json.dumps("Status Update Complete!")}
