# encoding:UTF-8
import requests
import json
import sched
import time
from pync import Notifier
import os
import json
import sys

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

    latitude = '23.027622'
    longitude = '113.758517'

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
        icon_file = cur_file_dir() + "/icon_searchCar.ico"
        Notifier.notify(notifyStr, title='宜步有车啦 ' + nowTime, group='ccc', closeLabel='关闭', actions='一键下单(暂不开放)',
                        appIcon=icon_file)
        Notifier.remove('ccc')
        print(canRentalAddressList)

    else:

        print('宜步还没有车,请切换城市')

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

