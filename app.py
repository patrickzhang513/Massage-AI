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

# --- 2. 视觉系统：保留你的 600% 审美并修正偏移 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
    .stApp { background-color: #fdfbf7 !important; color: #333333 !important; font-family: 'Noto Sans SC', sans-serif !important; }
    
    /* 统一标题字号 25px */
    .stTextInput label p, .stSelectbox label p, .stMultiSelect label p, .stTextArea label p, .stCheckbox label p, 
    div[data-testid="stSlider"] label p, div[data-testid="stWidgetLabel"] p, div[data-testid="stMarkdownContainer"] p {
        color: #2c1e1c !important; font-weight: 700 !important; font-size: 25px !important; line-height: 1.4 !important;
    }

    /* 你的 600% 巨型按钮及其居中补丁 */
    div.stFormSubmitButton > button {
        background-color: #9e2a2b !important; color: white !important; 
        width: 600% !important; height: 150px !important; 
        font-size: 50px !important; font-weight: 800 !important;
        position: relative !important; left: 50% !important; transform: translateX(-50%) !important;
        border-radius: 12px !important; margin-top: 20px !important;
    }
    div.stFormSubmitButton > button:hover { background-color: #7f1d1d !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 核心功能函数 ---
def save_to_csv(data_dict):
    file_name = "client_data.csv"
    file_exists = os.path.isfile(file_name)
    fieldnames = ["Timestamp", "Name", "Email", "Insurance", "Pain_Area", "Pain_Side", "Pain_Level", "Duration", "Pain_Type", "Job", "Sitting_Hours", "Goals", "Notes", "AI_Report"]
    with open(file_name, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists: writer.writeheader()
        writer.writerow(data_dict)

# --- 4. 状态管理与词典 ---
if 'language' not in st.session_state: st.session_state.language = 'en'
if 'submitted' not in st.session_state: st.session_state.submitted = False

def toggle_language():
    st.session_state.language = 'zh' if st.session_state.language == 'en' else 'en'

trans = {
    'en': {
        'lang_btn': 'Switch to 中文', 'title': 'Client Intake Form', 'lbl_name': 'Client Name', 'lbl_email': 'Email',
        'lbl_ins': 'Health Fund', 'privacy': 'Private & Secure.', 'lbl_area': 'Pain Area', 'lbl_side': 'Side',
        'lbl_duration': 'Duration', 'lbl_desc': 'Sensation', 'lbl_level': 'Intensity (0-10)', 'lbl_job': 'Activity',
        'lbl_sit': 'Sitting Hours', 'lbl_goal': 'Goal', 'lbl_note': 'History', 'lbl_consent': 'I consent to treatment.',
        'btn_submit': 'SUBMIT', 'loading': 'Processing...', 'success': 'Success', 'btn_new': 'New Client',
        'opt_area': ["Neck", "Shoulders", "Back", "Hips", "Legs"], 'opt_side': ["Both", "Left", "Right"],
        'opt_dur': ["New", "1wk", "1m", "Long term"], 'opt_desc': ["Sharp", "Dull", "Stiff"],
        'opt_job': ["Desk", "Standing", "Labor"], 'opt_goal': ["Relief", "Relax"]
    },
    'zh': {
        'lang_btn': 'Switch to English', 'title': '客户评估表', 'lbl_name': '姓名', 'lbl_email': '邮箱',
        'lbl_ins': '医保', 'privacy': '保密。', 'lbl_area': '部位', 'lbl_side': '侧别',
        'lbl_duration': '时长', 'lbl_desc': '感觉', 'lbl_level': '等级', 'lbl_job': '职业',
        'lbl_sit': '久坐', 'lbl_goal': '目标', 'lbl_note': '备注', 'lbl_consent': '我同意。',
        'btn_submit': '送出', 'loading': '分析中...', 'success': '完成', 'btn_new': '下一位',
        'opt_area': ["颈", "肩", "背部", "臀部", "腿部"], 'opt_side': ["双侧", "左侧", "右侧"],
        'opt_dur': ["新伤", "一周", "一月", "长期"], 'opt_desc': ["刺痛", "酸痛", "僵硬"],
        'opt_job': ["办公", "久站", "体力"], 'opt_goal': ["止痛", "放松"]
    }
}
t = trans[st.session_state.language]

# API 配置 (已修正模型路径)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Error: {e}"); st.stop()

# --- 5. 界面布局 ---
if st.button(t['lang_btn']): toggle_language(); st.rerun()

if not st.session_state.submitted:
    with st.form("main_form"):
        name = st.text_input(t['lbl_name'])
        email = st.text_input(t['lbl_email'])
        insurance = st.text_input(t['lbl_ins'])
        pain_area = st.multiselect(t['lbl_area'], t['opt_area'])
        pain_side = st.selectbox(t['lbl_side'], t['opt_side'])
        duration = st.selectbox(t['lbl_duration'], t['opt_dur'])
        pain_desc = st.multiselect(t['lbl_desc'], t['opt_desc'])
        pain_level = st.slider(t['lbl_level'], 0, 10, 5)
        activity = st.selectbox(t['lbl_job'], t['opt_job'])
        sitting = st.select_slider(t['lbl_sit'], options=["<2h", "2-4h", "4-8h", "8h+"])
        goals = st.multiselect(t['lbl_goal'], t['opt_goal'])
        notes = st.text_area(t['lbl_note'])
        consent = st.checkbox(t['lbl_consent'])
        
        if st.form_submit_button(t['btn_submit']):
            if not consent: st.warning("Please consent.")
            elif not name or not pain_area: st.warning("Fields missing.")
            else:
                with st.spinner(t['loading']):
                    try:
                        res = model.generate_content(f"Report for {name}, Pain: {pain_area}")
                        save_data = {
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Name": name, "Email": email, "Insurance": insurance,
                            "Pain_Area": ", ".join(pain_area), "Pain_Side": pain_side,
                            "Pain_Level": pain_level, "Duration": duration,
                            "Pain_Type": ", ".join(pain_desc), "Job": activity,
                            "Sitting_Hours": sitting, "Goals": ", ".join(goals),
                            "Notes": notes, "AI_Report": res.text
                        }
                        save_to_csv(save_data)
                        st.session_state.ai_result = res.text
                        st.session_state.submitted = True
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")
else:
    st.success(t['success'])
    st.markdown(st.session_state.ai_result)
    if st.button(t['btn_new']): st.session_state.submitted = False; st.rerun()
