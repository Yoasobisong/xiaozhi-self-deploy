import requests
import urllib.parse
import pyaudio
import wave
import io
import time

def play_audio_stream(audio_data):
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

def text_to_speech(text):
    """
    Convert text to speech using the provided API
    """
    # Base URL and parameters
    base_url = "http://192.168.3.6:9880/"
    refer_wav_path = "E:/git_repo/xiaozhi-self-deploy/library/GPT-SoVITS-beta0706/output/xiaohe/denoise_opt/xiaohe.mp3_0000000000_0000123520.wav"
    
    # Prepare parameters
    params = {
        'refer_wav_path': refer_wav_path,
        'prompt_text': "今天天气真是太好了，阳光灿烂，心情超级棒。",
        'prompt_language': '中文',
        'text': text,
        'text_language': '中文'
    }
    
    try:
        # Make request
        response = requests.get(f"{base_url}?{urllib.parse.urlencode(params)}", stream=True)
        response.raise_for_status()
        
        # Get audio data and play directly
        play_audio_stream(response.content)
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def interactive_tts():
    """
    Interactive text-to-speech function
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
            success = text_to_speech(text)
            if success:
                print("语音播放完成")
            else:
                print("语音转换失败，请重试")

if __name__ == "__main__":
    # First install required packages if not already installed
    # pip install requests pyaudio --proxy=127.0.0.1:7890
    interactive_tts() 