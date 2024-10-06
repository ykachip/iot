import socket
import time
import threading

# 1．ソケットを作成する
def open_sock(ip, port):
    # ソケットを作成する(TCP通信用)
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    server_addr = (ip, port)
    sock.bind(server_addr)

    # タイムアウト設定
    sock.settimeout(3)
    # 設定したソケット情報をOSに登録
    sock.listen()
    return sock

# 2．通信を開始する
def start_comm(sock, ip, port):
    global thread_active

    # クライアントのコネクション要求の待ち受け開始
    print("waiting for client connection on " + ip + ":" + str(port))
    while thread_active:
        try:
            # １クライアントからの接続を待ち受ける
            sock_cl, addr = sock.accept()

            # 接続してきたクライアントとの通信を開始する
            recv_client(sock_cl, addr)

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

    # TCPコネクション確立後の受信
    while thread_active:
        try:
            raw_msg = sock_cl.recv(RCV_MSG_SIZE)
            decode_msg = raw_msg.decode(encoding='utf-8')
            if len(decode_msg)>0:
                # 受信したメッセージを出力する
                print(decode_msg)

            else:
                print("sock_cl.close()")
                thread_active = False

        #接続リセット異常が発生した場合       
        except ConnectionResetError:
            thread_active = False

        # 受信タイムアウトが発生した場合
        except socket.timeout:
            pass
        except:
            thread_active = False

    # サブスレッドのsocketを閉じる
    sock_cl.shutdown(socket.SHUT_RDWR)
    sock_cl.close()

# 3．ソケットを破棄する
def close_sock(sock):
    if sock is not None:
        sock.close()


if __name__ == '__main__':

    # 通信ソケットを生成する
    # サーバーで使用するIPアドレスとポート番号を指定
    ip = "127.0.0.1"
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
