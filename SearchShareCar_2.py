# encoding:UTF-8

import uCarSearch
import warmCarSearch
import yiBuCarSearch

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

interval = 5

# 定义sched任务，用于循环执行
s = sched.scheduler(time.time, time.sleep)

def searchShareCar():

    uCarSearch.searchCar()
    warmCarSearch.searchCar()
    yiBuCarSearch.searchCar()

    s.enter(interval, 1, searchShareCar, )  # 方法里面再放一个sched任务，形成循环

def run():
    s.enter(interval, 1, searchShareCar, )  # 利用sched定时执行任务
    s.run()


if __name__ == "__main__":
    run()