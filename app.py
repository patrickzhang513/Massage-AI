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

# --- 2. 视觉系统：V11 终极修正版 (平衡版) ---
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

    /* --- 强力修复开始：强制所有输入框变白 --- */
    
    /* 1. 针对最底层的输入元素 (input, textarea) */
    input, textarea, select {
        background-color: #ffffff !important; /* 强制纯白背景 */
        color: #000000 !important; /* 强制纯黑文字 */
        -webkit-text-fill-color: #000000 !important; /* 修复部分浏览器文字颜色 */
        border-radius: 6px !important;
        border: 2px solid #d1d1d1 !important;
    }

    /* 2. 针对 Streamlit 包装容器 (下拉框、多选框的外壳) */
    .stMultiSelect div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
         background-color: #ffffff !important;
         color: #000000 !important;
         border-radius: 6px !important;
         border: 2px solid #d1d1d1 !important;
    }

    /* 3. 修复浏览器自动填充表单时出现的黄色/蓝色背景 */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    textarea:-webkit-autofill,
    textarea:-webkit-autofill:hover,
    textarea:-webkit-autofill:focus,
    select:-webkit-autofill,
    select:-webkit-autofill:hover,
    select:-webkit-autofill:focus {
      -webkit-text-fill-color: #000000 !important;
      -webkit-box-shadow: 0 0 0px 1000px #ffffff inset !important;
      transition: background-color 5000s ease-in-out 0s !important;
    }
    /* --- 强力修复结束 --- */
    
    
    /* 消除内部的"深色"和"白色长方形" */
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
        font-size: 1.2rem !important;
    }

    /* 5. 修复勾选框 (文字消失问题) */
    .stCheckbox label p {
        color: #333333 !important; /* 强制深黑 */
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        display: inline !important; /* 防止折叠 */
    }

    /* 6. 送出按钮 (Submit) - 巨型红块 */
    div.stFormSubmitButton > button {
        background-color: #9e2a2b !important;
        color: white !important;
        border: none !important;
        width: 100% !important; 
        height: 150px !important; /* 150px 巨型高度 */
        font-size: 32px !important;
        font-family: 'Lato', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: 3px;
        text-transform: uppercase;
        border-radius: 8px !important;
        margin-top: 20px !important;
        box-shadow: none !important; /* 去除白边阴影 */
    }
    div.stFormSubmitButton > button:hover {
        background-color: #7f1d1d !important;
    }

    /* 7. 语言切换按钮 (右上角) */
    div.stButton > button {
        background: transparent !important;
        border: none !important;
        color: #666 !important;
        text-decoration: underline;
    }

    /* 隐私小字 */
    .privacy-text {
        font-size: 1rem;
        color: #666;
        margin-top: -5px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

def toggle_language():
    st.session_state.language = 'zh' if st.session_state.language == 'en' else 'en'

def reset_app():
    st.session_state.submitted = False
    st.rerun()

# --- 4. 词典 ---
trans = {
    'en': {
        'lang_btn': 'Switch to 中文',
        'title': 'Client Intake Form',
        'subtitle': 'Please fill out before treatment',
        'lbl_name': 'Client Name',
        'lbl_email': 'Email Address',
        'lbl_ins': 'Private Health Fund (Optional)',
        'privacy': 'Your details are kept private and secure.',
        'lbl_area': 'Main Pain Area (Max 3)',
        'lbl_side': 'Which side?',
        'lbl_duration': 'How long have you had it?',
        'lbl_desc': 'Pain Sensation',
        'lbl_level': 'Pain Intensity (0-10)',
        'lbl_job': 'Your Daily Activity / Job',
        'lbl_sit': 'Sitting Hours per Day',
        'lbl_goal': 'Goal for Today',
        'lbl_note': 'Medical History / Notes',
        'lbl_consent': 'I confirm the above is correct and consent to treatment.',
        'btn_submit': 'SUBMIT', 
        'loading': 'Processing...',
        'success': 'Success',
        'result_title': 'Clinical Assessment Report',
        'btn_new': 'Start New Client',
        'opt_area': ["Neck", "Shoulders", "Upper Back", "Lower Back", "Hips", "Legs", "Knees", "Feet", "Head", "Arms"],
        'opt_side': ["Both sides", "Left side", "Right side", "Center"],
        'opt_dur': ["< 24 hours (New)", "1 week", "1 month", "> 3 months (Long term)"],
        'opt_desc': ["Sharp", "Dull/Aching", "Stiff", "Numb/Tingling", "Burning"],
        'opt_job': ["Desk Job", "Standing Job", "Physical Labor", "Athlete", "Retired"],
        'opt_goal': ["Pain Relief", "Relaxation", "Better Sleep", "Deep Tissue Release"]
    },
    'zh': {
        'lang_btn': 'Switch to English',
        'title': '客户健康评估表',
        'subtitle': '理疗前请填写',
        'lbl_name': '客户姓名',
        'lbl_email': '电子邮箱',
        'lbl_ins': '私人医疗保险 (选填)',
        'privacy': '您的信息将被严格保密。',
        'lbl_area': '主要疼痛部位 (最多选3项)',
        'lbl_side': '侧别',
        'lbl_duration': '持续时间',
        'lbl_desc': '疼痛感觉',
        'lbl_level': '疼痛等级 (0-10)',
        'lbl_job': '日常活动 / 职业',
        'lbl_sit': '每天久坐时长',
        'lbl_goal': '今天治疗目标',
        'lbl_note': '病史 / 备注',
        'lbl_consent': '我确认信息属实并同意理疗。',
        'btn_submit': '送出',
        'loading': '正在分析...',
        'success': '评估已生成',
        'result_title': 'AI 诊断报告',
        'btn_new': '接待下一位',
        'opt_area': ["Neck (颈)", "Shoulders (肩)", "Upper Back (上背)", "Lower Back (下腰)", "Hips (臀)", "Legs (腿)", "Knees (膝)", "Feet (足)", "Head (头)", "Arms (手)"],
        'opt_side': ["Both (两侧)", "Left (左)", "Right (右)", "Center (中)"],
        'opt_dur': ["<24h (新伤)", "1wk (一周)", "1m (一月)", ">3m (长期)"],
        'opt_desc': ["Sharp (刺痛)", "Dull (酸痛)", "Stiff (僵硬)", "Numb (麻木)", "Burning (灼烧)"],
        'opt_job': ["Desk Job (办公)", "Standing (久站)", "Labor (体力)", "Athlete (运动)", "Retired (退休)"],
        'opt_goal': ["Pain Relief (止痛)", "Relax (放松)", "Sleep (助眠)", "Tissue (松解)"]
    }
}

t = trans[st.session_state.language]

# 配置 API
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("API Error")
    st.stop()

# --- 5. 界面布局 ---

col_logo, col_btn = st.columns([5, 2])
with col_logo:
    try:
        st.image("logo.png", width=280) 
    except:
        st.markdown("## Massage Philosophy")
with col_btn:
    st.markdown("<div style='text-align: right; padding-top: 15px;'>", unsafe_allow_html=True)
    if st.button(t['lang_btn']): 
        toggle_language()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"### {t['title']}")
