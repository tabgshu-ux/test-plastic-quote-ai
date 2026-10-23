import streamlit as st

# 設定頁面配置
st.set_page_config(
    page_title="Global SaaS AI ERP - Platform Control Center",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.markdown("### 🌐 SaaS 總控台 (Platform Control Center)")
    st.sidebar.info("💡 *平台運營商總控路由：管理樂高拼圖模組市集、租戶模組開通、拼圖定價方案與總控權限設定。*")
    st.sidebar.markdown("---")
    
    # 總控台導航選單
    control_choice = st.sidebar.radio(
        "總控台功能導航：",
        [
            "🧩 樂高拼圖模組市集與定價管理",
            "🏢 全球租戶開通與模組派送",
            "⚙️ 總控系統設定與權限管理"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 Global SaaS AI ERP Platform Control Center.")

    # ==================== 1. 樂高拼圖模組市集與定價管理 ====================
    if "樂高拼圖模組市集" in control_choice:
        st.markdown("### 🧩 樂高拼圖模組市集與 SaaS 訂閱定價")
        st.info("💡 *在此管理所有可供租戶選購與開通的 ERP 模組、功能說明及其對應的訂閱定價方案。*")
        st.markdown("---")

        # 模擬模組與定價清單
        modules_pricing_data = [
            {"module_code": "MOD-01", "module_name": "📈 企業戰情室與 BI 分析", "category": "高階管理", "desc": "全球廠區營收、稼動率與異常警報戰情室", "price_usd": 49.0},
            {"module_code": "MOD-02", "module_name": "🌐 組織架構與匯率設定", "category": "系統底層", "desc": "多廠區、部門主檔與動態多幣別匯率引擎", "price_usd": 29.0},
            {"module_code": "MOD-03", "module_name": "👤 員工與薪資管理", "category": "人事行政", "desc": "員工主檔、合約與在地化薪資基準對接", "price_usd": 39.0},
            {"module_code": "MOD-04", "module_name": "⏱️ 請假與差勤管理", "category": "人事行政", "desc": "跨國請假申請、天數計算與打卡紀錄維護", "price_usd": 29.0},
            {"module_code": "MOD-05", "module_name": "📦 總務採購與請購單", "category": "行政總務", "desc": "多幣別請購單填寫、折合美金換算與自動拋轉", "price_usd": 39.0},
            {"module_code": "MOD-06", "module_name": "✍️ 全方位電子簽核中心", "category": "協同辦公", "desc": "跨部門表單統一審核、同意、駁回與稽核日誌", "price_usd": 59.0},
            {"module_code": "MOD-07", "module_name": "💰 跨國應付帳款 (Finance AP)", "category": "財務會計", "desc": "零用金報銷、多幣別帳款與付訖處理", "price_usd": 49.0},
            {"module_code": "MOD-08", "module_name": "🏷️ 固定資產與模具防混淆", "category": "廠務資產", "desc": "結合條碼/QR Code與實體照片，解決現場辨識痛點", "price_usd": 49.0},
            {"module_code": "MOD-09", "module_name": "🏭 MES 生產製造與 IoT 監控", "category": "生產製造", "desc": "射出機桶溫、壓力 IoT 數據監控與工單排程", "price_usd": 89.0},
            {"module_code": "MOD-10", "module_name": "📊 供應鏈與業務報價", "category": "業務營運", "desc": "依尺寸與鎖模力計算報價、多幣別支援", "price_usd": 49.0},
            {"module_code": "MOD-11", "module_name": "🧾 跨國電子發票解析", "category": "財務會計", "desc": "管理各國電子發票、稅號 MST 與 XML 憑證", "price_usd": 39.0},
            {"module_code": "MOD-12", "module_name": "📜 行政公文與合約列管", "category": "法務行政", "desc": "廠房租約、商務合約效期追蹤與提醒", "price_usd": 29.0},
            {"module_code": "MOD-13", "module_name": "🤖 AI 多模態無門檻輸入", "category": "AI 智慧", "desc": "語音轉文字口述填單、現場照片 AI 解析入庫", "price_usd": 69.0},
            {"module_code": "MOD-14", "module_name": "📊 多國動態稅制與總帳", "category": "財務會計", "desc": "動態稅率配置（如 VAT 10%）與總帳分錄", "price_usd": 59.0},
            {"module_code": "MOD-15", "module_name": "📦 全球供應鏈倉儲 (WMS)", "category": "供應鏈", "desc": "多廠區倉庫庫存、原料入庫與安全水位監控", "price_usd": 59.0},
            {"module_code": "MOD-16", "module_name": "🔌 第三方 API 閘道器配置", "category": "系統擴充", "desc": "網頁端配置第三方 API 與 JSON Schema 供 AI 調用", "price_usd": 79.0},
        ]

        import pandas as pd
        pricing_df = pd.DataFrame(modules_pricing_data)
        st.dataframe(pricing_df, use_container_width=True)

    # ==================== 2. 全球租戶開通與模組派送 ====================
    elif "全球租戶開通" in control_choice:
        st.markdown("### 🏢 全球租戶開通與樂高模組派送")
        st.info("💡 *在此管理各個企業租戶（如裕豐電機、海外分公司）的訂閱狀態，並勾選派送其專屬的 ERP 模組。*")
        st.markdown("---")

        tenants_df = pd.DataFrame([
            {"tenant_id": "TENANT-001", "company_name": "裕豐電機工業 (Reetech)", "country": "台灣 / 越南", "active_modules_count": 16, "status": "🟢 正常訂閱中"},
            {"tenant_id": "TENANT-002", "company_name": "某亞太精密科技", "country": "馬來西亞", "active_modules_count": 8, "status": "🟡 試用期中"}
        ])
        st.dataframe(tenants_df, use_container_width=True)

        st.markdown("#### ⚙️ 租戶模組動態派送設定")
        with st.form("tenant_assignment_form"):
            t_id = st.selectbox("選擇租戶", ["TENANT-001 - 裕豐電機工業", "TENANT-002 - 某亞太精密科技"])
            selected_modules = st.multiselect(
                "勾選要派送給該租戶的樂高模組：",
                ["MES 生產製造", "電子簽核中心", "員工與薪資", "總務採購", "固定資產與模具", "AI 多模態輸入"],
                default=["MES 生產製造", "電子簽核中心", "員工與薪資"]
            )
            if st.form_submit_button("🚀 儲存租戶模組授權配置", type="primary", use_container_width=True):
                st.success(f"🎉 租戶 [{t_id}] 的模組授權已成功更新！")

    # ==================== 3. 總控系統設定與權限管理 ====================
    elif "總控系統設定" in control_choice:
        st.markdown("### ⚙️ 總控平台系統設定與超級管理者權限")
        st.info("💡 *平台級參數設定、多租戶資料隔離檢核及超級管理員 (Super Admin) 帳號管理。*")
        st.markdown("---")
        
        st.markdown("#### 🔐 超級管理者清單")
        admin_df = pd.DataFrame([
            {"admin_id": 1, "username": "super_admin", "name": "許福村", "role": "Global Platform Architect", "last_login": "2026-10-23 11:00"}
        ])
        st.dataframe(admin_df, use_container_width=True)

if __name__ == "__main__":
    main()
