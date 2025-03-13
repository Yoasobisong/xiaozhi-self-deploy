from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Initialize Ollama with Qwen 2.5 model
llm = Ollama(
    model="qwen2.5",  # Make sure this matches your model name in Ollama
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    temperature=0.7
)

def chat_with_qwen(prompt: str) -> str:
    """
    Function to chat with Qwen 2.5 model
    """
    try:
        # Get response from the model
        response = llm(prompt)
        return response
    except Exception as e:
        return f"Error occurred: {str(e)}"

def main():
    print("开始与 Qwen 2.5 对话 (输入 'quit' 退出)")
    
    while True:
        # Get user input
        user_input = input("\n你: ")
        
        if user_input.lower() == 'quit':
            print("对话结束")
            break
            
        # Get response from the model
        response = chat_with_qwen(user_input)
        print("\nQwen:", response)

if __name__ == "__main__":
    main()
