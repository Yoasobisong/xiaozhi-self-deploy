import pyaudio
import numpy as np
import whisper

# 加载 Whisper 模型
model = whisper.load_model("base")

def process_audio_data(audio_chunk):
    """
    将音频块数据转换为模型可以处理的格式。
    """
    audio_data = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
    return audio_data

def transcribe_audio(audio_data):
    """
    使用 Whisper 模型对音频数据进行转录。
    """
    result = model.transcribe(audio_data)
    return result['text']

def main():
    # 配置 PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    print("开始实时语音识别...")

    try:
        while True:
            # 读取音频块
            audio_chunk = stream.read(1024)
            
            # 处理音频数据
            audio_data = process_audio_data(audio_chunk)
            
            # 转录音频数据
            text = transcribe_audio(audio_data)
            
            # 输出转录结果
            print(text)

    except KeyboardInterrupt:
        print("\n停止实时语音识别.")
    finally:
        # 关闭音频流
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()