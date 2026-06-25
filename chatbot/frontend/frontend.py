import os
import uuid
import sys
import streamlit as st
from utils import generate_thead_id
from backend.langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# make the project root (chatbot/) importable so `backend` resolves
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thead_id()

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

with st.sidebar:
    st.title("Langgraph Chatbot")
    st.button('New Chat')
    st.header("Conversations")
    st.text(st.session_state['thread_id'])

# load the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input(placeholder="Type here")

if user_input:
    
    # add the user's message to history and show it
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # stream the assistant's reply as a separate (sibling) bubble
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
        
        
