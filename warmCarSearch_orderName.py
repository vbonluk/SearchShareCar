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

warmCarUserId = ''

class warmCarQueryAllModel:
    def __init__(self):
        self.data = []
        self.status = ''

def searchCar():

    latitude = '22.254915'
    longitude = '113.55859'

    # 有车查询
    postdata = {"cityId": "200", "comCode": "GZPH001", "lang": "zh",'latitude':latitude,'longitude':longitude}
    header = {}
    r = requests.post("https://app.feezu.cn/car/findCompanyStation", data=postdata, headers=header)

    uc = warmCarQueryAllModel()
    uc.__dict__ = r.json()

    isHave = False
    orderName = '安驰修车行'
    canRentalAddressList = []
    nowTime = time.strftime("%l:%M:%S", time.localtime())
    print(nowTime)

    for content in uc.data:
        OrderNameData = content['stationName']
        if orderName in OrderNameData:
            print('找到站点：' + OrderNameData)
        else:
            continue

        canRentalNum = content['avaliableCarNum']
        stationName = content['stationName']
        if canRentalNum != 0:
            isHave = True
            # 当前可租车辆的可用里程查询
            stationId = content['stationId']

            postdata_li = {"stationId": stationId, "businessType": "3",'comCode':'GZPH001','lang':'zh','latitude':latitude,'longitude':longitude}
            header_li = {}
            r_li = requests.post("https://app.feezu.cn/car/findCarsByStationId", data=postdata_li,
                              headers=header_li)

            carResponse_li = r_li.json()
            contentList_li = carResponse_li['data']

            mileAgeList = []
            dianLiangList = []
            for content_li in contentList_li:
                mileAge = content_li['mileLeft']# 当前可续航里程数
                mileAgeList.append(mileAge)
                dianLiangList.append(content_li['fuelPercentage']) # 剩余电量

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

            canRentalAddressList.append('【%s】数量:%d,续航:%s,电量:%s' %(stationName,canRentalNum,mileStr,dianLiangStr))

    if isHave == True:
        print('***WarmCar有车啦***')
        notifyStr = ''
        for str in canRentalAddressList:
            notifyStr = notifyStr + str

        # Mac os 系统通知
        Notifier.notify(notifyStr,title='WarmCar有车啦 ' + nowTime,group='bbb')
        Notifier.remove('bbb')
        print(canRentalAddressList)

    else:

        print('WarmCar还没有车：' + orderName)


def runSearchCar():
    searchCar()
    s.enter(interval, 1, runSearchCar, )  # 方法里面再放一个sched任务，形成循环

def run():
    s.enter(interval,1,runSearchCar,)# 利用sched定时执行任务
    s.run()

if __name__ == "__main__":
    run()

