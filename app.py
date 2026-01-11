import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Massage Philosophy Intake",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 视觉系统：V11 经典平衡版 (Benchmark) ---
st.markdown("""
    <style>
    /* 引入 Lato 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

    /* 1. 全局配置 */
    .stApp {
        background-color: #fdfbf7 !important;
        color: #333333 !important;
        font-family: 'Lato', sans-serif !important;
    }

    /* 2. 统一所有标题 (包括输入框、下拉框、滑块、多选框) */
    .stTextInput label, .stSelectbox label, .stMultiSelect label, 
    .stTextArea label, .stCheckbox label, 
    /* 特别修复：滑块的标题 */
    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] p {
        color: #2c1e1c !important; /* 深褐色，比纯黑更有质感 */
        font-size: 1.5rem !important; /* 24px */
        font-weight: 700 !important;
        margin-bottom: 10px !important;
        line-height: 1.5 !important;
        font-family: 'Lato', sans-serif !important;
    }

    /* 3. 深度修复输入框 (多选框变黑、白色长方形问题) */
    
    /* 强制所有输入容器背景为白 */
    .stMultiSelect div[data-baseweb="select"], 
    .stSelectbox div[data-baseweb="select"],
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border-radius: 6px !important;
        border: 2px solid #d1d1d1 !important;
        color: #333 !important;
    }
    
    /* 消除内部的"深色"和"白色长方形" - (注意：这在深色模式下可能会导致栏位隐形) */
    .stMultiSelect div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: transparent !important; /* 让它透出外面的白色 */
        border: none !important;
        color: #333 !important;
    }
    
    /* 修复选项标签的颜色 (选中的药丸) */
    .stMultiSelect div[data-baseweb="tag"] {
        background-color: #f0f0f0 !important;
        border: 1px solid #ccc !important;
    }
    .stMultiSelect div[data-baseweb="tag"] span {
        color: #333 !important;
    }

    /* 聚焦时变红 */
    .stMultiSelect div[data-baseweb="select"]:focus-within,
    .stSelectbox div[data-baseweb="select"]:focus-within,
    div[data-baseweb="input"]:focus-within {
        border-color: #9e2a2b !important;
        box-shadow: 0 0 0 1px #9e2a2b !important;
    }

    /* 4. 滑块 (Slider) 颜色与样式修复 */
    
    /* 滑块轨道 - 已填充部分 (左边) */
    div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
        background-color: #9e2a2b !important; /* 鲜艳品牌红 */
    }
    /* 滑块本身 (圆点) */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #9e2a2b !important;
        box-shadow: 0 0 5px rgba(0,0,0,0.2) !important;
    }
    /* 滑块下方的数字 */
    div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
        color: #9e2a2b !important;
        font-size: 1.2
