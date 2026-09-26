import streamlit as st
import modules.executive_dashboard as exec_dash

# ----------------------------------------------------
# 🔐 1. 定義部門與職位權限矩陣 (Permission Matrix)
# ----------------------------------------------------
ROLE_PERMISSIONS = {
    "👑 董事長 / 總經理 (GM / Executive)": {
        "allowed_pages": [
            "📈 跨國企業營运戰情室",
            "📊 VPSH 八大財務報表",
            "🏢 總務管理 (固定資產與零用金)",
            "🏭 廠區機台稼動 (OEE)",
            "👥 人事與行政管理"
        ]
    },
    "💵 財務主管 (CFO / Finance Manager)": {
        "allowed_pages": [
            "📊 VPSH 八大財務報表",
            "🌐 全球 AR/AP 帳款統計",
            "🏢 總務管理 (固定資產與零用金)"
        ]
    },
    "🧾 財務會計 (Accountant)": {
        "allowed_pages": [
            "📊 VPSH 八大財務報表",
            "🌐 全球 AR/AP 帳款統計"
        ]
    },
    "🏢 總務主管 (GA Manager)": {
        "allowed_pages": [
            "🏢 總務管理 (固定資產與零用金)",
            "📦 辦公用品與零用金資產"
        ]
    },
    "📋 總務專員 (GA Specialist)": {
        "allowed_pages": [
            "📦 辦公用品與零用金資產"
        ]
    },
    "🏭 廠務主管 / 工程師 (Plant Manager)": {
        "allowed_pages": [
            "🏭 廠區機台稼動 (OEE)"
        ]
    }
}

# ----------------------------------------------------
# 🏢 2. 總務部門頁面渲染邏輯 (General Affairs Module)
# ----------------------------------------------------
def render_general_affairs_page(role):
    st.title("🏢 總務管理系統 (General Affairs Management)")
    st.caption(f"當前登入身分：{role} — 專屬授權存取區域")

    tab1, tab2, tab3 = st.tabs([
        "🛋️ 門市與辦公室固定資產",
        "💵 零用金與日常費用報支",
        "📦 總務耗材與辦公用品庫存"
    ])

    with tab1:
        st.subheader("🛋️ 固定資產與設備清冊 (Fixed Assets)")
        assets_data = [
            {"資產編號": "FA-2026-001", "資產名稱": "首爾門市自動咖啡機", "保管部門": "總務部", "取得金額 (USD)": "$12,000", "折舊狀態": "正常提撥中"},
            {"資產編號": "FA-2026-002", "資產名稱": "行政區伺服器與網路設備", "保管部門": "資訊部/總務", "取得金額 (USD)": "$8,500", "折舊狀態": "正常提撥中"},
            {"資產編號": "FA-2026-003", "資產名稱": "總部會客室沙發與桌椅", "保管部門": "總務部", "取得金額 (USD)": "$4,200", "折舊狀態": "正常提撥中"}
        ]
        st.dataframe(assets_data, use_container_width=True)

    with tab2:
        st.subheader("💵 零用金與日常費用申請/審核 (Petty Cash)")
        cash_data = [
            {"單號": "PC-20260901", "申請日期": "2026-09-20", "申請人": "張專員", "項目說明": "漢陽門市清潔用品採購", "金額 (USD)": "$120.00", "審核狀態": "🟢 已核銷"},
            {"單號": "PC-20260905", "申請日期": "2026-09-24", "申請人": "李主管", "項目說明": "公務車加油與過路費", "金額 (USD)": "$85.00", "審核狀態": "🟡 待財務核決"}
        ]
        st.dataframe(cash_data, use_container_width=True)

    with tab3:
        st.subheader("📦 總務耗材庫存 (GA Supplies)")
        supplies_data = [
            {"品項": "環保紙杯 (咖啡廳用)", "目前庫存": "12,000 個", "安全庫存": "3,000 個", "狀態": "🟢 充足"},
            {"品項": "影印紙 A4", "目前庫存": "45 箱", "安全庫存": "10 箱", "狀態": "🟢 充足"}
        ]
        st.dataframe(supplies_data, use_container_width=True)

# ----------------------------------------------------
# 🚀 3. 主程式流程：身份切換與頁面過濾
# ----------------------------------------------------
def main():
    st.sidebar.title("🔐 企業權限登入與選單")

    # 1. 選擇使用者職位
    selected_role = st.sidebar.selectbox(
        "👤 請選擇您的職位 / 角色 (Role):",
        list(ROLE_PERMISSIONS.keys())
    )

    # 2. 根據職位取得被授權可見的頁面
    allowed_pages = ROLE_PERMISSIONS[selected_role]["allowed_pages"]

    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 授權功能選單")

    # 3. 僅顯示該職位允許查看的頁面
    selected_page = st.sidebar.radio("請選擇要查看的頁面：", allowed_pages)

    # 4. 動態渲染對應頁面
    if selected_page == "📈 跨國企業營運戰情室":
        exec_dash.render_executive_dashboard_page()

    elif selected_page == "📊 VPSH 八大財務報表":
        exec_dash.render_executive_dashboard_page()

    elif selected_page == "🌐 全球 AR/AP 帳款統計":
        exec_dash.render_financial_ar_ap_stats()

    elif "總務" in selected_page or "辦公用品" in selected_page:
        render_general_affairs_page(selected_role)

    elif selected_page == "🏭 廠區機台稼動 (OEE)":
        exec_dash.render_plant_oee_kpi()

    elif selected_page == "👥 人事與行政管理":
        st.title("👥 人事與行政管理頁面")
        st.info("僅限總經理與 HR 瀏覽。")

if __name__ == "__main__":
    main()
