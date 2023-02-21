# access_log Parse Replay
监测access_log 文件增量，进行http包重发
# 1、 安装
```
pip install requests
pip install loguru
```
# 2、使用
```
usage: main.py [-h] [-p proxy] [-t int] -f logfile

access_log Parse Replay v1.0.0 by toby

optional arguments:
  -h, --help            show this help message and exit
  -p proxy, --proxy proxy
                        send requests to server PROXY
  -t int, --thread int  Thread nums (default 10)
  -f logfile, --file logfile
                        access log file
example:
    python main.py -f .\20230218.asclog
```