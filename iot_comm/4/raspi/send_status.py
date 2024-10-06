import RPi.GPIO as GPIO
from time import sleep

import datetime
import client
import json
import logging


gpio_high = False

# Log設定
formatter = logging.Formatter("%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s: %(message)s")
handler1 = logging.StreamHandler()
handler1.setLevel(logging.DEBUG)
handler1.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler1)


def send_gpio_status(client, log):
    now = datetime.datetime.now()
    timestr = now.strftime('[%m/%d %H:%M:%S] ')
    client.set_command(timestr+log)

def main():

    # GPIOのモード設定
    GPIO.setmode(GPIO.BCM)

    # GPIO OUT
    LED_OUT=23
    GPIO.setup(LED_OUT, GPIO.OUT)

    # GPIO INPUT
    SW_INPUT = 24
    GPIO.setup(SW_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # TCP通信 クライアント設定
    tcpclient = client.Tcp_Client(host_ip="192.168.11.100", host_port=5000, debug=True)
    tcpclient.start_comm()

    # JSON形式のデータ
    sensor_data = {
            "date": '',
            "status": False,
    }

    # GPIO INPUT値
    status = False

    try:
        while True:

            # GPIO INPUT値を取得する
            sw_status = GPIO.input(SW_INPUT)

            # INPUT値: HIGH
            if sw_status == GPIO.HIGH:
                
                # ステータスを設定
                status = True

                # LEDを点灯させる
                GPIO.output(LED_OUT,GPIO.HIGH)
                logger.debug("Switch status is HIGH")

            # INPUT値: LOW
            else:
                # ステータスを設定
                status = False
                
                # LEDを消灯させる
                GPIO.output(LED_OUT, GPIO.LOW)
                logger.debug("Switch status is LOW")

             # JSONデータを設定
            dt = datetime.datetime.now()
            sensor_data['date'] = datetime.datetime.strftime(dt, '%Y-%m-%d %H:%M:%S')
            sensor_data['status'] = status

            # JSONデータを文字列に変換する
            json_str = json.dumps(sensor_data)

            # TCP送信データとしてセットする
            tcpclient.set_command(json_str)

            # 間隔をあける
            sleep(1)

    except KeyboardInterrupt:
        pass

    # TCP通信を終了する
    tcpclient.stop_comm()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
    


    
