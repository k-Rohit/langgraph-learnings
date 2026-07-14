from langgraph.graph import START, END, StateGraph
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import sqlite3

load_dotenv()

# Define the llm model
chat_model = ChatOpenAI(model='gpt-4o-mini',temperature=0.1)

# define the list of tools
search_tool = DuckDuckGoSearchRun()
tools = [search_tool]
tool_node = ToolNode(tools=tools)
chat_model_with_tools = chat_model.bind_tools(tools=tools)

# define the state - 
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat(state: ChatState) -> ChatState:
    messages = state['messages']
    response = chat_model_with_tools.invoke(messages)
    return {'messages': [response]}

# create a sqllite database - 
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

# define the checkpointer - 
checkpointer = SqliteSaver(conn=conn)

# build the graph -
chat_workflow = StateGraph(ChatState)
chat_workflow.add_node('chat_node',chat)
chat_workflow.add_node('tools',tool_node)

# add the edges -
chat_workflow.add_edge(START, 'chat_node')
chat_workflow.add_conditional_edges('chat_node',tools_condition)
chat_workflow.add_edge('tools','chat_node')
chat_workflow.add_edge('chat_node', END)

chatbot = chat_workflow.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)

# sidebar titles, stored in the same DB as the checkpointer (single source of truth)
conn.execute(
    "CREATE TABLE IF NOT EXISTS thread_titles (thread_id TEXT PRIMARY KEY, title TEXT)"
)
conn.commit()

def set_thread_title(thread_id, title):
    conn.execute(
        "INSERT INTO thread_titles (thread_id, title) VALUES (?, ?) "
        "ON CONFLICT(thread_id) DO UPDATE SET title = excluded.title",
        (thread_id, title),
    )
    conn.commit()

def load_titles():
    rows = conn.execute("SELECT thread_id, title FROM thread_titles").fetchall()
    return {thread_id: title for thread_id, title in rows}