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

interval = 5 # 执行秒数

yiBuUserId = ''

# 城市：珠海：440400，中山：442000东莞：441900
cityCode = '440400'

class yiBuQueryAllModel:
    def __init__(self):
        self.result = []
        self.code = ''
        self.msg = ''

def searchCar():

    latitude = '22.254915'
    longitude = '113.55859'

    # 有车查询
    urlJsonParam = {'instance':'5000','latitude':latitude,'longitude':longitude,'cityCode':'440400'}
    jsonUrlData = {'method':'queryParkList','phone':'','cId':yiBuUserId,'version':'1.7.3','memberId':'','type':'member','param':urlJsonParam}
    urlJsonStr = json.dumps(jsonUrlData)
    r = requests.get('https://interface.ibgoing.com/services/i/e/'+ urlJsonStr)
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

            urlJsonParam_li = {'size': '30', 'parkId': stationId,'page':'1'}
            jsonUrlData_li = {'method': 'queryCarList', 'phone': '', 'cId': yiBuUserId,
                           'version': '1.7.3', 'memberId': '', 'type': 'member', 'param': urlJsonParam_li}
            urlJsonStr_li = json.dumps(jsonUrlData_li)
            r_li = requests.get('https://interface.ibgoing.com/services/i/e/' + urlJsonStr_li)

            carResponse_li = r_li.json()
            contentList_li = carResponse_li['result']

            mileAgeList = []
            dianLiangList = []
            for content_li in contentList_li:
                mileAge = content_li['mileage']# 当前可续航里程数
                mileAgeList.append(mileAge)
                dianLiangList.append(content_li['batteryResidual']) # 剩余电量


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

            canRentalAddressList.append('【%s】数量:%s,续航:%s,电量:%s' %(stationName,canRentalNum,mileStr,dianLiangStr))

    if isHave == True:
        print('***宜步有车啦***')
        notifyStr = ''
        for str in canRentalAddressList:
            notifyStr = notifyStr + str

        # Mac os 系统通知
        Notifier.notify(notifyStr,title='宜步有车啦 ' + nowTime,group='ccc')
        Notifier.remove('ccc')
        print(canRentalAddressList)

    else:

        print('宜步还没有车')


def runSearchCar():
    searchCar()
    s.enter(interval, 1, runSearchCar, )  # 方法里面再放一个sched任务，形成循环

def run():
    s.enter(interval,1,runSearchCar,)# 利用sched定时执行任务
    s.run()

if __name__ == "__main__":
    run()

