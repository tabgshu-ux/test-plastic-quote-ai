import streamlit as st
import pandas as pd
import modules.executive_dashboard as exec_dash

# ----------------------------------------------------
# 🔐 1. 企業使用者帳號資料庫 (保留原本 Admin 與各部門帳號)
# ----------------------------------------------------
USER_DB = {
    "admin": {"name": "系統管理員 (System Admin)", "pass": "admin123", "role": "ADMIN", "title": "💻 系統管理員"},
    "gm01": {"name": "張總經理", "pass": "gm123", "role": "GM", "title": "👑 董事長 / 總經理"},
    "cfo01": {"name": "陳財務長", "pass": "cfo123", "role": "CFO", "title": "💵 財務主管"},
    "acc01": {"name": "林會計", "pass": "acc123", "role": "ACCOUNTANT", "title": "🧾 財務會計"},
    "ga01": {"name": "李總務主管", "pass": "ga123", "role": "GA_MANAGER", "title": "🏢 總務主管"},
    "ga02": {"name": "王總務專員", "pass": "ga456", "role": "GA_STAFF", "title": "📋 總務專員"},
    "pm01": {"name": "黃廠長", "pass": "pm123", "role": "PLANT_MANAGER", "title": "🏭 廠務主管"}
}

# ----------------------------------------------------
# 🔐 2. 職務與授權頁面對照表 (Role-Based Access Control)
# ----------------------------------------------------
ROLE_PERMISSIONS = {
    "ADMIN": {
        "depts": ["📈 營運戰情室 (Executive)", "💵 財務 (Finance)", "👥 人事/行政 (HR & Admin)", "💼 業務/行銷 (Sales & Marketing)", "⚒️ 研發/技術 (R&D & Engineering)", "🏭 廠務/設備 (Plant & IoT)", "💻 資訊/IT (IT & System Admin)"],
        "fin_subs": ["📈 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)", "🏢 總務管理 (GA)"]
    },
    "GM": {
        "depts": ["📈 營運戰情室 (Executive)", "💵 財務 (Finance)", "👥 人事/行政 (HR & Admin)", "💼 業務/行銷 (Sales & Marketing)", "⚒️ 研發/技術 (R&D & Engineering)", "🏭 廠務/設備 (Plant & IoT)", "💻 資訊/IT (IT & System Admin)"],
        "fin_subs": ["📈 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)", "🏢 總務管理 (GA)"]
    },
    "CFO": {
        "depts": ["💵 財務 (Finance)"],
        "fin_subs": ["📈 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)", "🏢 總務管理 (GA)"]
    },
    "ACCOUNTANT": {
        "depts": ["💵 財務 (Finance)"],
        "fin_subs": ["📈 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)"]
    },
    "GA_MANAGER": {
        "depts": ["💵 財務 (Finance)", "👥 人事/行政 (HR & Admin)"],
        "fin_subs": ["🏢 總務管理 (GA)"]
    },
    "GA_STAFF": {
        "depts": ["💵 財務 (Finance)"],
        "fin_subs": ["🏢 總務管理 (GA)"]
    },
    "PLANT_MANAGER": {
        "depts": ["🏭 廠務/設備 (Plant & IoT)"],
        "fin_subs": []
    }
}

