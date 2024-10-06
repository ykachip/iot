import socket
import time
import threading
import os
import json

# 1．ソケットを作成する
def open_sock(ip, port):
    # ソケットを作成する(TCP通信用)
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    server_addr = (ip, port)
    sock.bind(server_addr)

    # タイムアウト設定
    sock.settimeout(3)
    # 設定したソケット情報をOSに登録
    CLIENT_NUM = 10
    sock.listen(CLIENT_NUM)
    return sock

# 2．通信を開始する
def start_comm(sock, ip, port):
    global thread_active

    # クライアントのコネクション要求の待ち受け開始
    print("waiting for client connection on " + ip + ":" + str(port))
    while thread_active:
        try:
            # 複数クライアントからの接続を待ち受ける
            sock_cl, addr = sock.accept()

            # 接続してきたクライアントとの通信を開始する（スレッド起動）
            thread = threading.Thread(target=recv_client, args=(sock_cl, addr))
            thread.start()
        except socket.timeout:
            # acceptにタイムアウトが発生した場合
            pass
        except:
            thread_active = False

# TCPデータ受信処理
def recv_client(sock_cl, addr):
    global thread_active

    # 接続要求のあったクライエント情報
    cl_ip = addr[0] # IPアドレス
    cl_port = str(addr[1]) # ポート番号
    print('client connect! from ip('+cl_ip +') port(' + cl_port +')')

    RCV_MSG_SIZE = 2048
    # 受信タイムアウトを設定する
    sock_cl.settimeout(3)

    json_list = []

    # TCPコネクション確立後の受信
    while thread_active:
        try:
            raw_msg = sock_cl.recv(RCV_MSG_SIZE)
            decode_msg = raw_msg.decode(encoding='utf-8')
            if len(decode_msg)>0:
                # 受信したメッセージを出力する
                print(decode_msg)

                # -------------------------------------------

                # 受信した文字列(str型)をJSONデータ形式(dict型)に変換する
                json_data= json.loads(decode_msg)

                # JSONデータに、キー'date'と'status'が含まれている
                if 'date' in json_data and 'status' in json_data:
                    # リストに登録する
                    json_list.append(json_data)

                # -------------------------------------------
            else:
                print("sock_cl.close()")
                thread_active = False         
        except ConnectionResetError:
            thread_active = False
        except socket.timeout:
            # 受信タイムアウトが発生した場合
            pass
        except:
            thread_active = False

    # サブスレッドのsocketを閉じる
    sock_cl.shutdown(socket.SHUT_RDWR)
    sock_cl.close()

    # リストに登録したセンサデータ(Json形式)をファイルに保存する
    save_sensor_file('sensor_data.json', json_list)
            
# 3．ソケットを破棄する
def close_sock(sock):
    if sock is not None:
        sock.close()

# リストデータ（Json形式）をファイルに保存する
def save_sensor_file(file_path, json_list):
    # センサデータ取得
    if len(json_list) > 0:
        try:
            is_file = os.path.isfile(file_path)
            # 同じファイルがすでに存在していた場合
            if is_file:
                # ファイルを削除する
                os.remove(file_path)
                print(f'delete same name file before writing file.')

            # リストデータ(Json形式)をファイルに書き出す
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_list, f, indent=2)

        except:
            print('!! save_sensor_data() Error !!')

    # センサデータの記録件数が0
    else:
        print(f'len(sensor_data_list)=0')


if __name__ == '__main__':

    # 通信ソケットを生成する
    # サーバーで使用するIPアドレスとポート番号を指定
    ip = "192.168.11.100"
    port = 5000

    # 1．ソケットを作成する
    sock = open_sock(ip, port)

    # 2．通信処理を開始する（スレッド起動)
    thread_active = True
    th = threading.Thread(target=start_comm, args=(sock, ip, port))
    th.start()
    
    while thread_active:
        inp = input("press 'q' if you stop\n")
        if inp == 'q':
            thread_active = False
            time.sleep(1)
            break

    # 3．ソケットを閉じる
    close_sock(sock)
