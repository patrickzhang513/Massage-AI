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

# --- 2. 核心 CSS 优化 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif !important;
        background-color: #fcfbf9;
        color: #000000 !important;
    }

    /* 顶部紧凑化 */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }
    
    /* 标题美化 */
    .stTextInput label, .stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label, .stTextArea label, .stCheckbox label {
        color: #2c1e1c !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        margin-bottom: 4px !important;
    }
    
    /* 隐私小字样式 */
    .privacy-text {
        font-size: 0.8rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 10px;
        font-style: italic;
    }

    /* 输入框优化 */
    input, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 4px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border-color: #d0d0d0 !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #ffffff !important;
    }
    li[role="option"] {
        color: #000000 !important;
    }

    /* 按钮样式 */
    div.stButton > button {
        background-color: transparent !important;
        color: #999 !important;
        border: none !important;
        font-size: 12px !important;
    }
    div.stButton > button:hover {
        color: #9e2a2b !important;
    }

    /* 提交按钮 (红色) */
    div.stFormSubmitButton > button {
        background-color: #9e2a2b !important;
        color: white !important;
        border: none !important;
        padding: 12px 0px !important;
        width: 100% !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        margin-top: 5px !important;
        box-shadow: 0 4px 6px rgba(158, 42, 43, 0.2);
    }
    div.stFormSubmitButton > button:hover {
        background-color: #7f1d1d !important;
        box-shadow: 0 6px 8px rgba(158, 42, 43, 0.3);
    }
    
    /* 下一位按钮 (绿色) - 特殊处理 */
    .new-client-btn button {
        background-color: #2e7d32 !important;
        color: white !important;
        margin-top: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'submitted' not in st.session_state:
    st.session_state.submitted = False # 记录是否提交过

def toggle_language():
    st.session_state.language = 'zh' if st.session_state.language == 'en' else 'en'

def reset_app():
    # 重置所有状态，相当于刷新页面
    st.session_state.submitted = False
    st.rerun()

# 翻译字典 (带图标)
trans = {
    'en': {
        'lang_btn': 'Switch to 中文',
        'title': 'Client Intake Form',
        'subtitle': 'Please complete prior to treatment',
        'lbl_name': '👤 Client Name',
        'lbl_email': '📧 Email Address',
        'privacy': '🔒 Your details are secure and strictly confidential.',
        'lbl_area': '🦴 Main Pain Area',
        'lbl_side': '↔️ Which side?',
        'lbl_duration': '⏱️ How long?',
        'lbl_desc': '⚡ Pain Sensation',
        'lbl_level': '📊 Intensity (0-10)',
        'lbl_job': '💼 Daily Activity',
        'lbl_sit': '🪑 Sitting Hours',
        'lbl_goal': '🎯 Treatment Goal',
        'lbl_note': '📝 Notes / Medical History',
        'lbl_consent': '✅ I acknowledge the information is accurate and consent to treatment.',
        'btn_submit': 'Submit Assessment',
        'loading': '🤖 AI Specialist is analyzing muscle structure...',
        'success': 'Assessment Complete!',
        'result_title': 'Clinical Analysis',
        'btn_new': 'Start New Client (Reset)',
        # Options
        'opt_area': ["Neck", "Shoulders", "Upper Back", "Lower Back", "Hips", "Legs", "Knees", "Feet", "Head", "Arms"],
        'opt_side': ["Both sides", "Left side", "Right side", "Center"],
        'opt_dur': ["< 24 hours (Acute)", "1 week", "1 month", "> 3 months (Chronic)"],
        'opt_desc': ["Sharp", "Dull/Aching", "Stiff", "Numb/Tingling", "Burning"],
        'opt_job': ["Desk Job", "Standing Job", "Physical Labor", "Athlete", "Retired"],
        'opt_goal': ["Pain Relief", "Relaxation", "Better Sleep", "Deep Tissue Release"]
    },
    'zh': {
        'lang_btn': 'Switch to English',
        'title': '客户健康评估表',
        'subtitle': '理疗前请填写 (约2分钟)',
        'lbl_name': '👤 客户姓名',
        'lbl_email': '📧 电子邮箱',
        'privacy': '🔒 您的信息将被严格保密，仅用于理疗档案。',
        'lbl_area': '🦴 主要疼痛部位',
        'lbl_side': '↔️ 侧别',
        'lbl_duration': '⏱️ 持续时间',
        'lbl_desc': '⚡ 疼痛感觉',
        'lbl_level': '📊 疼痛等级 (0-10)',
        'lbl_job': '💼 日常活动/职业',
        'lbl_sit': '🪑 每天久坐',
        'lbl_goal': '🎯 治疗目标',
        'lbl_note': '📝 备注 / 病史',
        'lbl_consent': '✅ 我确认以上信息属实并同意进行理疗。',
        'btn_submit': '送出评估',
        'loading': '🤖 AI 专家正在分析肌肉结构...',
        'success': '评估已生成！',
        'result_title': 'AI 诊断报告',
        'btn_new': '接待下一位 (重置)',
        # Options
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

# --- 4. 界面布局 ---

col_logo, col_btn = st.columns([5, 2])
with col_logo:
    try:
        st.image("logo.png", width=280)
    except:
        st.markdown("## Massage Philosophy")
with col_btn:
    st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
    if st.button(t['lang_btn']): 
        toggle_language()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"### {t['title']}")
st.caption(t['subtitle'])

# --- 表单逻辑 (如果是新客人，显示表单；如果提交了，显示结果) ---

if not st.session_state.submitted:
    with st.form("main_form"):
        col_basic1, col_basic2 = st.columns(2)
        with col_basic1:
            name = st.text_input(t['lbl_name'])
        with col_basic2:
            email = st.text_input(t['lbl_email'])
        
        # 隐私小字
        st.markdown(f"<p class='privacy-text'>{t['privacy']}</p>", unsafe_allow_html=True)
        
        pain_area = st.multiselect(t['lbl_area'], t['opt_area'])
        
        col1, col2 = st.columns(2)
        with col1:
            pain_side = st.selectbox(t['lbl_side'], t['opt_side'])
        with col2:
            duration = st.selectbox(t['lbl_duration'], t['opt_dur'])
            
        pain_desc = st.multiselect(t['lbl_desc'], t['opt_desc'])
        pain_level = st.slider(t['lbl_level'], 0, 10, 5)
        
        col3, col4 = st.columns(2)
        with col3:
            activity = st.selectbox(t['lbl_job'], t['opt_job'])
        with col4:
            sitting = st.select_slider(t['lbl_sit'], options=["<2h", "2-4h", "4-8h", "8h+"])
        
        goals = st.multiselect(t['lbl_goal'], t['opt_goal'])
        notes = st.text_area(t['lbl_note'], height=80)
        
        st.markdown("---")
        # 法律免责勾选
        consent = st.checkbox(t['lbl_consent'])
        
        submitted = st.form_submit_button(t['btn_submit'])
        
        if submitted:
            if not consent:
                st.warning("⚠️ Please agree to the consent checkbox. / 请勾选同意条款。")
            elif not name or not pain_area:
                st.warning("⚠️ Please fill in Name and Pain Area.")
            else:
                # 触发 AI 分析
                with st.spinner(t['loading']):
                    client_data = f"""
                    Name: {name} | Email: {email}
                    Pain: {', '.join(pain_area)} ({pain_side})
                    Level: {pain_level}/10 | Type: {', '.join(pain_desc)}
                    History: {duration}
                    Lifestyle: {activity}, Sit {sitting}
                    Goal: {', '.join(goals)}
                    Note: {notes}
                    Language Mode: {st.session_state.language}
                    """
                    
                    prompt = f"""
                    Role: Massage Philosophy AI Backend System.
                    Data: {client_data}
                    Output: Bilingual Client Report (English & Chinese).
                    Structure:
                    1. [Admin Summary] (English) - Risk factors & Session Recommendation (60/90min).
                    2. [Client Report] (Bilingual) - Anatomical explanation & Plan.
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        st.session_state.ai_result = response.text
                        st.session_state.submitted = True # 标记为已提交，刷新界面
                        st.rerun() # 强制刷新以隐藏表单
                    except Exception as e:
                        st.error(f"Error: {e}")

else:
    # --- 结果展示界面 (表单消失，只看报告) ---
    st.success(t['success'])
    
    st.markdown(f"### 🖥️ {t['result_title']}")
    st.markdown("""
    <div style="background-color:white; padding:25px; border-left:5px solid #9e2a2b; box-shadow:0 4px 15px rgba(0,0,0,0.05); border-radius: 8px;">
    """, unsafe_allow_html=True)
    st.markdown(st.session_state.ai_result)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 接待下一位按钮 (Green)
    # 我们用 columns 让它居中一点
    col_reset_L, col_reset_M, col_reset_R = st.columns([1, 2, 1])
    with col_reset_M:
        if st.button(t['btn_new'], type="primary"):
            reset_app()
