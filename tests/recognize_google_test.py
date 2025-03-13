import speech_recognition as sr
import threading
import time
import sys

def listen_and_recognize_stream():
    r = sr.Recognizer()
    
    # 用于存储当前识别的文本
    current_text = {"value": ""}
    
    def update_display():
        """更新显示的线程函数"""
        while True:
            sys.stdout.write(f"\r当前识别: {current_text['value']}")
            sys.stdout.flush()
            time.sleep(0.1)
    
    # 启动显示更新线程
    display_thread = threading.Thread(target=update_display)
    display_thread.daemon = True
    display_thread.start()
    
    print("开始录音，请说话...(按 Ctrl+C 退出)")
    
    with sr.Microphone() as source:
        print("正在调整环境噪声...")
        r.adjust_for_ambient_noise(source, duration=2)
        
        while True:
            try:
                audio = r.listen(source)
                # 使用Google Speech Recognition进行识别
                text = r.recognize_google(audio, language='zh-CN')
                current_text["value"] = text
                print(f"\n识别完成: {text}")
                
            except sr.UnknownValueError:
                current_text["value"] = "无法识别音频"
                print("\n无法识别音频")
            except sr.RequestError as e:
                current_text["value"] = "无法连接到服务"
                print(f"\n无法从Google Speech Recognition服务获取结果; {e}")
            except KeyboardInterrupt:
                print("\n程序结束")
                break
            except Exception as e:
                current_text["value"] = f"错误: {str(e)}"
                print(f"\n发生错误: {e}")

if __name__ == "__main__":
    listen_and_recognize_stream()