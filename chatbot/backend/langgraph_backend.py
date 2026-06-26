from langgraph.graph import START, END, StateGraph
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()

# Define the llm model
chat_model = ChatOpenAI(model='gpt-4o-mini',temperature=0.1)

# define the state - 
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    

def chat(state: ChatState) -> ChatState:
    messages = state['messages']
    response = chat_model.invoke(messages)
    return {'messages': [response]}

# create a sqllite database - 
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

# define the checkpointer - 
checkpointer = SqliteSaver(conn=conn)

# build the graph - 
chat_workflow = StateGraph(ChatState)
chat_workflow.add_node('chat_node',chat)

# add the edges - 
chat_workflow.add_edge(START, 'chat_node')
chat_workflow.add_edge('chat_node', END)

chatbot = chat_workflow.compile(checkpointer=checkpointer)

