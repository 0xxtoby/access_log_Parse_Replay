import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pprint import pprint
import requests
from loguru import logger

# 日志格式
# dhost -- rhost -- time -- [recv] -- [Protocol:HTTP;] -- http_request
# :80 -- 127.0.0.1:62674 -- [2023.02.18 11:30:03] -- [recv] -- [Protocol:HTTP;] -- "POST /chrome_record.php

HOST_INDEX = 0
TIME_INDEX = 2
REQUEST_INDEX = 5

lock = threading.Lock()


class http_data(object):
    def __init__(self, host: str = None, path: str = None, headers=None, body: str = None, method: str = None,
                 time=None):
        self.host = host
        self.path = path
        self.headers = headers
        self.body = body
        self.method = method
        self.time = time

    def replay(self, speedup=1):

        url = "http://" + self.host + self.path
        if self.method == "GET":
            try:
                req_result = "OK"
                requests.get(url, headers=self.headers)
            except Exception:
                req_result = "FAILED"
        else:
            try:
                req_result = "OK"
                requests.post(url, headers=self.headers, data=self.body)
            except Exception:
                req_result = "FAILED"

        lock.acquire()
        logger.success(" REQUEST: %s -- %s" % (url, req_result))

        lock.release()


def parse_logfile(filename):
    """分析日志文件并返回一个包含元组的对象列表
    """
    logfile = open(filename, "r")
    reqs = []
    for line in logfile:
        parts = line.split("--")

        time_text = parts[TIME_INDEX].strip()[1:-1]
        request_time = datetime.strptime(time_text, "%Y.%m.%d %H:%M:%S")

        host = parts[HOST_INDEX]
        if host[0] == ":":
            host = "127.0.0.1" + host.strip()

        http_request = parts[REQUEST_INDEX].strip()[1:-2]
        if http_request[0:3] == "POS" or http_request[0:3] == "GET":
            request_line = http_request.split("\\n")[0].strip()
            method = request_line.split(" ")[0]
            path = request_line.split(" ")[1]
            request_header = http_request.split("\\n")[1:-2]
            header = {}
            for i in request_header:
                try:
                    header[i.split(":")[0].strip()] = i.split(":")[1].strip()
                except:
                    logger.error("Invalid header:{}".format(i))

            request_body = http_request.split("\\n")[-1]

            reqs.append(
                http_data(host=host, path=path, headers=header, body=request_body, method=method, time=request_time))
        else:
            reqs[-1].body = reqs[-1].body + http_request
            # print(http_request)

    if not reqs:
        logger.debug("Seems like I don't know how to parse this file!")
    return reqs


if __name__ == '__main__':
    r = parse_logfile("20230218.asclog")

    # 线程池
    pool = ThreadPoolExecutor(max_workers=10)

    for i in r:
        time.sleep(0.01) #线程之间延迟10ms
        pool.submit(i.replay, )


