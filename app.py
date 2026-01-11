import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. 页面配置 (适配移动端) ---
st.set_page_config(
    page_title="Massage Philosophy Intake",
    page_icon="🌿",
    layout="centered", # ⚠️ 关键改动：使用居中布局，手机/电脑通吃
    initial_sidebar_state="collapsed"
)

# --- 2. 强制修复字体颜色 (CSS黑科技) ---
# 这段代码强制所有文字变黑，背景变米色，解决“看不见字”的问题
st.markdown("""
    <style>
    /* 1. 强制全局背景为米色，文字为黑色 */
    .stApp {
        background-color: #fcfbf9;
        color: #000000 !important;
    }
    
    /* 2. 修复输入框标签 (Label) 看不见的问题 */
    .stTextInput label, .stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label, .stTextArea label {
        color: #000000 !important; /* 强制纯黑 */
        font-size: 1.1rem !important; /* 字体加大，方便手机看 */
        font-weight: 600 !important;
    }
    
    /* 3. 修复输入框里面的文字颜色 */
    input, textarea, .stSelectbox div[data-baseweb="select"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    /* 4. 修复多选框/单选框的选项文字 */
    .stRadio div, .stMultiSelect div {
        color: #000000 !important;
    }
    p, span {
        color: #333333 !important;
    }

    /* 5. 按钮样式优化 (易经红) */
    div.stButton > button {
        background-color: #9e2a2b;
        color: white !important;
        border: none;
        padding: 15px 30px; /* 加大按钮热区 */
        width: 100%; /* 手机上按钮占满全宽 */
        font-size: 18px !important;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #7f1d1d;
        color: white !important;
    }
    
    /* 6. 语言切换按钮 (右上角) */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 语言与状态管理 ---
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
        'btn_toggle': '🇨🇳 中文界面', 
        'title': 'Client Intake Form',
        'subtitle': 'Takes 2-3 mins to complete',
        'sec_basic': '1. Basic Information',
        'lbl_name': 'Your Name',
        'lbl_email': 'Email Address',
        'sec_pain': '2. Pain & Symptoms',
        'lbl_area': 'Where is the pain?',
        'lbl_side': 'Which side?',
        'lbl_duration': 'How long?',
        'sec_char': '3. Details',
        'lbl_desc': 'How does it feel?',
        'lbl_level': 'Pain Intensity (0-10)',
        'sec_life': '4. Lifestyle',
        'lbl_job': 'Daily Activity',
        'lbl_sit': 'Sitting Hours',
        'sec_goal': '5. Goal',
        'lbl_goal': 'Goal for today',
        'lbl_note': 'Notes',
        'btn_submit': 'Generate Assessment',
        'err': '⚠️ Name and Pain Area are required.',
        'loading': 'Analyzing...',
        'success': 'Assessment Ready!'
    },
    'zh': {
        'btn_toggle': '🇦🇺 English View',
        'title': '客户健康评估表',
        'subtitle': '填写约需 2-3 分钟',
        'sec_basic': '1. 基础信息',
        'lbl_name': '您的姓名',
        'lbl_email': '电子邮箱',
        'sec_pain': '2. 疼痛与症状',
        'lbl_area': '哪里不舒服？',
        'lbl_side': '左边还是右边？',
        'lbl_duration': '痛了多久？',
        'sec_char': '3. 疼痛细节',
        'lbl_desc': '是什么样的痛感？',
        'lbl_level': '疼痛等级 (0-10)',
        'sec_life': '4. 生活习惯',
        'lbl_job': '日常活动类型',
        'lbl_sit': '每天久坐时长',
        'sec_goal': '5. 治疗目标',
        'lbl_goal': '今天的目标',
        'lbl_note': '补充说明',
        'btn_submit': '生成评估报告',
        'err': '⚠️ 请填写姓名和疼痛部位',
        'loading': '正在生成分析...',
        'success': '报告已生成！'
    }
}

t = trans[st.session_state.language]

# 配置 API
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("API Key Missing")
    st.stop()

# --- 4. 界面布局 (手机优先设计) ---

# 顶部：Logo 和 语言切换
col1, col2 = st.columns([3, 1])
with col1:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("## Massage Philosophy")
with col2:
    if st.button(t['btn_toggle']):
        toggle_language()
        st.rerun()

st.write(f"### {t['title']}")
st.caption(t['subtitle'])
st.markdown("---")

# 表单开始
with st.form("mobile_intake_form"):
    
    # Section 1
    st.markdown(f"**{t['sec_basic']}**")
    name = st.text_input(t['lbl_name'])
    email = st.text_input(t['lbl_email'])
    
    st.markdown("---")
    
    # Section 2
    st.markdown(f"**{t['sec_pain']}**")
    pain_area = st.multiselect(
        t['lbl_area'],
        ["Neck (颈)", "Shoulders (肩)", "Upper Back (上背)", "Lower Back (下腰)", 
         "Hips (臀)", "Legs (腿)", "Knees (膝)", "Feet (足)", "Head (头)", "Arms (手)"]
    )
    
    col_side, col_dur = st.columns(2)
    with col_side:
        pain_side = st.selectbox(t['lbl_side'], ["Both (两侧)", "Left (左)", "Right (右)", "Center (中)"])
    with col_dur:
        duration = st.selectbox(t['lbl_duration'], ["<24h (新伤)", "1wk (一周)", "1m (一月)", ">3m (长期)"])
        
    st.markdown("---")
    
    # Section 3
    st.markdown(f"**{t['sec_char']}**")
    pain_desc = st.multiselect(t['lbl_desc'], ["Sharp (刺痛)", "Dull (酸痛)", "Stiff (僵硬)", "Numb (麻木)"])
    pain_level = st.slider(t['lbl_level'], 0, 10, 5)
    
    st.markdown("---")
    
    # Section 4
    st.markdown(f"**{t['sec_life']}**")
    activity = st.selectbox(t['lbl_job'], ["Desk Job (办公)", "Standing (久站)", "Labor (体力)", "Athlete (运动)"])
    sitting = st.select_slider(t['lbl_sit'], options=["<2h", "2-4h", "4-8h", "8h+"])
    
    st.markdown("---")
    
    # Section 5
    st.markdown(f"**{t['sec_goal']}**")
    goals = st.multiselect(t['lbl_goal'], ["Pain Relief (止痛)", "Relax (放松)", "Sleep (助眠)", "Tissue (松解)"])
    notes = st.text_area(t['lbl_note'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    # 提交按钮
    submitted = st.form_submit_button(t['btn_submit'])

# --- 5. 结果生成 ---
if submitted:
    if not name or not pain_area:
        st.error(t['err'])
    else:
        with st.spinner(t['loading']):
            # Prompt 逻辑
            area_str = ", ".join(pain_area)
            desc_str = ", ".join(pain_desc)
            goals_str = ", ".join(goals)
            
            prompt = f"""
            Role: Senior Therapist AI for 'Massage Philosophy (易经)'.
            Input: Name:{name}, Pain:{area_str}({pain_side}), Dur:{duration}, Lvl:{pain_level}, Feel:{desc_str}, Job:{activity}, Sit:{sitting}, Goal:{goals_str}.
            
            Task: Create a Bilingual Report.
            
            Output Format:
            
            ---
            (PART 1: ENGLISH - For Therapist)
            # Massage Philosophy - Assessment
            **Client:** {name} | **Date:** {datetime.now().strftime('%Y-%m-%d')}
            **Condition:** {pain_level}/10 pain in {area_str}. Likely caused by {activity}.
            **Plan:** Recommend 60/90 mins. Focus on {area_str}. Technique: Deep Tissue/Heat.
            **Home Care:** 1 stretch advice.
            
            ---
            (PART 2: CHINESE - For Client)
            # 易经理疗 - 诊断简报
            **客户:** {name}
            **分析:** 您的{area_str}疼痛（{pain_level}级）主要与您【{activity}】的生活习惯有关。
            **方案:** 建议进行深层理疗。
            **建议:** 居家热敷患处。
            
            ---
            **Disclaimer:** Wellness reference only. Not medical advice.
            免责声明：仅供理疗参考，非医疗诊断。
            """
            
            try:
                response = model.generate_content(prompt)
                st.success(t['success'])
                
                st.markdown("""
                <div style="background-color:white; padding:20px; border-radius:10px; border:1px solid #ddd; box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                """, unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
