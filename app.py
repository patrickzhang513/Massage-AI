import streamlit as st
import google.generativeai as genai
from datetime import datetime
import csv
import os

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Massage Philosophy Intake",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 视觉系统 (2026-01-11 基准版) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');

    .stApp {
        background-color: #fdfbf7 !important;
        color: #333333 !important;
        font-family: 'Noto Sans SC', sans-serif !important;
    }

    /* 统一标签字号 25px */
    .stTextInput label p, .stSelectbox label p, .stMultiSelect label p, 
    .stTextArea label p, .stCheckbox label p, div[data-testid="stSlider"] label p {
        color: #2c1e1c !important;
        font-weight: 700 !important;
        font-size: 25px !important;
    }

    /* 核心审美：600% 宽度红色巨型按钮 */
    div.stFormSubmitButton > button {
        background-color: #9e2a2b !important;
        color: white !important;
        border: none !important;
        width: 600% !important;   
        height: 150px !important; 
        font-size: 50px !important;
        font-weight: 800 !important;
        position: relative !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        border-radius: 12px !important;
        margin-top: 20px !important;
    }
    div.stFormSubmitButton > button:hover {
        background-color: #7f1d1d !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 基础功能 ---
if 'language' not in st.session_state: st.session_state.language = 'en'
if 'submitted' not in st.session_state: st.session_state.submitted = False

def save_to_csv(data_dict):
    file_name = "client_data.csv"
    file_exists = os.path.isfile(file_name)
    fieldnames = ["Timestamp", "Name", "Email", "Insurance", "Pain_Area", "Pain_Side", "Pain_Level", "Duration", "Pain_Type", "Job", "Sitting_Hours", "Goals", "Notes", "AI_Report"]
    with open(file_name, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists: writer.writeheader()
        writer.writerow(data_dict)

# --- 4. 双语词典 ---
trans = {
    'en': {
        'title': 'Client Intake Form', 'lbl_name': 'Client Name', 'lbl_area': 'Main Pain Area',
        'lbl_level': 'Pain Intensity (0-10)', 'btn_submit': 'SUBMIT', 'loading': 'Processing...',
        'opt_area': ["Neck", "Shoulders", "Upper Back", "Lower Back", "Hips", "Legs"],
        'opt_side': ["Both sides", "Left side", "Right side", "Center"]
    },
    'zh': {
        'title': '客户健康评估表', 'lbl_name': '客户姓名', 'lbl_area': '主要疼痛部位',
        'lbl_level': '疼痛等级 (0-10)', 'btn_submit': '送出', 'loading': '正在分析...',
        'opt_area': ["颈部", "肩部", "上背部", "下腰部", "臀部", "腿部"],
        'opt_side': ["两侧", "左侧", "右侧", "中间"]
    }
}
t = trans[st.session_state.language]

# API 配置
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 5. 界面与表单 ---
st.markdown(f"### {t['title']}")

if not st.session_state.submitted:
    with st.form("main_form"):
        name = st.text_input(t['lbl_
