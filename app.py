import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 1. 页面配置 & 品牌色调 ---
st.set_page_config(
    page_title="Massage Philosophy Intake System",
    page_icon="🌿",
    layout="wide"
)

# 读取 API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("请先配置 API Key")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. 注入“易经”品牌 CSS (医疗级界面) ---
# 我们提取了 Logo 中的深红色 (#9e2a2b) 和深褐色 (#333333)
st.markdown("""
    <style>
    /* 全局字体与背景 */
    .stApp {
        background-color: #fdfbf7; /* 极淡的米色背景，护眼 */
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* 标题样式 */
    h1, h2, h3 {
        color: #3e2723; /* 深褐色，对应 Logo 文字 */
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* 按钮样式 - 品牌红 */
    div.stButton > button {
        background-color: #9e2a2b; /* 易经红 */
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #7f1d1d; /* 深一点的红色 */
        color: white;
    }
    
    /* 强调框样式 */
    .report-box {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-top: 5px solid #9e2a2b; /* 顶部红条 */
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏：复刻 Google Form (病历录入) ---
with st.sidebar:
    # 尝试显示 Logo，如果没有上传则显示文字
    try:
        st.image("logo.png", width=200) # 确保你上传的图片叫 logo.png
    except:
        st.markdown("## Massage Philosophy")
        st.caption("Remedial & Wellness Center")

    st.markdown("### 📋 Client Intake Form")
    
    with st.form("intake_form"):
        # 基本信息
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("Name (姓名)")
        with col_b:
            gender = st.selectbox("Gender (性别)", ["Female", "Male", "Other"])
            
        dob = st.date_input("Date of Birth (出生日期)", min_value=datetime(1940, 1, 1))
        
        # 医疗信息 (复刻表格核心)
        symptoms = st.text_area("Reason for visit / Main Symptoms (主要症状)", height=100, placeholder="e.g., Lower back pain when sitting, stiff neck...")
        
        history = st.text_area("Medical History / Injuries (病史/旧伤)", placeholder="e.g., Surgery in 2020, High blood pressure...")
        
        # 偏好设置
        pressure = st.slider("Pressure Preference (力度偏好)", 1, 10, 6)
        focus_area = st.multiselect("Focus Areas (重点部位)", ["Neck (颈)", "Shoulders (肩)", "Lower Back (下腰)", "Legs (腿)", "Head (头)", "Feet (足)"])
        
        submitted = st.form_submit_button("Generate Assessment (生成诊断)")

# --- 4. 主界面：AI 分析报告 ---
if submitted:
    if not name or not symptoms:
        st.error("Please fill in Name and Symptoms to proceed. (请填写姓名和症状)")
    else:
        # 显示加载状态
        with st.spinner('AI Specialist is analyzing the case...'):
            
            # --- 核心 Prompt (双语分离 + 易经风格) ---
            prompt = f"""
            You are the Senior Therapist AI for 'Massage Philosophy (易经)'.
            
            Client Data:
            - Name: {name} ({gender})
            - DOB: {dob}
            - Symptoms: {symptoms}
            - History: {history}
            - Focus: {', '.join(focus_area)}
            - Pressure: {pressure}/10

            Task: Generate a professional Remedial Massage Assessment Report.
            
            CRITICAL OUTPUT FORMAT (Must follow strictly for printing):
            
            ---
            (PART 1: ENGLISH REPORT)
            # Massage Philosophy - Clinical Assessment
            **Client Name:** {name} | **Date:** {datetime.now().strftime('%Y-%m-%d')}
            
            1. **Symptom Analysis**: Explain the anatomy involved (muscles/fascia) based on the symptoms.
            2. **Recommended Treatment**: 
               - Suggest strict duration (60/90 mins).
               - Specific techniques (e.g., Trigger Point, Myofascial Release, Cupping).
            3. **Treatment Plan**: Why this helps.
            4. **Home Care**: 1-2 exercises.
            
            ---
            (PART 2: CHINESE REPORT)
            # 易经 Massage Philosophy - 理疗诊断书
            **客患姓名:** {name}
            
            1. **症状病理分析**: 用中医或解剖学角度解释疼痛成因（如气血瘀滞、斜方肌劳损等）。
            2. **建议疗程方案**:
               - **推荐时长**: (根据病情强烈推荐 90分钟 或 120分钟 以达到深层治疗效果)。
               - **理疗项目**: (如：深层组织推拿、拔罐、刮痧)。
            3. **居家护理建议**: 热敷或拉伸建议。

            ---
            (PART 3: DISCLAIMER)
            **Disclaimer / 免责声明**
            This report is for wellness reference only and does not constitute a medical diagnosis. Please consult a doctor for serious conditions.
            本报告仅供理疗参考，不构成医疗诊断。如有严重不适或潜在疾病，请咨询专业医生。
            """
            
            response = model.generate_content(prompt)
            
            # --- 5. 渲染报告 (卡片式设计) ---
            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.markdown(response.text)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 打印按钮提示
            st.info("💡 Tip: You can press 'Ctrl + P' (or Cmd + P) to print this page directly for the client.")

else:
    # 欢迎界面
    st.markdown("## Welcome to Massage Philosophy Clinical System")
    st.markdown("#### 易经理疗 · 智能前台辅助系统")
    st.write("Please enter client details in the left sidebar to begin assessment.")
    st.info("👈 请在左侧侧边栏录入客人信息 (已集成 Google Form 字段)")
