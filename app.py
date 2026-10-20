elif "🧩 樂高積木式模組拼圖與功能開關" in menu_choice:
    st.markdown("## 🧩 樂高積木式模組拼圖與功能開關 (Feature Toggles)")
    st.info("💡 說明：請先在左側選取要設定的【主部門 / 系統】，再為該部門勾選對應的 ERP 功能模組拼圖。")

    # 左右雙欄設計：左側選部門，右側設功能
    col_dept, col_modules = st.columns([1, 2])

    with col_dept:
        st.markdown("### 🏢 選擇目標部門")
        selected_department = st.radio(
            "請選擇要配置的部門：",
            [
                "👑 總經理室 (Executive Office)",
                "📊 管理部 (Management Dept)",
                "🛡️ 全公司電子簽核中心 (Approval Center)",
                "⚙️ 工程與設計中心 (Engineering Dept)",
                "🏭 生產部 (Production Dept)",
                "💻 資訊管理部 (IT & System)"
            ]
        )
        st.markdown("---")
        st.markdown(f"📍 **目前正在設定**：\n`{selected_department}`")

    with col_modules:
        st.markdown(f"### 🧩 【{selected_department.split(' ')[1]}】的模組拼圖開關")
        st.markdown("請勾選此部門可使用的系統模組：")
        
        # 模擬不同部門的預設權限狀態
        c1, c2 = st.columns(2)
        with c1:
            mod1 = st.checkbox("📦 智能進銷存與庫存管理", value=True, key=f"{selected_department}_m1")
            mod2 = st.checkbox("💰 財務會計與應收付管理", value=True, key=f"{selected_department}_m2")
            mod3 = st.checkbox("🏭 生產排程與BOM表控管", value=False, key=f"{selected_department}_m3")
        with c2:
            mod4 = st.checkbox("🤝 CRM 客戶關係與報價模組", value=True, key=f"{selected_department}_m4")
            mod5 = st.checkbox("📊 商業智慧 BI 儀表板", value=True, key=f"{selected_department}_m5")
            mod6 = st.checkbox("⚙️ 設備維護與物聯網監控", value=False, key=f"{selected_department}_m6")

        st.markdown("---")
        if st.button(f"💾 儲存【{selected_department.split(' ')[1]}】的模組設定", type="primary", use_container_width=True):
            st.success(f"✅ 已成功將設定儲存至 [{selected_department}]！該部門成員下次登入時將自動生效。")
