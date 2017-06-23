# encoding:UTF-8
import requests
import json
import sched
import time
from pync import Notifier
import os
import json

# 定义sched任务，用于循环执行
s = sched.scheduler(time.time, time.sleep)

interval = 5 # 执行秒数

uCarUserId = '689c2871f8679b169f3ef5a51bdd2a18'# 689c2871f8679b169f3ef5a51bdd2a18 是默认的

class uCarQueryAllModel:
    def __init__(self):
        self.content = []
        self.ret = 0
        self.msg = ''

def searchCar():

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
            r_li = requests.post("http://www.ur-car.com.cn:8082/urcar/vehicle/queryVehicleByStationId", data=postdata_li,
                              headers=header_li)

            carResponse_li = r_li.json()
            contentList_li = carResponse_li['content']

            mileAgeList = []
            dianLiangList = []
            for content_li in contentList_li:
                vehicleType = content_li['vehicleType']
                mileAge = vehicleType['mileAge']# 当前可续航里程数
                mileAgeList.append(mileAge)
                activityHandlerParamList = content_li['activityHandlerParamList']
                for activityHandlerParam in activityHandlerParamList:
                    maxMilage = activityHandlerParam['maxMilage']  # 最大续航
                dianLiang = mileAge / maxMilage*100
                dianLiang = mileAge / 160 *100 # 感觉接口的maxMilage=300是固定假数据暂时设定160
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

            canRentalAddressList.append('【%s】数量:%d,续航:%s,电量:%s' %(stationName,canRentalNum,mileStr,dianLiangStr))

    if isHave == True:
        print('***uCar有车啦***')
        notifyStr = ''
        for str in canRentalAddressList:
            notifyStr = notifyStr + str

        # Mac os 系统通知
        Notifier.notify(notifyStr,title='uCar有车啦 ' + nowTime,group='aaa')
        Notifier.remove('aaa')
        print(canRentalAddressList)

    else:

        print('uCar还没有车')



def runSearchCar():
    searchCar()
    s.enter(interval, 1, runSearchCar, )  # 方法里面再放一个sched任务，形成循环

def run():
    s.enter(interval,1,runSearchCar,)# 利用sched定时执行任务
    s.run()

if __name__ == "__main__":
    run()