# ----------------------------------------------------
# 🏢 3. 總務 (General Affairs / GA) 模組頁面
# ----------------------------------------------------
def render_general_affairs_module(user_info):
    st.title("🏢 總務管理系統 (General Affairs / GA)")
    st.caption(f"登入使用者：{user_info['name']} ({user_info['title']}) — 固定資產、零用金與辦公耗材")

    st.divider()

    ga_tab1, ga_tab2, ga_tab3 = st.tabs([
        "🛋️ 門市與辦公室固定資產",
        "💵 零用金與日常費用報支",
        "📦 總務耗材與辦公用品庫存"
    ])

    with ga_tab1:
        st.subheader("🛋️ 固定資產與設備清冊 (Fixed Assets)")
        fixed_assets = [
            {"資產編號": "FA-2026-001", "資產名稱": "首爾門市自動咖啡機 (Hub)", "保管部門": "總務部", "存放地點": "首爾漢陽門市", "取得金額 (USD)": "$12,000", "耐用年限": "5年", "折舊狀態": "正常提撥中"},
            {"資產編號": "FA-2026-002", "資產名稱": "行政區伺服器與網路設備", "保管部門": "資訊部/總務", "存放地點": "台灣總部機房", "取得金額 (USD)": "$8,500", "耐用年限": "3年", "折舊狀態": "正常提撥中"},
            {"資產編號": "FA-2026-003", "資產名稱": "總部會客室沙發與高階桌椅", "保管部門": "總務部", "存放地點": "台灣總部 3F", "取得金額 (USD)": "$4,200", "耐用年限": "5年", "折舊狀態": "正常提撥中"}
        ]
        st.dataframe(pd.DataFrame(fixed_assets), use_container_width=True)

    with ga_tab2:
        st.subheader("💵 零用金申請與日常費用審核 (Petty Cash)")
        col_pc1, col_pc2 = st.columns([2, 1])
        with col_pc1:
            petty_cash = [
                {"單號": "PC-20260901", "申請日期": "2026-09-20", "申請人": "張專員", "項目說明": "漢陽門市清潔用品與洗滌劑採購", "金額 (USD)": "$120.00", "審核狀態": "🟢 已核銷"},
                {"單號": "PC-20260905", "申請日期": "2026-09-24", "申請人": "李主管", "項目說明": "公務車加油與國道過路費", "金額 (USD)": "$85.00", "審核狀態": "🟡 待財務核決"}
            ]
            st.dataframe(pd.DataFrame(petty_cash), use_container_width=True)
        with col_pc2:
            st.markdown("##### ➕ 新增零用金報銷申請")
            st.text_input("報銷項目名稱：", placeholder="例如：印表機碳粉匣採購")
            st.number_input("申請金額 ($ USD)：", min_value=0.0, value=50.0, step=10.0)
            if st.button("🚀 提交零用金申請", type="primary"):
                st.success("✅ 申請單已成功送出至財務主管審核！")

    with ga_tab3:
        st.subheader("📦 總務耗材與辦公用品庫存 (GA Supplies)")
        ga_supplies = [
            {"品項名稱": "☕ 環保紙杯 (Hub門市專用)", "目前庫存": "12,000 個", "安全庫存": "3,000 個", "狀態": "🟢 充足"},
            {"品項名稱": "📄 影印紙 A4 (雙面環保)", "目前庫存": "45 箱", "安全庫存": "10 箱", "狀態": "🟢 充足"}
        ]
        st.dataframe(pd.DataFrame(ga_supplies), use_container_width=True)

