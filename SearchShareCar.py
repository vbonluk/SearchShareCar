# encoding:UTF-8
import requests
import json
import sched
import time
from pync import Notifier
import os
import json

import ssl

# 设置 全局取消证书验证 http://blog.csdn.net/moonhillcity/article/details/52767999
ssl._create_default_https_context = ssl._create_unverified_context

# 定义sched任务，用于循环执行
s = sched.scheduler(time.time, time.sleep)

interval = 2  # 执行秒数

uCarUserId = '689c2871f8679b169f3ef5a51bdd2a18' # 689c2871f8679b169f3ef5a51bdd2a18 是默认的
warmCarUserId = ''
yiBuUserId = ''

# 宜步出行参数 城市：珠海：440400，中山：442000东莞：441900
cityCode = '440400'


class uCarQueryAllModel:
    def __init__(self):
        self.content = []
        self.ret = 0
        self.msg = ''


def searchCar_uCar():
    # 有车查询
    postdata = {"citycode": "440402", "cityCode": "440402", "sign": uCarUserId}
    header = {'URCARSPID': '00100'}
    r = requests.post("http://www.ur-car.com.cn:8082/urcar/station/queryAllStation", data=postdata, headers=header)

    uc = uCarQueryAllModel()
    uc.__dict__ = r.json()

    isHave = False
    canRentalAddressList = []
    nowTime = time.strftime("%l:%M:%S", time.localtime())
    print(nowTime)

    for content in uc.content:
        canRentalNum = content['canRentalNum']
        stationName = content['stationName']
        if canRentalNum != 0:
            isHave = True
            # 当前可租车辆的可用里程查询
            stationId = content['id']

            postdata_li = {"stationId": stationId, "cityCode": "undefined"}
            header_li = {'URCARSPID': '00100'}
            r_li = requests.post("http://www.ur-car.com.cn:8082/urcar/vehicle/queryVehicleByStationId",
                                 data=postdata_li,
                                 headers=header_li)

            carResponse_li = r_li.json()
            contentList_li = carResponse_li['content']

            mileAgeList = []
            dianLiangList = []
            for content_li in contentList_li:
                vehicleType = content_li['vehicleType']
                mileAge = vehicleType['mileAge']  # 当前可续航里程数
                mileAgeList.append(mileAge)
                activityHandlerParamList = content_li['activityHandlerParamList']
                for activityHandlerParam in activityHandlerParamList:
                    maxMilage = activityHandlerParam['maxMilage']  # 最大续航
                dianLiang = mileAge / maxMilage * 100
                dianLiang = mileAge / 160 * 100  # 感觉接口的maxMilage=300是固定假数据暂时设定160
                dianLiangList.append(dianLiang)

            mileStr = ''
            for index in range(len(mileAgeList)):
                if index == 0:
                    mileStr = '%d' % (mileAgeList[index])
                else:
                    mileStr = mileStr + ',%d' % (mileAgeList[index])

            dianLiangStr = ''
            for index in range(len(dianLiangList)):
                if index == 0:
                    dianLiangStr = '%d%%' % (dianLiangList[index])
                else:
                    dianLiangStr = dianLiangStr + ',%d%%' % (dianLiangList[index])

            canRentalAddressList.append('【%s】数量:%d,续航:%s,电量:%s' % (stationName, canRentalNum, mileStr, dianLiangStr))

    if isHave == True:
        print('***uCar有车啦***')
        notifyStr = ''
        for str in canRentalAddressList:
            notifyStr = notifyStr + str

        # Mac os 系统通知
        Notifier.notify(notifyStr, title='uCar有车啦 ' + nowTime, group='aaa')
        Notifier.remove('aaa')
        print(canRentalAddressList)

    else:

        print('uCar还没有车')


class warmCarQueryAllModel:
    def __init__(self):
        self.data = []
        self.status = ''


