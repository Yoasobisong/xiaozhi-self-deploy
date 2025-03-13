import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
import wave
import pyaudio
import time

class AudioRecorder:
    def __init__(self, save_dir="../voice", max_minutes=20):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.save_dir = save_dir
        self.max_seconds = max_minutes * 60
        
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        self.audio = pyaudio.PyAudio()
        
        # 用于存储音频数据和音量数据
        self.frames = []
        self.volumes = []
        self.timestamps = []
        
    def record(self):
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        wave_file = os.path.join(self.save_dir, f"recording_{timestamp}.wav")
        
        # 打开音频流
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        print("* 开始录音")
        start_time = time.time()
        
        try:
            while True:
                # 检查是否超过最大录音时间
                if time.time() - start_time > self.max_seconds:
                    print("\n* 达到最大录音时长限制")
                    break
                
                # 读取音频数据
                data = stream.read(self.CHUNK)
                self.frames.append(data)
                
                # 计算音量
                audio_data = np.frombuffer(data, dtype=np.int16)
                volume_norm = np.linalg.norm(audio_data) * 10
                self.volumes.append(volume_norm)
                self.timestamps.append(time.time() - start_time)
                
                # 显示录音时间
                elapsed = time.time() - start_time
                print(f"\r录音时间: {int(elapsed)}秒 / {self.max_seconds}秒", end="")
                
        except KeyboardInterrupt:
            print("\n* 录音被手动停止")
        
        print("\n* 录音结束")
        
        # 关闭流
        stream.stop_stream()
        stream.close()
        
        # 保存音频文件
        self._save_audio(wave_file)
        
        # 生成音频分析图
        self._generate_plots(timestamp)
        
        return wave_file
        
    def _save_audio(self, filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print(f"音频已保存: {filename}")
        
    def _generate_plots(self, timestamp):
        # 创建一个包含多个子图的图表
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        # 1. 音量随时间变化图
        ax1.plot(self.timestamps, self.volumes)
        ax1.set_title('音量变化')
        ax1.set_xlabel('时间 (秒)')
        ax1.set_ylabel('音量')
        
        # 2. 音频波形图
        audio_data = np.frombuffer(b''.join(self.frames), dtype=np.int16)
        time_axis = np.arange(len(audio_data)) / self.RATE
        ax2.plot(time_axis, audio_data)
        ax2.set_title('音频波形')
        ax2.set_xlabel('时间 (秒)')
        ax2.set_ylabel('振幅')
        
        # 3. 频谱图
        plt.subplot(313)
        plt.specgram(audio_data, Fs=self.RATE, cmap='viridis')
        plt.title('频谱图')
        plt.xlabel('时间 (秒)')
        plt.ylabel('频率 (Hz)')
        
        # 保存图表
        plot_file = os.path.join(self.save_dir, f"analysis_{timestamp}.png")
        plt.tight_layout()
        plt.savefig(plot_file)
        plt.close()
        print(f"分析图表已保存: {plot_file}")
        
    def close(self):
        self.audio.terminate()

if __name__ == "__main__":
    # 创建录音对象（20分钟限制）
    recorder = AudioRecorder(max_minutes=20)
    
    try:
        # 开始录音
        wave_file = recorder.record()
    finally:
        # 确保正确关闭
        recorder.close()
