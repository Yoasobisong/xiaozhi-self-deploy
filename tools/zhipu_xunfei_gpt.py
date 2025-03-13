from zhipu_duo_stream import ZhipuDuoChat
from realtime_gpt import RealtimeTTS
from xunfei import Client
import threading
import time

class ZhipuGpt():
    def __init__(self, host="192.168.233.71", port="5000", zhipu_api_key="92c3d906f8ea423693247fa632ff21c2.o2igmox8BfVTwht3", app_id="775ba7b7", api_key="13a2db4ce53ab219508f97176b4a4a04"):
        self.realtime_gpt = RealtimeTTS(host, port)
        self.zhipu = ZhipuDuoChat(zhipu_api_key)
        self.xunfei = Client(app_id, api_key)
        self.xunfei_thread = threading.Thread(target=self._get_voice).start()
        # time.sleep(9)
        # print("strat")
        
    def _get_voice(self):
        self.xunfei.start_recording()
        
    def run(self):
        try:
            while True:
                # print(self.xunfei.words)
                if self.xunfei.words != "" and self.xunfei.words != None:
                    user_input = self.xunfei.words
                    
                else:
                    user_input = ""
                if user_input != "":
                    flag, respond = self.zhipu.get_ai_response(user_input)
                    if flag:
                        # print(respond)
                        print("正在转换为语音...")
                        success = self.realtime_gpt.text_to_speech(respond)
                        if success:
                            # self.xunfei.words = ""
                            print("语音播放完成, 下一句对话")
                            user_input = ""
                            self.xunfei.words = ""
                        else:
                            print("语音转换失败，请重试")
                            self.xunfei.words = ""
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n程序已退出")
            # self.xunfei.run = False
            self.xunfei.close()

if __name__ == "__main__":
    def get_wlan_ip():
        try:
            import subprocess
            # Run ipconfig command and get output
            output = subprocess.check_output('ipconfig', shell=True).decode('gbk')
            
            # Find WLAN section
            wlan_section = output[output.find('无线局域网适配器 WLAN:'):]
            wlan_section = wlan_section[:wlan_section.find('\n\n')]
            
            # Find IPv4 address
            for line in wlan_section.split('\n'):
                if 'IPv4 地址' in line:
                    return line.split(': ')[-1].strip()
            return None
        except Exception as e:
            print(f"Error getting WLAN IP: {e}")
            return None
            
    host = get_wlan_ip()
    if host:
        print(f"WLAN IP address: {host}")
    else:
        print("Could not find WLAN IP address")

    zhipugpt = ZhipuGpt(host=host)
    zhipugpt.run()