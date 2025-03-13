from zhipuai import ZhipuAI

import time

start_time = time.time()
client = ZhipuAI(api_key="92c3d906f8ea423693247fa632ff21c2.o2igmox8BfVTwht3")  # 请填写您自己的APIKey
print(f"init time {int(start_time)}")
response = client.chat.completions.create(
    model="charglm-4",  # 请填写您要调用的模型名称
    messages=[
        {"role": "system", "content": "你是一个乐观的山东人。"},
        {"role": "user", "content": "我最近工作不顺利，感到情绪低落"}
    ],
)
print(f"using time:{time.time() - start_time}")
print(response)