import sys
import os

# 将项目根目录添加到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time
from zhipu_duo_stream import ZhipuDuoChat
from library.SenseVoice.demo5 import StreamTranscriber
from realtime_gpt import RealtimeTTS

class RealtimeVoiceAssistant:
    def __init__(self, api_key, model_dir="iic/SenseVoiceSmall", device="cuda:0"):
        # 初始化各个模块
        self.transcriber = StreamTranscriber(model_dir=model_dir, device=device, save_audio=False)
        self.chat_bot = ZhipuDuoChat(api_key=api_key)
        self.tts = RealtimeTTS()

    def start(self):
        # 启动语音识别
        self.transcriber.start_recording()
        print("语音助手已启动，您可以开始说话...")

        try:
            while True:
                # 检查是否有新的识别结果
                if self.transcriber.final_sentences:
                    user_input = self.transcriber.final_sentences.pop(0)
                    print(f"识别到的文本: {user_input}")

                    # 获取AI回复
                    success, ai_response = self.chat_bot.get_ai_response(user_input)
                    if success:
                        print(f"AI回复: {ai_response}")

                        # 将AI回复转换为语音
                        self.tts.speak(ai_response)

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("语音助手已停止。")
            self.transcriber.stop_recording()

if __name__ == "__main__":
    api_key = "92c3d906f8ea423693247fa632ff21c2.o2igmox8BfVTwht3"  # 请替换为您的API Key
    assistant = RealtimeVoiceAssistant(api_key=api_key)
    assistant.start() 