# -*- encoding:utf-8 -*-
import hashlib
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
import pyaudio
import wave

# reload(sys)
# sys.setdefaultencoding("utf8")
class Client():
    def __init__(self, app_id, api_key):
        # Initialize audio parameters
        self.CHUNK = 1280  # Audio chunk size
        self.FORMAT = pyaudio.paInt16  # Audio format
        self.CHANNELS = 1  # Single channel for microphone
        self.RATE = 16000  # Sample rate
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Initialize websocket connection
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def start_recording(self):
        # Open microphone stream
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        print("* Recording started")
        
        try:
            while True:
                # Read audio chunk from microphone
                data = self.stream.read(self.CHUNK)
                # Send audio data to websocket
                self.ws.send(data)
                time.sleep(0.04)
        except KeyboardInterrupt:
            print("* Recording stopped")
            self.stream.stop_stream()
            self.stream.close()
            self.ws.send(bytes(self.end_tag.encode('utf-8')))
            print("send end tag success")

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    break
                result_dict = json.loads(result)
                
                if result_dict["action"] == "result":
                    # Parse the result data
                    result_data = json.loads(result_dict["data"])
                    sentence_info = result_data["cn"]["st"]
                    result_type = sentence_info.get("type")  # 0-最终结果；1-中间结果
                    
                    # 提取文本
                    text = ""
                    for segment in sentence_info["rt"][0]["ws"]:
                        for word in segment["cw"]:
                            text += word["w"]
                    
                    if result_type == "1":  # 中间结果
                        print(f"\r实时识别: {text}", end="")
                    else:  # 最终结果
                        print(f"\n完整句子: {text}")
                
                if result_dict["action"] == "error":
                    print(f"\n错误信息: {result_dict}")
                    self.ws.close()
                    return
                
        except websocket.WebSocketConnectionClosedException:
            pass

    def close(self):
        self.ws.close()
        self.audio.terminate()


if __name__ == '__main__':
    logging.basicConfig()

    # Install required package
    # pip install pyaudio --proxy=127.0.0.1:7890

    app_id = "775ba7b7"
    api_key = "13a2db4ce53ab219508f97176b4a4a04"

    client = Client(app_id, api_key)
    client.start_recording()
