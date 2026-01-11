import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="Massage Philosophy Intake",
    page_icon="🌿",
    layout="centered", # 居中布局，适配手机和电脑
    initial_sidebar_state="collapsed"
)

# --- 2. 视觉优化 (CSS 魔法) ---
st.markdown("""
    <style>
    /* 全局背景色 - 米白色 (护眼专业) */
    .stApp {
        background-color: #fcfbf9;
        color: #000000 !important;
    }

    /* --- 字体层级调整 --- */
    
    /* 1. 问题标题 (Label) - 放大、加粗 */
    .stTextInput label, .stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label, .stTextArea label {
        color: #2c1e1c !important; /* 深褐色，比纯黑更有质感 */
        font-size: 1.3rem !important; /* 约 21px，非常清晰 */
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }
    
    /* 2. 选项文字/正文 - 正常大小 */
    .stRadio div, .stMultiSelect div, p, .stSelectbox div {
        color: #000000 !important;
        font-size: 1rem !important; /* 16px */
    }

    /* --- 3. 彻底修复输入框背景色 (改为浅色) --- */
    
    /* 输入框本体 */
    input, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    /* 下拉菜单的选择框 */
    div[data-baseweb="select"] > div {
        background-color: #f0f2f6 !important; /* 浅灰色背景 */
        color: #000000 !important;
        border-color: #d0d0d0 !important;
    }
    
    /* 下拉菜单弹出后的选项列表 (关键修复：防止深色干扰) */
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #ffffff !important;
    }
    li[role="option"] {
        color: #000000 !important;
    }

    /* --- 4. 按钮样式优化 --- */
    
    /* 提交按钮 (大、红、醒目) */
    div.stButton > button[kind="primary"] {
        background-color: #9e2a2b;
        color: white !important;
        border: none;
        padding: 15px 0px;
        width: 100%;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 8px;
        margin-top: 20px;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #7f1d1d;
    }

    /* 语言切换按钮 (极小、透明、不抢戏) */
    div.stButton > button[kind="secondary"] {
        background-color: transparent;
        color: #666666 !important;
        border: 1px solid #ddd;
        font-size: 12px !important;
        padding: 2px 10px;
        height: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 语言状态管理 ---
if 'language' not in st.session_state:
    st.session_state.language = 'en' # 默认英文

def toggle_language():
    if st.session_state.language == 'en':
        st.session_state.language = 'zh'
    else:
        st.session_state.language = 'en'

# 词典
trans = {
    'en': {
        'lang_btn': '中文', # 按钮上显示“去中文”
        'title': 'Client Intake Form',
        'subtitle': 'Estimated time: 2 mins',
        'lbl_name': 'Client Name',
        'lbl_email': 'Email',
        'lbl_area': 'Where is the pain?',
        'lbl_side': 'Which side?',
        'lbl_duration': 'How long have you had this?',
        'lbl_desc': 'How does it feel?',
        'lbl_level': 'Pain Intensity (0-10)',
        'lbl_job': 'Daily Activity / Job',
        'lbl_sit': 'Sitting hours per day',
        'lbl_goal': 'Goal for today',
        'lbl_note': 'Any Notes?',
        'btn_submit': 'Submit / 送出', # 您的要求
        'loading': 'Sending data to AI system...',
        'success': 'Successfully Submitted!',
        'result_title': 'System Analysis Result'
    },
    'zh': {
        'lang_btn': 'English', # 按钮上显示“Go English”
        'title': '客户健康评估表',
        'subtitle': '预计填写时间：2分钟',
        'lbl_name': '客户姓名',
        'lbl_email': '电子邮箱',
        'lbl_area': '主要疼痛部位',
        'lbl_side': '疼痛侧别',
        'lbl_duration': '持续时间',
        'lbl_desc': '疼痛感描述',
        'lbl_level': '疼痛等级 (0-10)',
        'lbl_job': '日常活动/职业',
        'lbl_sit': '每天久坐时长',
        'lbl_goal': '今天治疗的目标',
        'lbl_note': '补充说明',
        'btn_submit': 'Submit / 送出',
        'loading': '正在上传至后台分析...',
        'success': '提交成功！',
        'result_title': '后台系统分析结果'
    }
}

t = trans[st.session_state.language]

# 配置 API
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("后台 API 未连接")
    st.stop()

# --- 4. 界面布局 ---

# 顶部：Logo (大) + 语言按钮 (小)
col_logo, col_btn = st.columns([4, 1])
with col_logo:
    try:
        # width=300 放大Logo
        st.image("logo.png", width=300)
    except:
        st.markdown("## Massage Philosophy")
with col_btn:
    # 这是一个小的次要按钮 (secondary)
    if st.button(t['lang_btn'], kind="secondary"):
        toggle_language()
        st.rerun()

st.markdown(f"### {t['title']}")
st.caption(t['subtitle'])
st.markdown("---")

# 表单区域
with st.form("main_form"):
    
    # 基础信息
    name = st.text_input(t['lbl_name'])
    email = st.text_input(t['lbl_email'])
    
    st.markdown("<br>", unsafe_allow_html=True) # 增加间距
    
    # 疼痛详情
    pain_area = st.multiselect(
        t['lbl_area'],
        ["Neck (颈)", "Shoulders (肩)", "Upper Back (上背)", "Lower Back (下腰)", 
         "Hips (臀)", "Legs (腿)", "Knees (膝)", "Feet (足)", "Head (头)", "Arms (手)"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        pain_side = st.selectbox(t['lbl_side'], ["Both (两侧)", "Left (左)", "Right (右)", "Center (中)"])
    with col2:
        duration = st.selectbox(t['lbl_duration'], ["<24h (新伤)", "1wk (一周)", "1m (一月)", ">3m (长期)"])
        
    st.markdown("<br>", unsafe_allow_html=True)

    # 疼痛特征
    pain_desc = st.multiselect(t['lbl_desc'], ["Sharp (刺痛)", "Dull (酸痛)", "Stiff (僵硬)", "Numb (麻木)"])
    pain_level = st.slider(t['lbl_level'], 0, 10, 5)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 生活习惯
    activity = st.selectbox(t['lbl_job'], ["Desk Job (办公)", "Standing (久站)", "Labor (体力)", "Athlete (运动)"])
    sitting = st.select_slider(t['lbl_sit'], options=["<2h", "2-4h", "4-8h", "8h+"])
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 目标
    goals = st.multiselect(t['lbl_goal'], ["Pain Relief (止痛)", "Relax (放松)", "Sleep (助眠)", "Tissue (松解)"])
    notes = st.text_area(t['lbl_note'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 提交按钮 - 这里是 Submit / 送出
    # type="primary" 会调用上面定义的红色大按钮样式
    submitted = st.form_submit_button(t['btn_submit'], type="primary")

# --- 5. 后台系统处理逻辑 ---
if submitted:
    if not name or not pain_area:
        st.error("⚠️ Incomplete Information / 信息不完整")
    else:
        # 这里模拟数据发送到后台
        with st.spinner(t['loading']):
            
            # 1. 整理数据包 (Payload)
            client_data = f"""
            Name: {name} | Email: {email}
            Pain: {', '.join(pain_area)} ({pain_side})
            Level: {pain_level}/10 | Type: {', '.join(pain_desc)}
            History: {duration}
            Lifestyle: {activity}, Sit {sitting}
            Goal: {', '.join(goals)}
            Note: {notes}
            """
            
            # 2. 调用 AI 内核 (模拟后台分析)
            prompt = f"""
            Role: Massage Philosophy AI Backend System.
            Task: Analyze this intake form and generate a Clinical Plan.
            
            Data: {client_data}
            
            Output:
            Generate a concise, professional report structured as:
            1. [Admin Summary] (For Reception/Therapist)
               - Risk Factors: (e.g. Sedentary)
               - Recommended Session: 60/90min
            2. [Client Handout] (Bilingual)
               - Explain why it hurts.
               - Treatment Plan.
            """
            
            try:
                response = model.generate_content(prompt)
                
                # 3. 显示结果 (这就相当于前台看到的后台反馈)
                st.success(t['success'])
                st.markdown("---")
                st.markdown(f"### 🖥️ {t['result_title']}")
                
                st.markdown("""
                <div style="background-color:white; padding:20px; border-left:5px solid #9e2a2b; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                """, unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.caption("System ID: MP-2024-" + str(datetime.now().strftime("%H%M%S")))
                
            except Exception as e:
                st.error(f"System Error: {e}")
