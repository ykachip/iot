import socket
import threading
import time
import json
import logging

'''
 Tcp_Client Class
'''
class Tcp_Client:
  
  def __init__(self, host_ip="192.168.11.100", host_port=5000, debug=False):
    # Log設定
    formatter = logging.Formatter("%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s: %(message)s")
    handler1 = logging.StreamHandler()
    handler1.setLevel(logging.DEBUG)
    handler1.setFormatter(formatter)
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.DEBUG)
    self.logger.addHandler(handler1)

    self.ip = host_ip
    self.port = host_port
    self.lock = threading.Lock()
    self.M_SIZE = 1024
    
    self.cmd_list = []
    # self.rcv_data_list = []
    self.socket_connect_error_count = 0
    self.com_status = False

    # デバッグモード
    self.debug = debug

  def start_comm(self):
    self.thread_active = True
    self.cl_thread = threading.Thread(target=self.send_loop)
    #self.cl_thread = threading.Thread(target=self.rcv_loop)
    self.cl_thread.start()

  def stop_comm(self):
    self.thread_active = False
    self.com_status = False
    time.sleep(1)

  # 送信メッセージを送信待機リストに登録
  def set_command(self, cmd):
    # TCPコネクションが確立中のとき、送信メッセージをリストに登録する
    # (未確立のときにリストに登録する場合、接続できたときにまとめて送信されてしまうため)
    if self.com_status:
      with self.lock:
        self.cmd_list.append(cmd)

  # 送信待機リストからメッセージを取り出す
  def get_command(self):
    if len(self.cmd_list) > 0:
      with self.lock:
        cmd_str = self.cmd_list[0]
        del self.cmd_list[0]
        return (True, cmd_str)
    else:
      return (False, '')
    
  # TCP送信処理
  def send_loop(self):
    while self.thread_active:
      try:
        self.com_status = False
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #サーバーと接続
        self.socket_connect_error_count +=1
        self.logger.debug(f'sock ---> try-{self.socket_connect_error_count} connect to ip:{self.ip} port:{self.port}')

        self.sock.connect((self.ip, self.port))
        self.logger.debug('sock --> success connect!')

        # # TCPサーバと接続状態（コネクション確立）を設定する
        self.com_status = True
        self.socket_connect_error_count = 0
        
      except Exception as e:
        self.logger.error({e})
        time.sleep(5)
        continue
      
      try:   
        while self.thread_active:
          (result, cmd) = self.get_command()
          if result:
            send_result = self.send_str(self.sock, cmd)
          time.sleep(0.01)

      except KeyboardInterrupt:
        self.thread_active = False
        break
      except ConnectionResetError:
        self.logger.debug('ConnectionResetError')
      except Exception as e:
        self.logger.debug(f'{e}')
    
      # スレッド無効
      self.logger.debug('client ---> thread stop')
      if self.sock is not None:
        try:
          # 送受信の切断
          self.logger.debug('sock.shutdown')
          self.sock.shutdown(socket.SHUT_RDWR)
          # ソケットクローズ
          self.sock.close()
          self.sock = None
        except Exception as e:
          self.logger.debug(f'{e}')

    # ServerとのTCP接続が切断状態であることを設定する
    self.com_status = False

  def send_str(self, sock:socket.socket, strcmd):
      sock.send(strcmd.encode(encoding='utf-8'))
      return True

if __name__ == '__main__':
  
  tcpclient = Tcp_Client(host_ip="192.168.100.177", host_port=5000, debug=True)
  tcpclient.start_comm()
  while tcpclient.thread_active:
      try:
        sinp = input()
        if len(sinp) > 0:
          if sinp == 'q':
            break
        time.sleep(1)
      except KeyboardInterrupt:
        break
  tcpclient.stop_comm()
