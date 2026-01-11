import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Massage Philosophy Intake",
    page_icon="🌿",
    layout="wide"
)

# 隐藏多余菜单
hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# --- 2. 语言状态管理 (核心逻辑) ---
if 'language' not in st.session_state:
    st.session_state.language = 'en' # 默认设为英文

def toggle_language():
    if st.session_state.language == 'en':
        st.session_state.language = 'zh'
    else:
        st.session_state.language = 'en'

# 定义词典：这里管理所有的中英文对照
trans = {
    'en': {
        'btn_label': '中文', # 英文界面下显示“中文”按钮
        'sb_title': 'Client Intake Form',
        'sb_caption': 'Takes 2-3 mins to complete',
        'sec_basic': '1. Basic Information',
        'lbl_name': 'Client Name',
        'lbl_email': 'Email',
        'sec_pain': '2. Main Pain Details',
        'lbl_area': 'Main area of pain',
        'lbl_side': 'Side of pain',
        'lbl_duration': 'How long have you had this?',
        'sec_char': '3. Pain Characteristics',
        'lbl_desc': 'Description of sensation',
        'lbl_level': 'Pain Intensity (0-10)',
        'sec_life': '4. Daily Activity',
        'lbl_job': 'Daily activity type',
        'lbl_sit': 'Hours sitting per day',
        'sec_goal': '5. Treatment Goal',
        'lbl_goal': 'Main goal for today',
        'lbl_note': 'Additional Notes',
        'ph_note': 'Surgeries, injuries, or specific preferences...',
        'btn_submit': 'Generate Assessment',
        'err_msg': '⚠️ Please fill in Client Name and Pain Area.',
        'loading': 'Anina (AI Specialist) is analyzing...',
        'success': '✅ Assessment Generated Successfully!',
        'welcome_title': 'Massage Philosophy - Clinical Assessment',
        'welcome_msg': '👈 Please fill out the form in the left sidebar.',
        'welcome_guide': 'This digital form helps us understand your condition and generate a customized treatment plan.'
    },
    'zh': {
        'btn_label': 'English', # 中文界面下显示“English”按钮
        'sb_title': '客户身体评估表',
        'sb_caption': '填写约需 2-3 分钟',
        'sec_basic': '1. 基础信息',
        'lbl_name': '客户姓名',
        'lbl_email': '电子邮箱',
        'sec_pain': '2. 核心疼痛信息',
        'lbl_area': '主要疼痛部位',
        'lbl_side': '疼痛侧别',
        'lbl_duration': '疼痛持续多久了？',
        'sec_char': '3. 疼痛特征',
        'lbl_desc': '疼痛感描述',
        'lbl_level': '疼痛程度 (0=无痛, 10=剧痛)',
        'sec_life': '4. 日常活动与姿势',
        'lbl_job': '日常活动/工作类型',
        'lbl_sit': '每天久坐时长',
        'sec_goal': '5. 治疗目标',
        'lbl_goal': '今天的主要目标',
        'lbl_note': '补充说明',
        'ph_note': '如：有无旧伤、手术史、力度偏好...',
        'btn_submit': '生成专业评估报告',
        'err_msg': '⚠️ 请填写姓名和疼痛部位。',
        'loading': '首席顾问 Anina 正在分析病例...',
        'success': '✅ 报告已生成！',
        'welcome_title': '易经理疗 - 智能诊断系统',
        'welcome_msg': '👈 请在左侧侧边栏填写信息。',
        'welcome_guide': '本系统将数字化分析客户身体状况，并自动生成中英双语治疗方案。'
    }
}

# 获取当前语言的文本包
t = trans[st.session_state.language]

