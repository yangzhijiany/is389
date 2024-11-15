import os

from openai import OpenAI
client = OpenAI(base_url="http://localhost:2536/v1", api_key="lm-studio")
context_globe: str = ""

#----------------------------------------#
CONVERSATION_FILE = 'conversation.txt'

if os.path.exists(CONVERSATION_FILE):
    with open(CONVERSATION_FILE, 'r', encoding='utf-8') as file:
        context_globe = file.read()
else:
    context_globe = ""
#----------------------------------------#

def get_response(context: str, question: str, input_list: list) -> str:
    global context_globe
    context = context_globe
    input_list.append({"role": "user", "content": question})
    try:
        # 调用AI模型生成回复
        completion = client.chat.completions.create(
            model="local-model",
            messages=input_list,
            temperature=1.4,
        )
        response = completion.choices[0].message.content
        input_list.append({"role": "assistant", "content": response})
        context_globe += f"\nUser: {question}\nchatbot: {response}"

        with open(CONVERSATION_FILE, 'a', encoding='utf-8') as file:
            file.write(f"{question}\n{response}\n")

        return response
    except Exception as e:
        return "sryyy"


def handle_conversation():
    context = ""
    print("Welcome to the AI Chatbot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("bye！")
            break

        # 获取AI生成的回复
        response = get_response(context, user_input)
        print("chatbot: ", response)

        # 更新对话历史记录
        context += f"\nUser: {user_input}\nchatbot: {response}"



if __name__ == "__main__":
    handle_conversation()