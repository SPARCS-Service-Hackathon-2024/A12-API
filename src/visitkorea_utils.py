import numpy as np
import pandas as pd
import requests
import json
import requests
from utils import *

#향후 지역기반관광정보조회 시 필요한 기초 정보들 수집용 코드

#Refer https://www.data.go.kr/data/15101578/openapi.do#/API%20%EB%AA%A9%EB%A1%9D/areaBasedList1

YOUR_API_KEY = None
VISITKOREA_BASE_URL = "http://apis.data.go.kr/B551011/KorService1"

#기본적으로 get에 필요한 params들임. 향후 이용시 VISITKOREA_BASIC_PARAMS.copy() 로 사용
VISITKOREA_BASIC_PARAMS = { 
    "serviceKey": YOUR_API_KEY,
    "MobileOS": "WIN",
    "MobileApp": "api_testing",
    "_type": "json" 
    }

def get_visitkorea_api(endpoint:str,
                       params:dict) -> json:

    response = requests.get(VISITKOREA_BASE_URL + endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("API 요청이 실패하였습니다.")
        print(response.status_code)
        return None

def save_serviceCode_cat1():
    """
    서비스분류코드 조회의 대분류를 json 형태로 저장
    """
    params = VISITKOREA_BASIC_PARAMS.copy()
    params.update({"numOfRows": 100})
    endpoint = "/categoryCode1"
    
    info = get_visitkorea_api(endpoint,params)
    save_to_json(info, "serviceCode_cat1.json")

def save_serviceCode_cat2():
    """
    서비스분류코드 조회의 중분류를 json 형태로 저장
    """
    endpoint = "/categoryCode1"
    serviceCode_cat1 = read_from_json("serviceCode_cat1.json")
    
    
    only_save_cat2_item = {"items": [] }
    
    for item in serviceCode_cat1['response']['body']['items']['item']:
        #저장된 cat1.json에서 대분류를 가져와, 각각 중분류 정보 호출
        cat1 = item['code']
        params = VISITKOREA_BASIC_PARAMS.copy()
        params.update({"numOfRows": 100,
                     "cat1": cat1})
        
        info = get_visitkorea_api(endpoint,params)
        
        only_save_cat2_item['items'].extend(info['response']['body']['items']['item'])
        
    save_to_json(only_save_cat2_item, "serviceCode_cat2.json")


def save_serviceCode_cat3():
    """
    서비스분류코드 조회의 소분류를 json 형태로 저장
    
    two pointer 알고리즘 사용하여 대분류-중분류-소분류 형식으로 저장되도록 함.
    """
    endpoint = "/categoryCode1"
    serviceCode_cat1 = read_from_json("serviceCode_cat1.json")
    serviceCode_cat2 = read_from_json("serviceCode_cat2.json")
    
    save_items_json = {"items": {} }
    
    item2_pointer = 0
    for item1 in serviceCode_cat1['response']['body']['items']['item']:
        #저장된 cat1.json에서 대분류를 가져와, 각각 중분류 정보 호출
        cat1 = item1['code']
        save_items_json['items'][cat1] = {}
        
        #최대 길이 초과 전까지 반복
        while (item2_pointer<len(serviceCode_cat2['items'])):
            cat2 = serviceCode_cat2['items'][item2_pointer]['code']
            item2_pointer+=1
            save_items_json['items'][cat1][cat2] = []
            if cat1 in cat2:
                params = VISITKOREA_BASIC_PARAMS.copy()
                params.update({"numOfRows": 100,
                                "cat1": cat1,
                                "cat2": cat2})
                info = get_visitkorea_api(endpoint,params)
                save_items_json['items'][cat1][cat2].extend(info['response']['body']['items']['item'])
            else:
                break
        
    save_to_json(save_items_json, "serviceCode_cat3.json")


def save_regionCode_cat1():
    """
    지역분류코드 조회의 지역코드를 json 형태로 저장
    """
    params = VISITKOREA_BASIC_PARAMS.copy()
    params.update({"numOfRows": 100})
    endpoint = "/areaCode1"
    
    info = get_visitkorea_api(endpoint,params)
    save_to_json(info, "areaCode_cat1.json")

def save_regionCode_cat2():
    """
    지역분류코드 조회의 시군구코드를 json 형태로 저장
    """
    endpoint = "/areaCode1"
    regionCode_cat1 = read_from_json("areaCode_cat1.json")
    
    
    only_save_name2_item = {"items": {} }
    
    for item in regionCode_cat1['response']['body']['items']['item']:
        #저장된 cat1.json에서 대분류를 가져와, 각각 중분류 정보 호출
        code = item['code']
        params = VISITKOREA_BASIC_PARAMS.copy()
        params.update({"numOfRows": 100,
                     "areaCode": code})
        
        info = get_visitkorea_api(endpoint,params)
        
        only_save_name2_item['items'][code] = (info['response']['body']['items']['item'])
        
    save_to_json(only_save_name2_item, "areaCode_cat2.json")


if __name__=="__main__":
    
    #save_serviceCode_cat1()
    #save_serviceCode_cat2()
    #save_serviceCode_cat3()
    
    #save_regionCode_cat1()
    #save_regionCode_cat2()
    pass