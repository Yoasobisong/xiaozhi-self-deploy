from funasr import AutoModel
import pyaudio
import numpy as np
import threading
import queue
import time

# Model initialization
chunk_size = [0, 10, 5]  # [0, 10, 5] 600ms, [0, 8, 4] 480ms
encoder_chunk_look_back = 4  # number of chunks to lookback for encoder self-attention
decoder_chunk_look_back = 1  # number of encoder chunks to lookback for decoder cross-attention
model_path = "E:/git_repo/xiaozhi-self-deploy/models/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online"
model = AutoModel(model=model_path, device="cuda:0")

# Audio settings
CHUNK = 960 * chunk_size[1]  # Match with model chunk size
FORMAT = pyaudio.paFloat32  # FunASR expects float32
CHANNELS = 1
RATE = 16000

class AudioStreamProcessor:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_running = False
        self.p = pyaudio.PyAudio()
        self.cache = {}
        
    def process_audio(self):
        while self.is_running:
            if not self.audio_queue.empty():
                audio_chunk = self.audio_queue.get()
                
                # Process with FunASR
                res = model.generate(
                    input=audio_chunk,
                    cache=self.cache,
                    is_final=False,
                    chunk_size=chunk_size,
                    encoder_chunk_look_back=encoder_chunk_look_back,
                    decoder_chunk_look_back=decoder_chunk_look_back
                )
                
                if res and res[0]:  # Only print non-empty results
                    print(res[0], end='', flush=True)

    def audio_callback(self, in_data, frame_count, time_info, status):
        # Convert binary data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)

    def start_streaming(self):
        self.is_running = True
        
        # Start processing thread
        process_thread = threading.Thread(target=self.process_audio)
        process_thread.start()

        # Start audio stream
        stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.audio_callback
        )

        print("开始录音和实时识别 (按Ctrl+C停止)...")
        
        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n停止录音和识别...")
            self.is_running = False
            stream.stop_stream()
            stream.close()
            process_thread.join()
            self.p.terminate()

            # Final recognition with is_final=True
            if self.audio_queue.qsize() > 0:
                last_chunk = self.audio_queue.get()
                res = model.generate(
                    input=last_chunk,
                    cache=self.cache,
                    is_final=True,
                    chunk_size=chunk_size,
                    encoder_chunk_look_back=encoder_chunk_look_back,
                    decoder_chunk_look_back=decoder_chunk_look_back
                )
                if res and res[0]:
                    print("\n最终识别结果:", res[0])

if __name__ == "__main__":
    processor = AudioStreamProcessor()
    processor.start_streaming()