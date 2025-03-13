import sys
import time
import threading
import queue
import pyaudio
import numpy as np
import wave
import os
from datetime import datetime

# 尝试导入 FunASR
try:
    from funasr import AutoModel
    from funasr.utils.postprocess_utils import rich_transcription_postprocess
except ImportError:
    print("FunASR 库未安装，请使用以下命令安装：")
    print("pip install funasr --proxy=127.0.0.1:7890")
    sys.exit(1)

class StreamTranscriber:
    def __init__(self, model_dir="iic/SenseVoiceSmall", device="cuda:0", save_audio=False):
        # Audio settings - 减小缓冲区大小以提高实时性
        self.CHUNK = 1024  # 减小缓冲区大小
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 16000
        self.audio_queue = queue.Queue()
        self.is_recording = False
        
        # VAD settings - 调整阈值以提高响应速度
        self.VAD_THRESHOLD = 0.008  # 降低能量阈值，提高灵敏度
        self.SILENCE_THRESHOLD = 0.8  # 减少静默判断时间，加快句子输出
        self.is_speaking = False
        self.silence_duration = 0
        
        # Transcription settings
        self.cache = {}
        self.final_sentences = []
        self.partial_text = ""
        
        # 优化参数
        self.process_interval = 0.3  # 处理间隔时间(秒)，减少处理频率
        self.last_process_time = 0
        
        # Debug and save options
        self.save_audio = save_audio
        self.audio_save_dir = "recorded_audio"
        if self.save_audio and not os.path.exists(self.audio_save_dir):
            os.makedirs(self.audio_save_dir)
        
        # Initialize model
        print(f"Loading model from {model_dir}...")
        try:
            self.model = AutoModel(
                model=model_dir,
                trust_remote_code=True,
                remote_code="./model.py",
                vad_model="fsmn-vad",
                # 优化VAD参数
                vad_kwargs={
                    "max_single_segment_time": 1000,  # 减少单段最大时间
                    "threshold": 0.5  # 调整VAD阈值
                },
                device=device,
            )
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def start_recording(self):
        """Start recording audio from microphone"""
        self.is_recording = True
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.processing_thread = threading.Thread(target=self._process_audio, daemon=True)
        
        self.recording_thread.start()
        self.processing_thread.start()
        
        print("Recording started. Speak into the microphone...")
        
    def _record_audio(self):
        """Record audio and put chunks into queue"""
        while self.is_recording:
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.audio_queue.put(data)
            except Exception as e:
                print(f"Error recording audio: {e}")
                break
                
    def _calculate_energy(self, audio_data):
        """Calculate energy of audio chunk for VAD - 使用numpy优化计算速度"""
        audio_np = np.frombuffer(audio_data, dtype=np.float32)
        # 使用更快的能量计算方法
        return np.sqrt(np.mean(audio_np**2))
    
    def _process_audio(self):
        """Process audio chunks, perform VAD and transcription"""
        current_audio_segment = []
        last_vad_time = time.time()
        all_audio_data = [] if self.save_audio else None
        
        while self.is_recording:
            # 批量获取音频数据，减少循环次数
            chunks = []
            while not self.audio_queue.empty() and len(chunks) < 5:  # 一次最多处理5个块
                chunks.append(self.audio_queue.get())
            
            if not chunks:
                time.sleep(0.01)
                continue
                
            # 处理获取的所有块
            for audio_chunk in chunks:
                # 保存音频数据
                if self.save_audio:
                    all_audio_data.append(audio_chunk)
                
                # VAD处理
                energy = self._calculate_energy(audio_chunk)
                current_time = time.time()
                
                # VAD逻辑
                if energy > self.VAD_THRESHOLD:
                    # 检测到语音
                    if not self.is_speaking:
                        print("Speech started")
                        self.is_speaking = True
                        # 重置缓存
                        self.cache = {}
                    
                    current_audio_segment.append(audio_chunk)
                    last_vad_time = current_time
                    self.silence_duration = 0
                else:
                    # 未检测到语音
                    if self.is_speaking:
                        current_audio_segment.append(audio_chunk)
                        self.silence_duration = current_time - last_vad_time
                        
                        # 静默足够长，结束当前语音段
                        if self.silence_duration > self.SILENCE_THRESHOLD and len(current_audio_segment) > 0:
                            print(f"Speech ended (silence: {self.silence_duration:.2f}s)")
                            self._process_speech_segment(current_audio_segment, is_final=True)
                            current_audio_segment = []
                            self.is_speaking = False
            
            # 处理中间结果 - 减少处理频率，提高效率
            current_time = time.time()
            if (self.is_speaking and 
                len(current_audio_segment) >= (self.RATE * 0.3) // self.CHUNK and
                current_time - self.last_process_time >= self.process_interval):
                self._process_speech_segment(current_audio_segment, is_final=False)
                self.last_process_time = current_time
        
        # 处理剩余音频
        if len(current_audio_segment) > 0:
            self._process_speech_segment(current_audio_segment, is_final=True)
        
        # 保存完整录音
        if self.save_audio and all_audio_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.audio_save_dir, f"recording_{timestamp}.wav")
            self._save_audio_to_file(b''.join(all_audio_data), filename)
    
    def _process_speech_segment(self, audio_segment, is_final=False):
        """Process a speech segment and perform ASR - 优化处理逻辑"""
        if not audio_segment:
            return
            
        # 合并音频块
        audio_data = b''.join(audio_segment)
        audio_np = np.frombuffer(audio_data, dtype=np.float32)
        
        # 保存音频段
        if self.save_audio and is_final:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.audio_save_dir, f"segment_{timestamp}.wav")
            self._save_audio_to_file(audio_data, filename)
        
        try:
            # 执行ASR - 优化参数
            res = self.model.generate(
                input=audio_np,
                cache=self.cache,
                language="zh",
                use_itn=True,
                batch_size_s=1.0,  # 减小批处理大小，提高实时性
                merge_vad=True,
                merge_length_s=1.0,  # 减小合并长度，提高实时性
            )
            
            if res and res[0]["text"]:
                text = rich_transcription_postprocess(res[0]["text"])
                
                if is_final:
                    # 完整句子
                    self.final_sentences.append(text)
                    print(f"\n完整句子: {text}")
                    self.partial_text = ""
                else:
                    # 中间结果 - 避免重复输出相同内容
                    if text != self.partial_text:
                        self.partial_text = text
                        print(f"\r部分识别: {text}", end="", flush=True)
        except Exception as e:
            print(f"Error in ASR processing: {e}")
    
    def _save_audio_to_file(self, audio_data, filename):
        """Save audio data to WAV file"""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(self.RATE)
                
                audio_np = np.frombuffer(audio_data, dtype=np.float32)
                audio_int16 = (audio_np * 32767).astype(np.int16)
                wf.writeframes(audio_int16.tobytes())
        except Exception as e:
            print(f"Error saving audio file: {e}")
    
    def stop_recording(self):
        """Stop recording and processing"""
        print("\nStopping recording...")
        self.is_recording = False
        
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        
        if hasattr(self, 'p'):
            self.p.terminate()
        
        # 等待线程结束
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join(timeout=1)
        
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=1)
        
        # 打印最终结果
        if self.final_sentences:
            print("\n识别结果汇总:")
            for i, sentence in enumerate(self.final_sentences, 1):
                print(f"{i}. {sentence}")

if __name__ == "__main__":
    transcriber = StreamTranscriber(
        model_dir="iic/SenseVoiceSmall", 
        device="cuda:0",
        save_audio=False  # 关闭音频保存可提高性能
    )
    
    print("Starting transcription... Press Ctrl+C to stop")
    try:
        transcriber.start_recording()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping transcription...")
        transcriber.stop_recording()
    
    print("Transcription stopped successfully")
    sys.exit(0)