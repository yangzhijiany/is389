import os
import openai
from dotenv import load_dotenv

# 设置 OpenAI 的 API 密钥
load_dotenv()
openai.api_key = os.getenv('openai_api_key')




def get_response(user_input, messages):
    try:

        messages.append({"role": "user", "content": f"User's_input: {user_input}"})

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            temperature=1.3,
            messages=messages,
            max_tokens=200,
            top_p=0.9,
            frequency_penalty=0,
            presence_penalty=0
        )

        ai_response = response["choices"][0]["message"]["content"]

        assistant_reply = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": assistant_reply})
        return ai_response
    except Exception as e:
        # 捕获错误并返回
        return f"出现错误喵: {str(e)}"


# 主循环
def main():
    """
    主循环，管理用户输入和与 Hoshino 的对话。
    """
    print("欢迎来到 Hoshino 聊天机器人！随便聊点什么吧，输入 'exit' 退出喵~")
    # 初始化对话历史
    conversation_history = ""
    while True:
        user_input = input("你: ")
        if user_input.lower() == "exit":
            print("Hoshino: 再见喵~希望你还会回来找我喵！")
            break

        # 调用聊天函数
        response, conversation_history = get_response(user_input, conversation_history)
        # 输出 Hoshino 的回复
        response = get_response(user_input)
        print(f"Hoshino: {response}")
