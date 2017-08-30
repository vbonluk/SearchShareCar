# encoding:UTF-8
import requests
import json
import sched
import time
from win10toast import ToastNotifier
import os
import json
import sys

import ssl
# 设置 全局取消证书验证 http://blog.csdn.net/moonhillcity/article/details/52767999
ssl._create_default_https_context = ssl._create_unverified_context

# 定义sched任务，用于循环执行
s = sched.scheduler(time.time, time.sleep)

interval = 5 # 执行秒数

toaster = ToastNotifier()

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
    orderNameList = ['金嘉', '山姆']
    canRentalAddressList = []
    nowTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
    print(nowTime)

    for content in uc.data:
        OrderNameData = content['stationName']

        isHaveOrderNameInList = False  # 是否含有查询的站点
        for orderName in orderNameList:
            if orderName in OrderNameData:  # 模糊对比，包含有字符就行
                isHaveOrderNameInList = True

        if isHaveOrderNameInList == True:
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
        print(canRentalAddressList)

    for orderName_2 in orderNameList:
        isStationHaveCar = False
        for str in canRentalAddressList:
            if orderName_2 in str:  # 模糊对比，包含有字符就行
                isStationHaveCar = True

        if isStationHaveCar == False:
            print('WarmCar还没有车：' + orderName_2)

    # 由于调用Windows的GUI空间耗时比较长，故放到最后执行。
    if isHave == True:
        notifyStr = ''
        for str in canRentalAddressList:
            notifyStr = notifyStr + str

        # Windows 系统通知
        icon_file = cur_file_dir() + "/icon_searchCar.ico"
        toaster.show_toast(notifyStr, 'WarmCar有车啦 ', icon_file)
        # print(cur_file_dir())

#获取脚本文件的当前路径
def cur_file_dir():
     #获取脚本路径
     path = sys.path[0]
     #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)

def runSearchCar():
    searchCar()
    s.enter(interval, 1, runSearchCar, )  # 方法里面再放一个sched任务，形成循环

def run():
    s.enter(interval,1,runSearchCar,)# 利用sched定时执行任务
    s.run()

if __name__ == "__main__":
    run()

