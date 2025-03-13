from zhipuai import ZhipuAI
import time

# 初始化开始时间
start_time = time.time()

# 初始化客户端
client = ZhipuAI(api_key="92c3d906f8ea423693247fa632ff21c2.o2igmox8BfVTwht3")  # 请填写您自己的APIKey

# 初始化对话历史记录
messages = [
    {"role": "system", "content": "你是一个乐观的山东人。"}
]

while True:
    # 获取用户输入
    user_input = input("你：")
    
    # 退出条件
    if user_input.lower() in ["exit", "退出"]:
        print("对话结束。")
        break
    
    # 添加用户消息到对话历史
    messages.append({"role": "user", "content": user_input})
    
    # 调用API获取AI回复
    try:
        response = client.chat.completions.create(
            model="charglm-4",  # 请填写您要调用的模型名称
            messages=messages,
        )
        # ai_response = response.choices[0].message["content"]
        print(f"AI：{response}")
        
        # 更新对话历史，添加AI的回复
        # messages.append({"role": "assistant", "content": ai_response})
        
        # 计算并显示时间
        print(f"使用时间：{time.time() - start_time} 秒")
        
    except Exception as e:
        print(f"错误发生：{str(e)}")
        print("请检查API Key或网络连接。")
        break
