import streamlit as st
import google.generativeai as genai
from datetime import datetime
import csv  # <--- 新增
import os   # <--- 新增

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Massage Philosophy Intake",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 视觉系统：V16 (终极修复：强制统一所有标签大小) ---
st.markdown("""
    <style>
    /* ============================
       1. 全局字体与颜色
       ============================ */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');

    .stApp {
        background-color: #fdfbf7 !important;
        color: #333333 !important;
        font-family: 'Noto Sans SC', sans-serif !important;
    }

    /* ============================
       2. 万能标题控制区 (Master Label Control)
       ============================ */
    
    /* 👇 这里是核心修改！
       无论它是输入框、滑块、还是勾选框，都会强制执行这里的字号。
    */
    .stTextInput label p,              /* 文本输入框 (姓名/邮箱) */
    .stSelectbox label p,              /* 下拉菜单 */
    .stMultiSelect label p,            /* 多选框 */
    .stTextArea label p,               /* 文本域 (备注) */
    .stCheckbox label p,               /* 勾选框 (确认信息) */
    div[data-testid="stSlider"] label p,            /* 滑块标签 (关键修复) */
    div[data-testid="stWidgetLabel"] p,             /* 万能兜底 (防止漏网之鱼) */
    label[data-testid="stWidgetLabel"] p            /* 另一种结构的兜底 */
    {  
        color: #2c1e1c !important;
        font-family: 'Noto Sans SC', sans-serif !important;
        font-weight: 700 !important;
        
        /* 👇👇👇 在这里调整大小，所有标题会一起变！ 👇👇👇 */
        font-size: 25px !important;  
        /* 👆👆👆 觉得太大就改 20px，觉得太小就改 30px */
        
        line-height: 1.4 !important;
        margin-bottom: 5px !important;
    }

    /* ============================
       3. 页面大标题 (Client Intake Form)
       ============================ */
    h1, h2, h3, h4, h5, h6 {
        color: #2c1e1c !important;
        font-family: 'Noto Sans SC', sans-serif !important;
        font-weight: 700 !important;
        font-size: 40px !important; 
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }

    /* ============================
       4. 组件本体样式 (输入框、按钮等)
       ============================ */
    
    /* 输入框本体 */
    input[type="text"], input[type="email"], textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 4px !important;
        padding: 8px !important;
        font-size: 18px !important; /* 输入的内容字号 */
    }

    /* 下拉/多选框本体 */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #d1d1d1 !important;
        color: #333 !important;
    }

    /* 滑块颜色 */
    div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
        background-color: #9e2a2b !important; 
    }
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #9e2a2b !important;
        box-shadow: 0 0 5px rgba(0,0,0,0.2) !important;
    }
    
    /* 修复滑块下方的刻度数字 (防止它也变大) */
    div[data-testid="stSlider"] div[data-testid="stTickBar"] p {
        font-size: 14px !important; /* 保持刻度小一点 */
        font-weight: 400 !important;
        color: #666 !important;
    }

    /* 送出按钮 */
    div.stFormSubmitButton > button {
        background-color: #9e2a2b !important;
        color: white !important;
        border: none !important;
        width: 600% !important;   
        height: 150px !important; 
        font-size: 50px !important;
        font-family: 'Noto Sans SC', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: 3px;
        text-transform: uppercase;
        border-radius: 12px !important;
        margin-top: 20px !important;
        box-shadow: none !important;
    }
    div.stFormSubmitButton > button:hover {
        background-color: #7f1d1d !important;
    }
    
    /* 语言切换按钮 */
    div.stButton > button {
        background: transparent !important;
        border: none !important;
        color: #666 !important;
        text-decoration: underline;
    }
    
    /* 隐私条款文字 */
    .privacy-text {
        font-size: 16px !important;
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
# --- 保存数据的函数 (新增) ---
def save_to_csv(data_dict):
    file_name = "client_data.csv"
    # 检查文件是否已存在
    file_exists = os.path.isfile(file_name)
    
    # 定义 Excel 表头 (列名)
    fieldnames = [
        "Timestamp", "Name", "Email", "Insurance", 
        "Pain_Area", "Pain_Side", "Pain_Level", 
        "Duration", "Pain_Type", "Job", 
        "Sitting_Hours", "Goals", "Notes", "AI_Report"
    ]
    
    # 打开文件并写入 ('a' 代表 append 追加模式)
    with open(file_name, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # 如果是第一次创建文件，先写入表头
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(data_dict)

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
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"API Setup Error: {e}")
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
        
        # 多选框
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
        
        # 多选框
        pain_desc = st.multiselect(t['lbl_desc'], t['opt_desc'], placeholder="")
        
        # 滑块
        pain_level = st.slider(t['lbl_level'], 0, 10, 5)
        
        col3, col4 = st.columns(2)
        with col3:
            activity = st.selectbox(t['lbl_job'], t['opt_job'], index=None, placeholder="")
        with col4:
            # 滑块
            sitting = st.select_slider(t['lbl_sit'], options=["<2h", "2-4h", "4-8h", "8h+"])
        
        # 多选框
        goals = st.multiselect(t['lbl_goal'], t['opt_goal'], placeholder="")
        
        notes = st.text_area(t['lbl_note'], height=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 勾选框
        consent = st.checkbox(t['lbl_consent'])
        
        # 按钮
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