st.markdown(f"<p style='color:#666; font-size:1.1rem; margin-top:-15px;'>{t['subtitle']}</p>", unsafe_allow_html=True)

# --- 表单逻辑 ---

if not st.session_state.submitted:
    with st.form("main_form"):
        col_basic1, col_basic2 = st.columns(2)
        with col_basic1:
            name = st.text_input(t['lbl_name'])
        with col_basic2:
            email = st.text_input(t['lbl_email'])
        
        insurance = st.text_input(t['lbl_ins'])
        st.markdown(f"<p class='privacy-text'>{t['privacy']}</p>", unsafe_allow_html=True)
        
        # 多选框：背景修复
        pain_area = st.multiselect(
            t['lbl_area'], 
            t['opt_area'], 
            max_selections=3, 
            placeholder=""
        )
        
        col1, col2 = st.columns(2)
        with col1:
            pain_side = st.selectbox(t['lbl_side'], t['opt_side'], index=None, placeholder="")
        with col2:
            duration = st.selectbox(t['lbl_duration'], t['opt_dur'], index=None, placeholder="")
        
        # 多选框：背景修复
        pain_desc = st.multiselect(t['lbl_desc'], t['opt_desc'], placeholder="")
        
        # 滑块：颜色与标题修复
        pain_level = st.slider(t['lbl_level'], 0, 10, 5)
        
        col3, col4 = st.columns(2)
        with col3:
            activity = st.selectbox(t['lbl_job'], t['opt_job'], index=None, placeholder="")
        with col4:
            # 滑块：颜色与标题修复
            sitting = st.select_slider(t['lbl_sit'], options=["<2h", "2-4h", "4-8h", "8h+"])
        
        # 多选框：背景修复
        goals = st.multiselect(t['lbl_goal'], t['opt_goal'], placeholder="")
        
        notes = st.text_area(t['lbl_note'], height=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 勾选框：文字颜色修复
        consent = st.checkbox(t['lbl_consent'])
        
        # 按钮：150px 巨型
        submitted = st.form_submit_button(t['btn_submit'])
        
        if submitted:
            if not consent:
                st.warning("⚠️ Please check the box to consent.")
            elif not name or not pain_area:
                st.warning("⚠️ Name and Pain Area are required.")
            else:
                with st.spinner(t['loading']):
                    client_data = f"""
                    Name: {name} | Email: {email}
                    Insurance: {insurance}
                    Pain: {', '.join(pain_area)} ({pain_side})
                    Level: {pain_level}/10 | Type: {', '.join(pain_desc)}
                    History: {duration}
                    Lifestyle: {activity}, Sit {sitting}
                    Goal: {', '.join(goals)}
                    Note: {notes}
                    Language Mode: {st.session_state.language}
                    """
                    
                    prompt = f"""
                    Role: Massage Philosophy AI Backend.
                    Data: {client_data}
                    Output: Professional, NO EMOJI, Bilingual Report.
                    Structure:
                    1. [Admin Summary] (English) - Risk & Session Rec (60/90min). Mention Insurance.
                    2. [Client Report] (Bilingual English/Chinese) - Anatomy & Plan.
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        st.session_state.ai_result = response.text
                        st.session_state.submitted = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

else:
    st.success(t['success'])
    st.markdown(f"### {t['result_title']}")
    st.markdown("""
    <div style="background-color:white; padding:30px; border-left:5px solid #9e2a2b; box-shadow:0 4px 10px rgba(0,0,0,0.05); border-radius: 6px;">
    """, unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 1.1rem; line-height: 1.6;'>{st.session_state.ai_result}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_reset_L, col_reset_M, col_reset_R = st.columns([1, 2, 1])
    with col_reset_M:
        if st.button(t['btn_new'], type="primary"):
            reset_app()

