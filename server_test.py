import time

from flask import Flask

app = Flask(__name__)


@app.route('/chrome_record.php', methods=["POST"])
def hello_world():
    time.sleep(3)
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="80")
