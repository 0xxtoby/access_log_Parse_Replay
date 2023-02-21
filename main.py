import argparse
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pprint import pprint
import requests
from loguru import logger


class Http_Data(object):
    def __init__(self, host: str = None, path: str = None, headers=None, body: str = None, method: str = None,
                 time=None):
        self.host = host
        self.path = path
        self.headers = headers
        self.body = body
        self.method = method
        self.time = time
        self.flag = 0

    def replay(self, speedup=1):

        url = "http://" + self.host + self.path
        if self.method == "GET":
            try:
                req_result = "OK"
                requests.get(url, headers=self.headers, proxies=PROXY)
            except Exception:
                req_result = "FAILED"
        else:
            try:
                req_result = "OK"
                requests.post(url, headers=self.headers, data=self.body, proxies=PROXY)
            except Exception:
                req_result = "FAILED"

        lock.acquire()
        logger.success(" REQUEST: %s %s -- prox: %s -- %s" % (self.method, url, proxy, req_result))

        lock.release()


def parse_logfile(http_d_0: Http_Data, file_line: str = None):
    """分析日志文件并返回一个包含元组的对象列表
    """

    line = file_line
    parts = line.split("--")

    time_text = parts[TIME_INDEX].strip()[1:-1]
    request_time = datetime.strptime(time_text, "%Y.%m.%d %H:%M:%S")

    host = parts[HOST_INDEX]
    if host[0] == ":":
        host = "127.0.0.1" + host.strip()

    http_request = parts[REQUEST_INDEX].strip()[1:-2]
    if http_request[0:3] == "POS" or http_request[0:3] == "GET":
        if http_d_0.flag == 1:
            time.sleep(0.01)
            pool.submit(http_d_0.replay, )

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
        http_d = Http_Data()
        http_d.host = host
        http_d.path = path
        http_d.headers = header
        http_d.body = request_body
        http_d.method = method
        http_d.time = request_time
        http_d.flag = 1

        http_d_0 = http_d
        return http_d_0
    else:
        http_d_0.body = http_d_0.body + http_request
        http_d_0.flag = 1
        return http_d_0
    # print(http_request)


def file_load(log_path):
    count = 0
    position = 0
    http_d_0 = Http_Data()

    with open(log_path, mode='r') as f1:
        while True:
            line = f1.readline()
            if line:
                count += 1
                logger.info("load line count %s " % (count))

                http_d_0 = parse_logfile(http_d_0, line)

            cur_position = f1.tell()  # 记录上次读取文件的位置

            if cur_position == position:
                time.sleep(0.1)
                continue
            else:
                position = cur_position


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='access_log Parse Replay v1.0.0 by toby')
    parser.add_argument('-p', '--proxy', metavar='proxy', type=str, help='send requests to server PROXY')
    parser.add_argument('-t', '--thread', metavar='int', type=int, help=' Thread nums (default 10)')
    parser.add_argument('-f', '--file', metavar='logfile', type=str, required=True, help='access log file')
    args = parser.parse_args()

    # 代理
    proxy = args.proxy
    PROXY = {'http': proxy, 'https': proxy} if proxy else {}

    # 日志格式
    # dhost -- rhost -- time -- [recv] -- [Protocol:HTTP;] -- http_request
    # :80 -- 127.0.0.1:62674 -- [2023.02.18 11:30:03] -- [recv] -- [Protocol:HTTP;] -- "POST /chrome_record.php

    HOST_INDEX = 0
    TIME_INDEX = 2
    REQUEST_INDEX = 5

    # 多线程
    lock = threading.Lock()
    max_workers = args.thread if args.thread else 10
    logger.info("thread count is {}".format(max_workers))
    pool = ThreadPoolExecutor(max_workers=10)

    file_load(args.file)
