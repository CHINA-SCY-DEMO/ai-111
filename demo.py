import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import os

class ChatHistory:
    def __init__(self):
        self.messages = []
        self.load_history()
    
    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.messages.append(message)
        self.save_history()
    
    def load_history(self):
        try:
            with open('chat_history.json', 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
        except FileNotFoundError:
            self.messages = []
    
    def save_history(self):
        with open('chat_history.json', 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
    
    def get_messages(self):
        return self.messages

# 页面配置
st.set_page_config(
    page_title="AI助手",
    page_icon="🤖",
    layout="wide"
)

# 初始化会话状态
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = ChatHistory()
if 'client' not in st.session_state:
    st.session_state.client = OpenAI(
        api_key="sk-19da2bc022d2471081acf16f6fc49054",
        base_url="https://api.deepseek.com"
    )

# 标题
st.title("🤖 AI助手")

# 侧边栏
with st.sidebar:
    st.header("操作")
    if st.button("清除历史对话"):
        st.session_state.chat_history.messages = []
        st.session_state.chat_history.save_history()
        st.rerun()

# 显示聊天历史
for message in st.session_state.chat_history.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 用户输入
if prompt := st.chat_input("在这里输入您的问题..."):
    # 添加用户消息
    st.session_state.chat_history.add_message("user", prompt)
    
    # 显示用户消息
    with st.chat_message("user"):
        st.write(prompt)
    
    try:
        # 显示AI思考状态
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                # 发送请求
                response = st.session_state.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=st.session_state.chat_history.get_messages(),
                    stream=False
                )
                
                # 获取回答
                ai_response = response.choices[0].message.content
                
                # 保存AI回答
                st.session_state.chat_history.add_message("assistant", ai_response)
                
                # 显示AI回答
                st.write(ai_response)
                
    except Exception as e:
        st.error(f"发生错误: {str(e)}")
        st.session_state.chat_history.messages.pop()  # 移除最后添加的用户消息