import uuid
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

class TitleModel(BaseModel):
    title: str = Field(...,description="Title of the user input")

model = ChatOpenAI(model='gpt-4o-mini')
str_model = model.with_structured_output(TitleModel)

# for creating dynamic thread id
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    st.session_state['thread_id'] = generate_thread_id()
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
    
def give_meaningful_title(user_input):
    prompt = f"You are given an input {user_input} which is a question. You have to understand the question and give a title to that question"
    title = str_model.invoke(prompt).title
    return title
    