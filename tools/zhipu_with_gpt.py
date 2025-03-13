from zhipu_duo_stream import ZhipuDuoChat
from realtime_gpt import RealtimeTTS


class ZhipuGpt():
    def __init__(self, host="192.168.3.6", port="5000", api_key="92c3d906f8ea423693247fa632ff21c2.o2igmox8BfVTwht3"):
        self.realtime_gpt = RealtimeTTS(host, port)
        self.zhipu = ZhipuDuoChat(api_key)

        
    def run(self):
        while True:
            user_input = input("你：")

            if user_input.lower() in ["exit", "退出"]:
                print("对话结束。")
                break
            
            flag, respond = self.zhipu.get_ai_response(user_input)
            if flag:
                print(respond)
                print("正在转换为语音...")
                success = self.realtime_gpt.text_to_speech(respond)
                if success:
                    print("语音播放完成")
                else:
                    print("语音转换失败，请重试")
            else:
                print("获取对话失败，请检查网络问题")

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

if __name__ == "__main__":
    host = get_wlan_ip()
    if host:
        print(f"WLAN IP address: {host}")
    else:
        print("Could not find WLAN IP address")
        
    zhipugpt = ZhipuGpt(host=host)
    zhipugpt.run()