import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import generate_thread_id, reset_chat, add_thread, give_meaningful_title
from backend.langgraph_backend import chatbot, retrieve_all_threads, load_titles, set_thread_title
from langchain_core.messages import HumanMessage

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

# maps thread_id -> meaningful title (shown in the sidebar), loaded from disk so
# titles survive a restart
if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = load_titles()

add_thread(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']},
          "metadata": {
              "thread_id" : st.session_state["thread_id"]
          },
          "run_name": "chat_turn"
          }

with st.sidebar:
    st.title("Langgraph Chatbot")
    if st.button('New Chat'):
        reset_chat()
        
    st.header("Conversations")

# show newest chats first; label each with its title (fallback while untitled)
for thread in reversed(st.session_state['chat_threads']):
    label = st.session_state['thread_titles'].get(thread, 'New Chat')
    if st.sidebar.button(label, key=thread):
        st.session_state['thread_id'] = thread
        state = chatbot.get_state({'configurable': {'thread_id': thread}})
        msgs = state.values.get('messages', [])
        st.session_state['message_history'] = [
            {'role': 'user' if m.type == 'human' else 'assistant', 'content': m.content}
            for m in msgs
        ]

# load the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input(placeholder="Type here")

if user_input:
    # on the first message of this chat, generate a meaningful title for the sidebar
    current_thread = st.session_state['thread_id']
    if current_thread not in st.session_state['thread_titles']:
        title = give_meaningful_title(user_input)
        st.session_state['thread_titles'][current_thread] = title
        set_thread_title(current_thread, title)

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
        
        