# 读取 API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("请先配置 API Key")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. 注入 CSS 样式 ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfbf9; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    h1, h2, h3, h4 { color: #3e2723; font-family: sans-serif; }
    div.stButton > button {
        background-color: #9e2a2b; color: white; border: none; 
        padding: 10px 20px; border-radius: 6px;
    }
    div.stButton > button:hover { background-color: #7f1d1d; color: white; }
    /* 语言切换按钮样式微调 */
    .lang-btn button { background-color: #f0f0f0 !important; color: #333 !important; border: 1px solid #ccc !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. 侧边栏 ---
with st.sidebar:
    # 顶部布局：Logo + 语言切换按钮
    col_logo, col_lang = st.columns([3, 1])
    with col_logo:
        try:
            st.image("logo.png", width=160)
        except:
            st.markdown("### Massage Philosophy")
    with col_lang:
        # 这是一个小的切换按钮
        if st.button(t['btn_label'], key="lang_btn"):
            toggle_language()
            st.rerun()

    st.markdown(f"### 📋 {t['sb_title']}")
    st.caption(t['sb_caption'])
    st.markdown("---")
    
    with st.form("intake_form"):
        # 1. 基础信息
        st.markdown(f"#### {t['sec_basic']}")
        client_name = st.text_input(t['lbl_name'])
        email = st.text_input(t['lbl_email'])
        
        st.markdown("---")
        
        # 2. 疼痛信息
        st.markdown(f"#### {t['sec_pain']}")
        pain_area = st.multiselect(
            t['lbl_area'],
            # 选项保留双语，方便 AI 理解，也方便员工对照
            ["Neck (颈部)", "Shoulders (肩部)", "Upper Back (上背部)", "Lower Back (下腰部)", 
             "Hips/Glutes (臀部)", "Legs (腿部)", "Knees (膝盖)", "Feet (足部)", "Arms (手臂)", "Head (头部)"]
        )
        
        pain_side = st.radio(
            t['lbl_side'],
            ["Both sides (两侧)", "Left side (左侧)", "Right side (右侧)", "Central (中间)"],
            horizontal=True
        )
        
        pain_duration = st.selectbox(
            t['lbl_duration'],
            ["< 24 hours (24小时内)", "1-7 days (1周内)", "1-4 weeks (1个月内)", "1-3 months (1-3个月)", "> 3 months (3个月以上)"]
        )
        
        st.markdown("---")

        # 3. 疼痛特征
        st.markdown(f"#### {t['sec_char']}")
        pain_desc = st.multiselect(
            t['lbl_desc'],
            ["Sharp (刺痛)", "Dull/Aching (酸痛)", "Stiff (僵硬)", "Numbness (麻木)", "Burning (灼烧)", "Throbbing (跳痛)"]
        )
        
        pain_level = st.slider(t['lbl_level'], 0, 10, 5)
        
        st.markdown("---")

        # 4. 日常活动
        st.markdown(f"#### {t['sec_life']}")
        activity_type = st.selectbox(
            t['lbl_job'],
            ["Sedentary/Desk Job (久坐办公)", "Standing Job (久站)", "Physical Labor (体力劳动)", "Athlete (运动/健身)", "Retired (退休/轻度活动)"]
        )
        
        sitting_hours = st.select_slider(
            t['lbl_sit'],
            options=["< 2h", "2-4h", "4-8h", "8h+"]
        )
        
        st.markdown("---")

        # 5. 目标与备注
        st.markdown(f"#### {t['sec_goal']}")
        goals = st.multiselect(
            t['lbl_goal'],
            ["Pain Relief (止痛)", "Relaxation (放松)", "Mobility (活动度)", "Better Sleep (改善睡眠)", "Deep Tissue (深层松解)"]
        )
        
        notes = st.text_area(t['lbl_note'], placeholder=t['ph_note'])
        
        # 提交按钮
        submitted = st.form_submit_button(t['btn_submit'])

# --- 5. 主界面逻辑 ---
st.header(t['welcome_title'])

if submitted:
    if not client_name or not pain_area:
        st.error(t['err_msg'])
    else:
        with st.spinner(t['loading']):
            
            # 数据处理
            area_str = ", ".join(pain_area)
            desc_str = ", ".join(pain_desc)
            goals_str = ", ".join(goals)
            
            # --- AI Prompt (保持核心业务逻辑不变) ---
            prompt = f"""
            You are 'Anina', the Senior Therapist AI for 'Massage Philosophy (易经)'.
            
            Client Data:
            - Name: {client_name}
            - Pain: {area_str} ({pain_side})
            - Duration: {pain_duration}
            - Level: {pain_level}/10
            - Sensation: {desc_str}
            - Job: {activity_type}, Sits {sitting_hours}/day
            - Goals: {goals_str}
            - Notes: {notes}

            Task: Generate a Bilingual Clinical Assessment Report.
            
            Structure:
            1. PART 1: English Report (Professional, for records).
            2. PART 2: Chinese Report (For client communication).
            3. PART 3: Disclaimer.
            
            Content Logic:
            - Connect lifestyle ({activity_type}) to pain.
            - Explain anatomy (muscles involved).
            - Recommend 60/90 mins session if pain > 5 or chronic.
            
            Format: Use Markdown, bold key terms.
            
            ---
            (PART 1: ENGLISH CLINICAL REPORT)
            # Massage Philosophy - Clinical Assessment
            **Client:** {client_name} | **Date:** {datetime.now().strftime('%Y-%m-%d')}
            
            **1. Assessment (S & O):**
            Client presents with {pain_level}/10 pain in {area_str}. Condition: {pain_duration}.
            Likely aggravated by {activity_type}.
            
            **2. Analysis (A):**
            (Anatomical analysis here).
            
            **3. Plan (P):**
            - **Session:** (Recommend duration).
            - **Techniques:** (Deep Tissue / Trigger Point / Heat).
            - **Home Care:** (Stretches).

            ---
            (PART 2: CHINESE REPORT)
            # 易经理疗 - 诊断报告
            **客户:** {client_name}
            
            **1. 症状分析:**
            (用中文解释成因，例如：长期久坐导致腰方肌紧张)。
            
            **2. 治疗方案:**
            - **推荐时长:** (根据痛感推荐).
            - **重点项目:** (深层松解/热石等).
            
            **3. 居家建议:**
            (简单建议).

            ---
            **Disclaimer / 免责声明**
            This report is for wellness reference only. Not a medical diagnosis.
            本报告仅供理疗参考，不构成医疗诊断。
            """
            
            try:
                response = model.generate_content(prompt)
                st.success(t['success'])
                
                # 报告显示区域
                st.markdown("""
                <div style="background-color:white; padding:30px; border-radius:10px; border-top:5px solid #9e2a2b; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                """, unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error: {e}")

else:
    # 欢迎页引导
    st.info(t['welcome_msg'])
    st.markdown(f"#### {t['welcome_guide']}")
