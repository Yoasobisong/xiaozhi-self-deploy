import requests
import urllib.parse
import pyaudio
import wave
import io
import time

class RealtimeTTS:
    def __init__(self, host="192.168.3.6", port="5000"):
        """
        Initialize RealtimeTTS with server configuration
        """
        self.base_url = f"http://{host}:{port}/tts"
        self.cha_name = "taimei"
        # self.top_k = 12
        # self.top_p = 0.6
        # self.temperature = 0.7

    def _play_audio_stream(self, audio_data):
        """
        Play audio directly from memory without saving to disk
        """
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open wave file from memory
        with wave.open(io.BytesIO(audio_data), 'rb') as wf:
            # Open stream
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                          channels=wf.getnchannels(),
                          rate=wf.getframerate(),
                          output=True)
            
            # Read data in chunks and play
            chunk_size = 1024
            data = wf.readframes(chunk_size)
            
            while data:
                stream.write(data)
                data = wf.readframes(chunk_size)
                
            # Cleanup
            stream.stop_stream()
            stream.close()
            
        p.terminate()

    def text_to_speech(self, text):
        """
        Convert text to speech using streaming approach
        """
        # Prepare parameters
        params = {
            'text': text,
            'text_language': "中文",
            'cha_name': self.cha_name,
            'stream':"true"
        }
        
        try:
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # Open stream with default settings for real-time playback
            stream = p.open(format=p.get_format_from_width(2),
                           channels=1,
                           rate=32000,
                           output=True)
            
            # Make streaming request
            response = requests.get(f"{self.base_url}?{urllib.parse.urlencode(params)}", 
                                  stream=True)
            response.raise_for_status()
            
            # Stream and play audio data in chunks
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    stream.write(chunk)
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()
            return True
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def start_interactive(self):
        """
        Start interactive text-to-speech session
        """
        print("实时语音阅读系统 (输入 'quit' 退出)")
        print("-" * 50)
        
        while True:
            text = input("\n请输入要阅读的文字: ")
            
            if text.lower() == 'quit':
                print("退出系统")
                break
                
            if text.strip():
                print("正在转换为语音...")
                success = self.text_to_speech(text)
                if success:
                    print("语音播放完成")
                else:
                    print("语音转换失败，请重试")

    def speak(self, text):
        """
        Direct method to convert text to speech without interaction
        """
        print(f"正在转换文本: {text}")
        return self.text_to_speech(text)


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
            
    

def main():
    host = get_wlan_ip()
    if host:
        print(f"WLAN IP address: {host}")
    else:
        print("Could not find WLAN IP address")
        return 
    # Create TTS instance
    tts = RealtimeTTS(host=host)
    # Start interactive session
    tts.start_interactive()


if __name__ == "__main__":
    # First install required packages if not already installed
    # pip install requests pyaudio --proxy=127.0.0.1:7890
    main()
