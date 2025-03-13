from zhipuai import ZhipuAI
import time

class ZhipuDuoChat:
    def __init__(self, api_key, model="charglm-4"):
        # Initialize client and basic settings
        self.client = ZhipuAI(api_key=api_key)
        self.model = model
        self.start_time = time.time()
        self.messages = [
            {"role": "system", "content": "你是一个叫小智的台湾女孩，说话机车，声音好听，习惯简短表达，爱用网络梗。请注意,要像一个人一样说话,请不要回复表情符号、代码、和xml标签。当前时间是:{date_time}，现在我正在和你进行语音聊天，我们开始吧。  如果用户希望结束对话，请在最后说\"拜拜\"或\"再见\"。我是光哥，你的男朋友,注意你回答的标点符号不能有~"}
        ]
        self.dot = [".", ",", "?", "!", "，", "。", "？", "！", ]
    
    def _out(self, content):
        # Check if content contains any punctuation mark
        # Check if character is a punctuation mark
        if any(not c.isalnum() and not c.isspace() for c in content):
            print("/", end="", flush=True)
            return True

        return False

    def get_ai_response(self, user_input):
        # Add user message to history
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            # Get streaming response from API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=True,
            )
            
            print("小智:", end="", flush=True)
            ai_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    # if(self._out(content)):
                    #     print("sure")
                    ai_response += content
            print()  # New line
            
            # Add AI response to history
            self.messages.append({"role": "assistant", "content": ai_response})
            
            # Calculate and display time
            # print(f"使用时间：{time.time() - self.start_time} 秒")
            return True, ai_response
            
        except Exception as e:
            print(f"错误发生：{str(e)}")
            print("请检查API Key或网络连接。")
            return False, ""

    def chat(self):
        while True:
            user_input = input("你：")
            
            if user_input.lower() in ["exit", "退出"]:
                print("对话结束。")
                break
            
            if not self.get_ai_response(user_input):
                break

def main():
    api_key = "92c3d906f8ea423693247fa632ff21c2.o2igmox8BfVTwht3"  # Replace with your API key
    chat_bot = ZhipuDuoChat(api_key)
    chat_bot.chat()

if __name__ == "__main__":
    main() 