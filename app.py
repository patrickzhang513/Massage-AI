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

# --- 2. 视觉系统：V10 终极修复版 ---
st.markdown("""
    <style>
    /* 引入 Lato 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

    /* 1. 全局配置 */
    .stApp {
        background-color: #fdfbf7 !important; /* 米色背景 */
        color: #333333 !important;
        font-family: 'Lato', sans-serif !important;
    }

    /* 2. 标题样式 (大、清晰、深褐) */
    .stTextInput label, .stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label, .stTextArea label, .stCheckbox label {
        color: #2c1e1c !important;
        font-size: 1.5rem !important; /* 24px */
        font-weight: 700 !important;
        margin-bottom: 10px !important;
        line-height: 1.5 !important;
    }

    /* 3. 输入框美化 (修复"白色小长方形"问题) */
    
    /* 基础输入框 */
    input, textarea {
        background-color: #ffffff !important;
        border: 2px solid #d1d1d1 !important;
        border-radius: 6px !important;
        font-size: 1.2rem !important;
        color: #000000 !important;
        padding: 10px !important;
    }
    
    /* 下拉/多选框容器 (关键修复：确保高度饱满，不塌陷) */
    .stMultiSelect > div > div, .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 2px solid #d1d1d1 !important;
        border-radius: 6px !important;
        min-height: 50px !important; /* 强制最小高度，保证美观 */
        color: #000000 !important;
    }
    
    /* 聚焦时边框变红 */
    .stMultiSelect > div > div:focus-within, .stSelectbox > div > div:focus-within, input:focus, textarea:focus {
        border-color: #9e2a2b !important;
        box-shadow: 0 0 0 1px #9e2a2b !important;
    }

    /* 下拉选项文字大小 */
    .stMultiSelect span, .stSelectbox span {
        font-size: 1.2rem !important;
        color: #333 !important;
    }

    /* 4. 滑块 (Slider) 上色修复 (专业红) */
    
    /* 滑块轨道 (Track) */
    div[data-testid="stSlider"] > div > div > div > div {
        background-color: #9e2a2b !important; /* 强制红色 */
        height: 8px !important; /* 加粗一点 */
        border-radius: 4px !important;
    }
    
    /* 滑块圆点 (Thumb) */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #9e2a2b !important;
        border: 2px solid white !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        height: 24px !important; /* 放大圆点 */
        width: 24px !important;
    }
    
    /* 滑块文字数值 */
    div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        color: #9e2a2b !important;
    }

    /* 5. 按钮系统 - 巨型按钮 (跟备注栏一样大) */
    
    /* 语言切换 (右上角) */
    div.stButton > button {
        font-size: 1rem !important;
        color: #666 !important;
        text-decoration: underline;
        background: transparent !important;
        border: none !important;
    }

    /* SUBMIT 按钮 (特别定制) */
    div.stFormSubmitButton > button {
        background-color: #9e2a2b !important; /* 品牌红 */
        color: white !important;
        border: none !important;
        
        /* 尺寸核心设置 */
        width: 100% !important; 
        height: 150px !important; /* ⚠️ 这里设定为150px，跟 text_area 高度一致 */
        
        /* 字体核心设置 */
        font-size: 32px !important; /* 特大号字体 */
        font-family: 'Lato', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: 3px;
        text-transform: uppercase;
        
        border-radius: 8px !important;
        margin-top: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* 悬停效果 (变深红，无白底) */
    div.stFormSubmitButton > button:hover {
        background-color: #7f1d1d !important;
        color: white !important;
    }
    div.stFormSubmitButton > button:active {
        background-color: #5c1515 !important;
        color: white !important;
    }

    /* 6. 隐私小字 */
    .privacy-text {
        font-size: 1rem;
        color: #666;
        margin-top: -5px;
        margin-bottom: 25px;
    }
    
    /* 去除占位符颜色，让空盒子看起来更白 */
    ::placeholder {
        color: transparent !important;
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
        'lbl_area': 'Where is the pain? (Max 3)', # 提示最多选3个
        'lbl_side': 'Which side?',
        'lbl_duration': 'How long have you had it?',
        'lbl_desc': 'What does the pain feel like?',
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
        
        # 核心更新：使用 max_selections=3 限制只能选3个
        pain_area = st.multiselect(
            t['lbl_area'], 
            t['opt_area'], 
            max_selections=3, # 限制3个
            placeholder="" # 保持干净
        )
        
        col1, col2 = st.columns(2)
        with col1:
            pain_side = st.selectbox(t['lbl_side'], t['opt_side'], index=None, placeholder="")
        with col2:
            duration = st.selectbox(t['lbl_duration'], t['opt_dur'], index=None, placeholder="")
            
        pain_desc = st.multiselect(t['lbl_desc'], t['opt_desc'], placeholder="")
        
        # 滑块现在会有颜色了
        pain_level = st.slider(t['lbl_level'], 0, 10, 5)
        
        col3, col4 = st.columns(2)
        with col3:
            activity = st.selectbox(t['lbl_job'], t['opt_job'], index=None, placeholder="")
        with col4:
            sitting = st.select_slider(t['lbl_sit'], options=["<2h", "2-4h", "4-8h", "8h+"])
        
        goals = st.multiselect(t['lbl_goal'], t['opt_goal'], placeholder="")
        
        # 备注栏 - 高度 150px
        notes = st.text_area(t['lbl_note'], height=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        consent = st.checkbox(t['lbl_consent'])
        
        # 提交按钮 - CSS已设定高度为 150px (跟备注一样大)
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
