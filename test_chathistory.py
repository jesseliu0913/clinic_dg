import openai, os


api_key=os.getenv("OPENAI_API_KEY")
conversation_history = []

def chat_with_gpt(user_input, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=conversation_history
    )

    assistant_message = response['choices'][0]['message']['content']
    conversation_history.append({"role": "assistant", "content": assistant_message})
    print(assistant_message)
    return assistant_message

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    chat_with_gpt(user_input, conversation_history)
