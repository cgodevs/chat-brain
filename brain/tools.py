from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def get_ai_message(message):
    gpt4o_chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    msg = HumanMessage(content=message)
    ai_message = gpt4o_chat.invoke([msg])
    print(ai_message.content)
    return ai_message.content