def searchCar_warmCar():
    latitude = '22.254915'
    longitude = '113.55859'

    # 有车查询
    postdata = {"cityId": "200", "comCode": "GZPH001", "lang": "zh", 'latitude': latitude, 'longitude': longitude}
    header = {}
    r = requests.post("https://app.feezu.cn/car/findCompanyStation", data=postdata, headers=header)

    uc = warmCarQueryAllModel()
    uc.__dict__ = r.json()

    isHave = False
    canRentalAddressList = []
    nowTime = time.strftime("%l:%M:%S", time.localtime())
    print(nowTime)

    for content in uc.data:
        canRentalNum = content['avaliableCarNum']
        stationName = content['stationName']
        if canRentalNum != 0:
            isHave = True
            # 当前可租车辆的可用里程查询
            stationId = content['stationId']

            postdata_li = {"stationId": stationId, "businessType": "3", 'comCode': 'GZPH001', 'lang': 'zh',
                           'latitude': latitude, 'longitude': longitude}
            header_li = {}
            r_li = requests.post("https://app.feezu.cn/car/findCarsByStationId", data=postdata_li,
                                 headers=header_li)

            carResponse_li = r_li.json()
            contentList_li = carResponse_li['data']

            mileAgeList = []
            dianLiangList = []
            for content_li in contentList_li:
                mileAge = content_li['mileLeft']  # 当前可续航里程数
                mileAgeList.append(mileAge)
                dianLiangList.append(content_li['fuelPercentage'])  # 剩余电量

            mileStr = ''
            for index in range(len(mileAgeList)):
                if index == 0:
                    mileStr = '%s' % (mileAgeList[index])
                else:
                    mileStr = mileStr + ',%s' % (mileAgeList[index])

            dianLiangStr = ''
            for index in range(len(dianLiangList)):
                if index == 0:
                    dianLiangStr = '%s' % (dianLiangList[index])
                else:
                    dianLiangStr = dianLiangStr + ',%s' % (dianLiangList[index])

            canRentalAddressList.append('【%s】数量:%d,续航:%s,电量:%s' % (stationName, canRentalNum, mileStr, dianLiangStr))

    if isHave == True:
        print('***WarmCar有车啦***')
        notifyStr = ''
        for str in canRentalAddressList:
            notifyStr = notifyStr + str

        # Mac os 系统通知
        Notifier.notify(notifyStr, title='WarmCar有车啦 ' + nowTime, group='bbb')
        Notifier.remove('bbb')
        print(canRentalAddressList)

    else:

        print('WarmCar还没有车')


class yiBuQueryAllModel:
    def __init__(self):
        self.result = []
        self.code = ''
        self.msg = ''


def searchCar_yiBuCar():
    latitude = '22.254915'
    longitude = '113.55859'

    # 有车查询
    urlJsonParam = {'instance': '5000', 'latitude': latitude, 'longitude': longitude, 'cityCode': '440400'}
    jsonUrlData = {'method': 'queryParkList', 'phone': '', 'cId': yiBuUserId,
                   'version': '1.7.3', 'memberId': '', 'type': 'member', 'param': urlJsonParam}
    urlJsonStr = json.dumps(jsonUrlData)
    r = requests.get('https://interface.ibgoing.com/services/i/e/' + urlJsonStr)
    uc = yiBuQueryAllModel()
    uc.__dict__ = r.json()

    isHave = False
    canRentalAddressList = []
    nowTime = time.strftime("%l:%M:%S", time.localtime())
    print(nowTime)

    for content in uc.result:
        canRentalNum = content['freeCarNum']
        stationName = content['address']

        cityCodeResult = content['cityCode']

        if cityCodeResult != cityCode:
            continue

        if int(canRentalNum) != 0:
            isHave = True
            # 当前可租车辆的可用里程查询
            stationId = content['parkId']

            urlJsonParam_li = {'size': '30', 'parkId': stationId, 'page': '1'}
            jsonUrlData_li = {'method': 'queryCarList', 'phone': '', 'cId': yiBuUserId,
                              'version': '1.7.3', 'memberId': '', 'type': 'member', 'param': urlJsonParam_li}
            urlJsonStr_li = json.dumps(jsonUrlData_li)
            r_li = requests.get('https://interface.ibgoing.com/services/i/e/' + urlJsonStr_li)

            carResponse_li = r_li.json()
            contentList_li = carResponse_li['result']

            mileAgeList = []
            dianLiangList = []
            for content_li in contentList_li:
                mileAge = content_li['mileage']  # 当前可续航里程数
                mileAgeList.append(mileAge)
                dianLiangList.append(content_li['batteryResidual'])  # 剩余电量

            mileStr = ''
            for index in range(len(mileAgeList)):
                if index == 0:
                    mileStr = '%s' % (mileAgeList[index])
                else:
                    mileStr = mileStr + ',%s' % (mileAgeList[index])

            dianLiangStr = ''
            for index in range(len(dianLiangList)):
                if index == 0:
                    dianLiangStr = '%s%%' % (dianLiangList[index])
                else:
                    dianLiangStr = dianLiangStr + ',%s%%' % (dianLiangList[index])

            canRentalAddressList.append('【%s】数量:%s,续航:%s,电量:%s' % (stationName, canRentalNum, mileStr, dianLiangStr))

    if isHave == True:
        print('***宜步有车啦***')
        notifyStr = ''
        for str in canRentalAddressList:
            notifyStr = notifyStr + str

        # Mac os 系统通知
        Notifier.notify(notifyStr, title='宜步有车啦 ' + nowTime, group='ccc')
        Notifier.remove('ccc')
        print(canRentalAddressList)

    else:

        print('宜步还没有车')


def searchCar():
    searchCar_uCar()
    searchCar_warmCar()
    searchCar_yiBuCar()
    s.enter(interval, 1, searchCar, )  # 方法里面再放一个sched任务，形成循环


def run():
    s.enter(interval, 1, searchCar, )  # 利用sched定时执行任务
    s.run()


if __name__ == "__main__":
    run()
