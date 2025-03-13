import whisper
import sys
import torch
import time
print(torch.cuda.is_available())  # 应该输出 True
print(torch.version.cuda)  # 应该输出 11.8

try:
    # Load model with CPU device and int8 quantization
    whisper_model = whisper.load_model("tiny", device="cuda:0")
    for i in range(10):
        t1 = time.time()
        result = whisper_model.transcribe(
            r"E:\git_repo\xiaozhi-self-deploy\library\GPT-SoVITS-beta0706\voice\xiaohe.mp3",
            initial_prompt="以下是普通话的句子。",
        )
        print(f"times{i}: {time.time()-t1}")
        print(" , ".join([i["text"] for i in result["segments"] if i is not None]))
except Exception as e:
    print(f"Error occurred: {str(e)}")
    sys.exit(1)