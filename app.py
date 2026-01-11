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

# --- 2. 视觉系统：V13 终极修复版 (防塌陷/防深色) ---
st.markdown("""
    <style>
    /* 引入 Lato 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap');

    /* 1. 全局强制设置：背景米色 */
    .stApp {
        background-color: #fdfbf7 !important;
        font-family: 'Lato', sans-serif !important;
    }
    
    /* 2. 所有文字强制黑色、加粗 */
    .stApp, p, label, span, div, li {
        color: #000000 !important;
    }

    /* 3. 标题样式 (加大号、加粗、黑色) */
    .stTextInput label, .stSelectbox label, .stMultiSelect label, 
    .stTextArea label, .stCheckbox label, 
    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] p {
        color: #000000 !important; /* 纯黑 */
        font-size: 1.6rem !important; /* 26px */
        font-weight: 800 !important; /* 特粗 */
        margin-bottom: 12px !important;
        line-height: 1.4 !important;
        font-family: 'Lato', sans-serif !important;
    }

    /* 4. 输入框/下拉框 - 核心修复 (解决消失和变黑问题) */
    
    /* (A) 单行输入框 (Name, Email) */
    input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #d1d1d1 !important;
        border-radius: 8px !important;
        min-height: 50px !important; /* 保证高度 */
        font-size: 1.2rem !important;
        padding: 10px !important;
    }
    
    /* (B) 备注栏 (Textarea) */
    textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #d1d1d1 !important;
        border-radius: 8px !important;
    }

    /* (C) 下拉框 & 多选框容器 (解决"消失"的关键) */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important; /* 强制白底 */
        border: 2px solid #d1d1d1 !important; /* 强制边框 */
        border-radius: 8px !important;
        min-height: 50px !important; /* ⚠️ 强制最小高度，防止塌陷成一条线 */
        color: #000000 !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* (D) 修复下拉框里的文字颜色 */
    div[data-baseweb="select"] span {
        color: #000000 !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    /* (E) 修复多选框里的"小药丸" (Tags) */
    div[data-baseweb="tag"] {
        background-color: #e0e0e0 !important;
        border: 1px solid #999 !important;
    }

    /* 5. 修复浏览器自动填充导致的黄色/黑色背景 */
    input:-webkit-autofill, textarea:-webkit-autofill, select:-webkit-autofill {
        -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* 6. 滑块 (Slider) - 红色轨道 */
    div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
        background-color: #9e2a2b !important; 
    }
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #9e2a2b !important;
        width: 28px !important;
        height: 28px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
    }
    
    /* 7. 最后的声明文字 (Checkbox) - 强制黑 */
    div[data-testid="stCheckbox"] label p {
        color: #000000 !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
    }

    /* 8. 送出按钮 (Submit) - 巨型红块 */
    div.stFormSubmitButton > button {
        background-color: #9e2a2b !important;
        color: white !important;
        border: none !important;
        width: 100% !important; 
        height: 150px !important; 
        font-size: 34px !important;
        font-weight: 900 !important;
        font-family: 'Lato', sans-serif !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-radius: 10px !important;
        margin-top: 30px !important;
    }
    div.stFormSubmitButton > button:hover {
        background-color: #7f1d1d !important;
    }

    /* 隐私小字 */
    .privacy-text {
        font-size: 1.1rem;
        color: #555 !important;
        font-weight: 700 !important;
        margin-bottom: 25px;
    }
    
    /* 占位符颜色 (淡一点) */
    ::placeholder {
        color: #aaa !important;
        opacity: 1;
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
st.markdown(f"<p style='margin-top:-15px;'>{t['subtitle']}</p>", unsafe_allow_html=True)

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
        
        # 多选框 (已修复消失问题)
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
        
        pain_desc = st.multiselect(t['lbl_desc'], t['opt_desc'], placeholder="")
        
        # 滑块 (已修复标题为黑色)
        pain_level = st.slider(t['lbl_level'], 0, 10, 5)
        
        col3, col4 = st.columns(2)
        with col3:
            activity = st.selectbox(t['lbl_job'], t['opt_job'], index=None, placeholder="")
        with col4:
            sitting = st.select_slider(t['lbl_sit'], options=["<2h", "2-4h", "4-8h", "8h+"])
        
        goals = st.multiselect(t['lbl_goal'], t['opt_goal'], placeholder="")
        
        notes = st.text_area(t['lbl_note'], height=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 勾选框 (已修复文字颜色)
        consent = st.checkbox(t['lbl_consent'])
        
        # 按钮 (巨型 150px)
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
    st.markdown(f"<div style='font-size: 1.3rem; line-height: 1.6; font-weight: 500;'>{st.session_state.ai_result}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_reset_L, col_reset_M, col_reset_R = st.columns([1, 2, 1])
    with col_reset_M:
        if st.button(t['btn_new'], type="primary"):
            reset_app()
