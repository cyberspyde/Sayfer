from datetime import datetime
import random, string, subprocess, wikipedia, os, requests, threading, json, uuid
from subprocess import call
import azure.cognitiveservices.speech as speechsdk
from chat import get_response, bot_name
from playsound import playsound
from tkinter import *
import numpy as np

mydate = datetime.today().strftime("%y-%m-%d")

key_file = open('../key')
key_data = json.load(key_file)

resource_key = key_data['resource_key']
region = key_data['region']
endpoint = key_data['endpoint']
path = key_data['path']

key_file.close()

def english_to_uzbek(text):
    params = '&from=en&to=uz'
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': resource_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
        'text' : str(text)
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    ans = json.loads(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))


    return ans[0]['translations'][0]['text']

def uzbek_to_english(text):
    params = '&from=uz&to=en'
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': resource_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
        'text' : str(text)
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    ans = json.loads(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))


    return ans[0]['translations'][0]['text'] 


def drop_characters(text):
    a = text
    b = "!@#$()-_=+%&.,\" "
    
    for char in b:
        a = a.replace(char, " ")    

    return a

day_first = {
    1 : "O'n",
    2 : "Yigirma",
    3 : "O'ttiz"
}

day_second = {
    1 : "Birinchi",
    2 : "Ikkinchi",
    3 : "Uchinchi",
    4 : "To'rtinchi",
    5 : "Beshinchi",
    6 : "Oltinchi",
    7 : "Yettinchi",
    8 : "Sakkizinchi",
    9 : "To'qqizinchi",
    0 : "inchi"
}


def day_filter(answer):
    answer = drop_characters(answer)

    digits = [int(s) for s in answer.split() if s.isdigit() and int(s) <= 31 and int(s) >= 10]
    digits2 = [int(s) for s in answer.split() if s.isdigit() and int(s) <= 9]

    digits_in_text = []
    digits_in_text2 = []

    for digit in digits:
        sp = [int(a) for a in str(digit)]
        digits_in_text.append(sp)

    for digit in digits2:
        sp = [int(a) for a in str(digit)]
        digits_in_text2.append(sp)

    day_first_values = []
    day_second_values = []

    day_first_values2 = []

    for p in digits_in_text:
        day_first_values.append(str(p[0]).replace(str(p[0]), day_first[p[0]]))
        day_second_values.append(str(p[1]).replace(str(p[1]), day_second[p[1]]))


    for p in digits_in_text2:
        day_first_values2.append(str(p[0]).replace(str(p[0]), day_second[p[0]]))

    joint_days = {}
    joint_days2 = {}

    for t in range(0, len(digits)):
        days_in_text = day_first_values[t] + " " + day_second_values[t]
        joint_days[digits[t]] = days_in_text 

    for t in range(0, len(digits2)):
        days_in_text2 = day_first_values2[t]
        joint_days2[digits2[t]] = days_in_text2 

    for _ in range(0, len(digits)):
        for t in answer.split():
            if(t.isdigit() and int(t) <= 31 and int(t) >= 10):
                answer = answer.replace(t, joint_days[int(t)])

    for _ in range(0, len(digits2)):
        for t in answer.split():
            if(t.isdigit() and int(t) <= 9):
                answer = answer.replace(t, joint_days2[int(t)])

    return answer

def year_filter(answer):
    year_first = {
        1 : "bir ming",
        2 : "ikki ming",
        3 : "uch ming",
        4 : "to'rt ming",
        5 : "besh ming",
        6 : "olti ming",
        7 : "yetti ming",
        8 : "sakkiz ming",
        9 : "to'qqiz ming"
    }

    year_second = {
        1 : "bir yuz",
        2 : "ikkiyuz",
        3 : "uchyuz",
        4 : "to'rtyuz",
        5 : "beshyuz",
        6 : "oltiyuz",
        7 : "yettiyuz",
        8 : "sakkizyuz",
        9 : "to'qqizyuz",
        0 : ""
    }

    year_third = {
        1 : "o'n",
        2 : "yigirma",
        3 : "o'ttiz",
        4 : "qirq",
        5 : "ellik",
        6 : "oltmish",
        7 : "yetmish",
        8 : "sakson",
        9 : "to'qson",
        0 : ""

    }

    year_fourth = {
        1 : "birinchi",
        2 : "ikkinchi",
        3 : "uchinchi",
        4 : "to'rtinchi",
        5 : "beshinchi",
        6 : "oltinchi",
        7 : "yettinchi",
        8 : "sakkizinchi",
        9 : "to'qqizzinchi",
        0 : "inchi"
    }

    answer = drop_characters(answer)

    digits = [int(s) for s in answer.split() if s.isdigit() and int(s) >= 1000]
    
    digits_in_text = []
    for k in digits:
        seperate_year_digits = [int(b) for b in str(k)]
        digits_in_text.append(seperate_year_digits)

    year_first_values = []
    year_second_values = []
    year_third_values = []
    year_fourth_values = []


    for p in digits_in_text:
        year_first_values.append(str(p[0]).replace(str(p[0]), year_first[p[0]]))
        year_second_values.append(str(p[1]).replace(str(p[1]), year_second[p[1]]))
        year_third_values.append(str(p[2]).replace(str(p[2]), year_third[p[2]]))
        year_fourth_values.append(str(p[3]).replace(str(p[3]), year_fourth[p[3]]))

    joint_years = {}
    for t in range(0, len(digits)):
        years_in_text = year_first_values[t] + " " + year_second_values[t] + " " + year_third_values[t] + " " + year_fourth_values[t]
        joint_years[digits[t]] = years_in_text 


    for _ in range(0, len(digits)):
        for t in answer.split():
            if(t.isdigit() and int(t) >= 1000):
                answer = answer.replace(t, joint_years[int(t)])

    return answer


def get_current_time():
    answer = datetime.now().strftime("%H-%M").split("-",1)
    hour = int(answer[0])
    minute = int(answer[1])

    if (minute > 9):
        minute_digits = [int(a) for a in str(minute)]
        minute_last = minute_digits[1]
        minute_first = minute_digits[0]

    minute_say = ""

    if minute in range(10, 20):
        minute_say = "o'n"
    elif minute in range(20, 30):
        minute_say = "yigirma"
    elif minute in range(30, 40):
        minute_say = "o'ttiz"
    elif minute in range(40, 50):
        minute_say = "qirq"
    elif minute in range(50, 60):
        minute_say = "ellik"



    if (hour > 9):
        hour_digits = [int(a) for a in str(hour)]
        hour_last = hour_digits[1]
        hour_first = hour_digits[0]

    hour_say = ""

    if hour in range(10, 20):
        hour_say = "o'n"
    elif hour in range(20, 24):
        hour_say = "yigirma"



    if(minute <= 9 and hour <= 9):
        currentTime = f"Soat {hour} dan, {minute} daqiqa o'tdi."
    elif(minute >= 10 and hour <= 9):
        currentTime = f"Soat {hour} dan, {minute_say} {minute_last} daqiqa o'tdi."
    elif(minute <= 9 and hour >= 10):
        currentTime = f"Soat {hour_say} {hour_last} dan, {minute} daqiqa o'tdi."
    elif(minute >= 10 and hour >= 10):
        currentTime = f"Soat {hour_say} {hour_last} dan, {minute_say} {minute_last} daqiqa o'tdi."

    return currentTime
