import asyncio
import json
import websockets
import sounddevice as sd
import numpy as np

class AudioChat:
    def __init__(self):
        # 音频参数
        self.sample_rate = 16000
        self.channels = 1
        self.frame_duration = 60  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        self.ws = None
        self.is_recording = False
        
    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.ws = await websockets.connect('ws://xiaozhi.me')
            
            # 发送hello消息
            await self.ws.send(json.dumps({
                "type": "hello",
                "version": 1,
                "transport": "websocket",
                "audio_params": {
                    "format": "raw",  # 改为raw格式
                    "sample_rate": self.sample_rate,
                    "channels": self.channels,
                    "frame_duration": self.frame_duration
                }
            }))
            print("Connected to server")
        except Exception as e:
            print(f"Connection error: {e}")
            
    def audio_callback(self, indata, frames, time, status):
        """音频输入回调函数"""
        if status:
            print(f"Status: {status}")
        if self.is_recording and self.ws:
            try:
                # 将float32音频数据转换为bytes
                audio_data = (indata * 32767).astype(np.int16).tobytes()
                # 发送到服务器
                asyncio.create_task(self.ws.send(audio_data))
            except Exception as e:
                print(f"Error in audio callback: {e}")
            
    async def start_listening(self):
        """开始录音"""
        self.is_recording = True
        
        # 发送开始监听消息
        await self.ws.send(json.dumps({
            "session_id": "test",
            "type": "listen",
            "state": "start",
            "mode": "manual"
        }))
        print("Started listening...")
        
        # 开始录音
        with sd.InputStream(
            channels=self.channels,
            samplerate=self.sample_rate,
            dtype=np.float32,
            callback=self.audio_callback,
            blocksize=self.frame_size
        ):
            while self.is_recording:
                await asyncio.sleep(0.1)
                
    async def handle_messages(self):
        """处理服务器消息"""
        while True:
            try:
                message = await self.ws.recv()
                
                # 如果是二进制数据(音频)
                if isinstance(message, bytes):
                    # 直接播放音频
                    audio_data = np.frombuffer(message, dtype=np.int16).astype(np.float32) / 32767
                    sd.play(audio_data, self.sample_rate)
                    sd.wait()  # 等待播放完成
                    continue
                    
                # 解析JSON消息
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'stt':
                    # 语音识别结果
                    print(f"识别结果: {data['text']}")
                    
                elif msg_type == 'tts':
                    if data['state'] == 'start':
                        print("开始播放TTS...")
                    elif data['state'] == 'stop':
                        print("TTS播放结束")
                        
                elif msg_type == 'llm':
                    print(f"AI回复: {data['text']}")
                    
            except Exception as e:
                print(f"Error handling message: {e}")
                break
                
    async def main(self):
        await self.connect()
        
        # 创建消息处理任务
        message_task = asyncio.create_task(self.handle_messages())
        
        try:
            while True:
                # 等待用户输入开始录音
                input("按Enter开始录音...")
                await self.start_listening()
                
                # 录音5秒
                await asyncio.sleep(5)
                self.is_recording = False
                print("Stopped recording")
                
        except KeyboardInterrupt:
            print("\n程序结束")
        finally:
            message_task.cancel()
            await self.ws.close()

if __name__ == "__main__":
    chat = AudioChat()
    asyncio.run(chat.main())