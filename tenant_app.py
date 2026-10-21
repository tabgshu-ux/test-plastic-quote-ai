
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Tenant Enterprise ERP System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card-container { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-bottom: 20px; }
    h1, h2, h3 { color: #1e293b; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 初始化租戶端全域狀態
if "tenant_logged_in" not in st.session_state:
    st.session_state.tenant_logged_in = False
if "current_tenant_user" not in st.session_state:
    st.session_state.current_tenant_user = None

# 模擬當前租戶的內部資料庫 (未來可與後端 DB 隔離串接)
if "current_tenant_data" not in st.session_state:
    st.session_state.current_tenant_data = {
        "tenant_id": "tenant_vina_group",
        "name": "🇻🇳 越南平陽控股集團 (暨環保鞋業與咖啡廳)",
        "plan": "🚀 旗艦集團版 (Enterprise)",
        "staff": [
            {"name": "許福村", "account": "boss", "password": "123", "role": "👑 Tenant Admin (老闆/最高管理員)", "dept": "董事長室"},
            {"name": "Trần Văn Minh", "account": "minh", "password": "123", "role": "💰 Department Manager (財務主管)", "dept": "財務部"},
            {"name": "Le Van Hung", "account": "hung", "password": "123", "role": "🏭 Field Worker (現場作業人員)", "dept": "工程技術部"}
        ],
        "org_nodes": [
            {"id": "node_root", "name": "集團董事長室", "type": "👑 頂層 (Board)", "parent": "無 (頂層)"},
            {"id": "node_eng", "name": "越南平陽廠區", "type": "🏭 製造廠區", "parent": "集團董事長室"}
        ]
    }

tenant_info = st.session_state.current_tenant_data

# ==================== 租戶端側邊欄導覽 ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/factory.png", width=64)
    st.markdown(f"### 🏭 {tenant_info['name']}")
    st.markdown(f"**目前方案**: `{tenant_info['plan']}`")
    st.markdown("---")
    
    if st.session_state.tenant_logged_in:
        user_info = st.session_state.current_tenant_user
        st.markdown(f"**登入員工**: `{user_info['name']}`")
        st.markdown(f"**職務身分**: `{user_info['role']}`")
        if st.button("🔒 登出租戶系統", use_container_width=True):
            st.session_state.tenant_logged_in = False
            st.session_state.current_tenant_user = None
            st.rerun()
    else:
        st.markdown("🔒 **目前身分**: `請先登入企業帳號`")
        
    st.markdown("---")
    if st.session_state.tenant_logged_in:
        tenant_menu = st.radio(
            "企業內部模組選單",
            [
                "👑 老闆級即時經營戰情室 (Executive BI)",
                "☕ 智慧零售與 POS 咖啡廳管理",
                "🏭 MES 車間製鞋排程與顏色管理",
                "👥 企業內部員工與權限管理 (RBAC)"
            ]
        )
    else:
        tenant_menu = "🔒 請先登入"

# ==================== 租戶端主畫面邏輯 ====================
if not st.session_state.tenant_logged_in:
    st.markdown("## 🔐 企業租戶 ERP 系統安全登入")
    st.info("💡 *請輸入您在該企業內部的帳號與密碼 (預設老闆帳號: `boss` / 密碼: `123`)。*")
    
    with st.form("tenant_login_form"):
        t_acc = st.text_input("企業登入帳號 (Account)", placeholder="例: boss 或 minh")
        t_pass = st.text_input("密碼 (Password)", type="password", placeholder="請輸入密碼...")
        
        if st.form_submit_button("🔓 登入企業 ERP", type="primary", use_container_width=True):
            matched_staff = None
            for s in tenant_info["staff"]:
                if s["account"] == t_acc and s["password"] == t_pass:
                    matched_staff = s
                    break
            
            if matched_staff:
                st.session_state.tenant_logged_in = True
                st.session_state.current_tenant_user = matched_staff
                st.success(f"🎉 登入成功！歡迎回到 {tenant_info['name']}")
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤！")
else:
    current_user = st.session_state.current_tenant_user
    
    if "老闆級即時經營戰情室" in tenant_menu:
        # 嚴格權限檢查：只有老闆或 Admin 才能看戰情室
        if "Admin" not in current_user["role"] and "老闆" not in current_user["role"]:
            st.warning("⚠️ **權限不足 (Access Denied)**：此戰情室僅限最高決策者與 Tenant Admin 檢視。")
        else:
            st.markdown(f"## 👑 {tenant_info['name']}：老闆級即時經營戰情室 (Executive BI)")
            st.info("💡 *整合跨部門營收、咖啡廳免費額度、鞋款顏色銷售分析與重大異常預警。*")
            
            # 四大核心指標
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 本月即時總營收", "$ 128,450 USD", "+ 12.5%")
            with col2:
                st.metric("☕ 咖啡廳今日免費杯數", "342 / 500 杯", "消耗率 68%")
            with col3:
                st.metric("👟 咖啡絲環保鞋產量", "1,250 雙", "稼動率 92%")
            with col4:
                st.metric("⚡ 電動車激勵競賽積分第一", "Le Van Hung", "推薦 28 人")
                
            st.markdown("---")
            
            # 圖表與異常預警
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                st.markdown("### 📈 各鞋款顏色喜好與銷售佔比")
                chart_data = pd.DataFrame({
                    "鞋款顏色": ["拿鐵棕 (Latte Brown)", "抹茶綠 (Matcha Green)", "經典黑 (Classic Black)", "燕麥白 (Oatmeal White)"],
                    "銷售數量 (雙)": [450, 320, 280, 200]
                })
                st.bar_chart(chart_data.set_index("鞋款顏色"))
                st.markdown('</div>', unsafe_allow_html=True)
                
            with c_right:
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                st.markdown("### 🚨 跨部門重大異常與庫存預警通知")
                st.warning("⚠️ **【庫存警報】** 「咖啡絲環保原料」安全水位偏低（剩餘 15%），建議立即發起自動補貨。")
                st.info("ℹ️ **【審核通知】** 有 3 筆超過 $5,000 USD 的設備採購單正等待董事長室簽核。")
                st.success("✅ **【系統狀態】** POS 收銀機與人臉辨識門市連線正常。")
                st.markdown('</div>', unsafe_allow_html=True)

    elif "智慧零售與 POS 咖啡廳管理" in tenant_menu:
        st.markdown("## ☕ 智慧零售、POS 收銀與會員咖啡廳管理系統")
        st.info("💡 *在此管理會員人臉辨識記錄、咖啡免費額度消耗、推薦分潤與電動車激勵競賽。*")
        st.success("✅ POS 實體收銀機連線正常 | AI 人臉辨識鏡頭運行中")

    elif "MES 車間製鞋排程與顏色管理" in tenant_menu:
        st.markdown("## 🏭 MES 製造執行系統：鞋款顏色與車間動態排程")
        st.info("💡 *前端客戶選定的鞋款顏色與尺寸，將即時同步至此進行橡膠射出機台與產線排程。*")

    else:
        st.markdown("## 👥 企業內部員工與權限管理 (RBAC)")
        st.info("💡 *在此管理該企業內部員工的部門、職稱與資料存取權限。*")
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(tenant_info["staff"]), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
