import socket
import time

# 1．ソケットを作成する(TCP通信用)
sock = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)

# 2．通信先のサーバーが待機するIPアドレスとポート番号を指定
server_addr = ("127.0.0.1", 5000)
print("connect server..")

# 3．サーバに接続する（接続要求を出す）
sock.connect(server_addr)
print("connected!")

# タイムアウトを設定する
sock.settimeout(1)
RCV_MSG_SIZE = 2048

# 4. コンソール画面で入力した文字列をサーバへ送信する
while True:
    try:
        msg_raw = input("press 'q' if you stop\n")
        if msg_raw == 'q':
            break

        # TCPメッセージを送信する
        msg_encode = msg_raw.encode(encoding='utf-8')
        sock.send(msg_encode)

        # サーバからのメッセージ受信
        raw_msg = sock.recv(RCV_MSG_SIZE)
        decode_msg = raw_msg.decode(encoding='utf-8')
        if len(decode_msg)>0:

            print('受信したデータ:', decode_msg)

    except socket.timeout:
        print('受信タイムアウト発生')
        pass
    except KeyboardInterrupt:
        time.sleep(0.5)
        break
    except ConnectionResetError:
        break

# 5. ソケットを閉じる。
sock.shutdown(socket.SHUT_RDWR)
sock.close()