# ----------------------------------------------------
# 🚀 4. 主程式與身份驗證 (Authentication & Main Flow)
# ----------------------------------------------------
def main():
    st.set_page_config(
        page_title="Multinational ERP System",
        page_icon="📈",
        layout="wide"
    )

    # 初始化 Session 登入狀態
    if "user_account" not in st.session_state:
        st.session_state["user_account"] = None

    # ----------------------------------------------------
    # 🔓 未登入狀態：強制顯示登入視窗
    # ----------------------------------------------------
    if st.session_state["user_account"] is None:
        st.title("🔒 企業 ERP 跨國管理系統 — 使用者登入")
        
        col_login, col_tip = st.columns([1, 1])
        with col_login:
            account = st.text_input("請輸入員工/管理員帳號 (Account)：")
            password = st.text_input("請輸入登入密碼 (Password)：", type="password")
            
            if st.button("🚀 登入系統", type="primary"):
                if account in USER_DB and USER_DB[account]["pass"] == password:
                    st.session_state["user_account"] = account
                    st.toast(f"✅ 歡迎登入，{USER_DB[account]['name']}！")
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤，請重新輸入！")

        with col_tip:
            st.info("""
            💡 **測試帳號密碼指引：**
            * **admin** / `admin123` ：系統管理員（完整最高存取權限）
            * **gm01** / `gm123` ：張總經理（全部部門權限）
            * **cfo01** / `cfo123` ：陳財務長（財務與總務全部權限）
            * **acc01** / `acc123` ：林會計（僅財務權限，無總務）
            * **ga01** / `ga123` ：李總務主管（僅總務與人事權限）
            * **pm01** / `pm123` ：黃廠長（僅廠務設備權限）
            """)
        st.stop()

    # ----------------------------------------------------
    # 🔐 已登入狀態：取得當前使用者資訊與對應權限
    # ----------------------------------------------------
    user_account = st.session_state["user_account"]
    user_info = USER_DB[user_account]
    user_role = user_info["role"]
    
    permissions = ROLE_PERMISSIONS.get(user_role, {"depts": [], "fin_subs": []})
    allowed_depts = permissions["depts"]
    allowed_fin_subs = permissions["fin_subs"]

    # 側邊欄：使用者資訊與登出按鈕
    st.sidebar.markdown(f"👤 **登入身分**：{user_info['name']}")
    st.sidebar.caption(f"職務：{user_info['title']}")
    if st.sidebar.button("🚪 安全登出系統", type="secondary"):
        st.session_state["user_account"] = None
        st.rerun()

    st.sidebar.divider()

    # 系統語言切換
    st.sidebar.markdown("### 🌐 System Language")
    lang = st.sidebar.selectbox(
        "選擇語言 / Select Language",
        ["繁體中文", "Tiếng Việt", "English", "简体中文", "Bahasa Indonesia"],
        key="global_sys_lang"
    )
    st.session_state["lang"] = lang

    st.sidebar.divider()

    # ----------------------------------------------------
    # 側邊欄：動態過濾選單（僅顯示該帳號授權之部門）
    # ----------------------------------------------------
    st.sidebar.markdown("### 📌 授權功能選單：")
    
    selected_dept = st.sidebar.radio(
        "選擇部門/模組：",
        allowed_depts,
        key="authenticated_dept_radio"
    )

    # ----------------------------------------------------
    # 頁面主體渲染邏輯
    # ----------------------------------------------------
    if "📈 營運戰情室" in selected_dept:
        exec_dash.render_executive_dashboard_page(sub_option="🌐 全部市場 (All Markets)", lang=lang)

    elif "💵 財務" in selected_dept:
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 💵 授權財務與總務細項：")

        selected_fin_sub = st.sidebar.radio(
            "選擇細項：",
            allowed_fin_subs,
            key="authenticated_fin_sub_radio"
        )

        if "🏢 總務管理" in selected_fin_sub:
            render_general_affairs_module(user_info)
        else:
            exec_dash.render_executive_dashboard_page(sub_option=selected_fin_sub, lang=lang)

    elif "👥 人事/行政" in selected_dept:
        st.title("👥 人事與行政管理系統 (HR & Admin)")
        st.info(f"當前身分：{user_info['name']} ({user_info['title']}) — 專屬授權 HR 考勤、薪資發放與人員績效模組。")

    elif "💼 業務/行銷" in selected_dept:
        st.title("💼 業務與行銷管理系統 (Sales & CRM)")
        st.info(f"當前身分：{user_info['name']} ({user_info['title']}) — 專屬授權 CRM 客戶訂單與經銷商渠道管理。")

    elif "⚒️ 研發/技術" in selected_dept:
        st.title("⚒️ 研發與技術管理系統 (R&D & Engineering)")
        st.info(f"當前身分：{user_info['name']} ({user_info['title']}) — 專屬授權 3D 鞋型設計與自動化模具研發專案。")

    elif "🏭 廠務/設備" in selected_dept:
        st.title("🏭 廠務與自動化設備 MES 系統")
        exec_dash.render_plant_oee_kpi()

    elif "💻 資訊/IT" in selected_dept:
        st.title("💻 資訊系統與權限管理 (IT & System Admin)")
        st.info(f"當前身分：{user_info['name']} ({user_info['title']}) — 專屬授權 ERP 系統日誌與網路資安監控。")

if __name__ == "__main__":
    main()
