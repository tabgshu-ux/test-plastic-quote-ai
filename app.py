import streamlit as st

def render_master_portal():
    st.markdown("## 🏢 平台總控台 - 全球企業租戶與商業授權方案管理中心")
    st.markdown("在此管理所有客戶租戶、檢視與設定「旗艦版/正式版/訂閱版」之功能費用，並可快速進入各租戶環境。")
    st.markdown("---") # 加入明確的視覺分隔線

    # 模擬的企業租戶資料庫
    if "tenant_list" not in st.session_state:
        st.session_state.tenant_list = [
            {
                "tenant_id": "TENANT-001",
                "company_name": "裕豐電機工業 (Reetech Industrial)",
                "tax_id": "0312345678",
                "plan": "🚀 企業旗艦版 (Enterprise Flagship)",
                "pricing": "$3,000 USD / 年",
                "seats": "無限席位 (Unlimited)",
                "expiry": "2027-12-31",
                "modules": ["總經理室 (Executive Office)", "管理部 (Management Dept)", "工程中心", "ISO品質合規", "ESG碳足跡"]
            },
            #未來可擴充其他租戶...
        ]

    st.markdown("### 📋 平台現有企業租戶清單（卡片式檢視）")
    
    # 搜尋過濾列
    search_query = st.text_input("🔍 快速搜尋租戶（可輸入公司名稱、代號或統編）：", placeholder="例如：裕豐 或 TENANT-001")

    st.markdown("---")

    # 迴圈遍歷所有租戶，改用獨立的「卡片外框 + 分隔線」呈現，避免點錯行
    for tenant in st.session_state.tenant_list:
        if search_query and search_query.lower() not in tenant["company_name"].lower() and search_query.lower() not in tenant["tenant_id"].lower():
            continue

        with st.container():
            # 使用醒目的區塊與邊框包覆該租戶資訊
            col_info, col_action = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"#### 🏢 {tenant['company_name']}")
                st.caption(f"**租戶代號 (ID)**：`{tenant['tenant_id']}` | **統一編號**：{tenant['tax_id']}")
                st.write(f"• **商業方案**：{tenant['plan']} (定價：{tenant['pricing']})")
                st.write(f"• **授權席位**：{tenant['seats']} | **合約到期日**：{tenant['expiry']}")
                st.write(f"• **已開通模組**： {', '.join(tenant['modules'])}")
            
            with col_action:
                st.markdown("<br>", unsafe_allow_html=True) # 調整按鈕垂直對齊
                # 獨立的進入按鈕，配有明確的租戶名稱，杜絕點錯可能性
                if st.button(f"🚀 進入 {tenant['tenant_id']}", key=f"enter_{tenant['tenant_id']}"):
                    st.session_state.current_tenant = tenant['tenant_id']
                    st.success(f"已成功切換至 {tenant['company_name']} 租戶環境！")
                    st.rerun()

            # 每個租戶卡片之間加上一條乾淨的分隔線，視覺層次分明
            st.markdown("---")
