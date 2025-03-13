from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import hmac
import base64
import json
import hashlib
import urllib.parse
import websocket
import threading
import time
import ssl

class XunfeiStreamASR:
    def __init__(self, app_id, api_key, api_secret):
        # 讯飞开放平台的配置
        self.APPID = app_id
        self.APIKey = api_key
        self.APISecret = api_secret
        self.url = "wss://iat-api.xfyun.cn/v2/iat"
        
        self.ws = None
        self.is_running = False
        self.current_text = ""
    
    def _create_url(self):
        # 生成鉴权URL
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        signature_origin = f"host: iat-api.xfyun.cn\ndate: {date}\nGET /v2/iat HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), 
                               signature_origin.encode('utf-8'),
                               digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        params = {
            "authorization": authorization,
            "date": date,
            "host": "iat-api.xfyun.cn"
        }
        return f"{self.url}?{urllib.parse.urlencode(params)}"
    
    def _on_message(self, ws, message):
        try:
            result = json.loads(message)
            if result["code"] != 0:
                print(f"Error: {result['code']}, {result['message']}")
                return
            
            data = result["data"]
            if data["status"] == 2:  # 最后一个结果
                self.current_text = ""
                print()  # 换行
            else:
                for item in data["result"]["ws"]:
                    for w in item["cw"]:
                        self.current_text += w["w"]
                print(f"\r当前识别: {self.current_text}", end="", flush=True)
                
        except Exception as e:
            print(f"\nError in message handling: {str(e)}")
    
    def _on_error(self, ws, error):
        print(f"\nError: {str(error)}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        print("\n连接已关闭")
        self.is_running = False
    
    def _on_open(self, ws):
        def run():
            # 发送开始参数
            data = {
                "common": {"app_id": self.APPID},
                "business": {
                    "language": "zh_cn",
                    "domain": "iat",
                    "accent": "mandarin",
                    "vad_eos": 3000,
                    "dwa": "wpgs"  # 开启实时返回
                },
                "data": {
                    "status": 0,
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw"
                }
            }
            ws.send(json.dumps(data))
        
        threading.Thread(target=run).start()
    
    def start(self):
        websocket.enableTrace(False)
        url = self._create_url()
        self.ws = websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        self.is_running = True
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    def stop(self):
        if self.ws:
            self.ws.close()
        self.is_running = False

if __name__ == "__main__":
    # 替换为你的讯飞开放平台配置
    APP_ID = "your_app_id"
    API_KEY = "your_api_key"
    API_SECRET = "your_api_secret"
    
    asr = XunfeiStreamASR(APP_ID, API_KEY, API_SECRET)
    
    try:
        print("开始语音识别，按Ctrl+C退出...")
        asr.start()
    except KeyboardInterrupt:
        print("\n正在停止...")
        asr.stop() 