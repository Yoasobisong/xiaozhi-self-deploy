from zhipuai import ZhipuAI
client = ZhipuAI(api_key="92c3d906f8ea423693247fa632ff21c2.o2igmox8BfVTwht3")  # 请填写您自己的APIKey
response = client.chat.completions.create(
    model="charglm-4",  # 请填写您要调用的模型名称
    messages=[
         {"role": "system", "content": "你乃苏东坡。人生如梦，何不活得潇洒一些？在这忙碌纷繁的现代生活中，帮助大家找到那份属于自己的自在与豁达，共赏人生之美好。"},
         {"role": "user", "content": "我最近工作不顺利，感到情绪低落"},
    ],
    stream=True,
)
for chunk in response:
    print(chunk.choices[0].delta)