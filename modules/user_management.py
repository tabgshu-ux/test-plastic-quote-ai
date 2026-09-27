import datetime
import os
import pandas as pd
import psycopg2
import streamlit as st

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "global_erp"),
        user=os.getenv("DB_USER", "erp_user"),
        password=os.getenv("DB_PASSWORD", "your_password"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432")
    )

def render_user_management_page(sub_option="🏢 跨國廠區與子公司管理"):
    st.title("💻 資訊/IT 部門 — 權限與系統管理中心")
    st.caption("管理集團部門結構、全球廠區據點擴建，以及跨國 ERP 模組授權 (RBAC) 與全系統操作軌跡稽核")

    # ----------------------------------------------------
    # 🗄️ 1. 初始化 Session State (全域操作稽核日誌與系統數據)
    # ----------------------------------------------------
    if "system_audit_logs" not in st.session_state:
        st.session_state.system_audit_logs = [
            {
                "log_id": "AUD-20260927-001",
                "timestamp": "2026-09-27 14:32:10",
                "year": "2026",
                "month": "09",
                "day": "27",
                "operator": "admin (Alex Chen)",
                "dept_module": "💻 資訊/IT",
                "action_type": "🔑 權限變更",
                "target": "ga_user (李總務)",
                "detail": "開通 [🏢 總務與倉儲] 模組編輯權限",
                "status": "🟢 正常"
            },
            {
                "log_id": "AUD-20260927-002",
                "timestamp": "2026-09-27 11:15:00",
                "year": "2026",
                "month": "09",
                "day": "27",
                "operator": "ga_user (李總務)",
                "dept_module": "📦 倉儲管理",
                "action_type": "📤 領料出庫",
                "target": "RM-PP-001",
                "detail": "領料出庫 500.0 kg，條碼比對通過 (4710123456012)",
                "status": "🟢 正常"
            },
            {
                "log_id": "AUD-20260926-005",
                "timestamp": "2026-09-26 16:45:22",
                "year": "2026",
                "month": "09",
                "day": "26",
                "operator": "hr_manager (張主管)",
                "dept_module": "👥 人事/行政",
                "action_type": "➕ 新增員工",
                "target": "VN-004 (Nguyễn Văn B)",
                "detail": "建立越南廠新員工檔案，綁定起薪 9,000,000 VND",
                "status": "🟢 正常"
            },
            {
                "log_id": "AUD-20260815-003",
                "timestamp": "2026-08-15 09:10:05",
                "year": "2026",
                "month": "08",
                "day": "15",
                "operator": "accountant (王會計)",
                "dept_module": "🧾 財務管理",
                "action_type": "📄 應付帳款核銷",
                "target": "AP-202608-012",
                "detail": "核銷越南廠原料採購單據 42,000,000 VND",
                "status": "🟢 正常"
            },
            {
                "log_id": "AUD-20260110-001",
                "timestamp": "2026-01-10 08:00:12",
                "year": "2026",
                "month": "01",
                "day": "10",
                "operator": "system_job",
                "dept_module": "💻 資訊/IT",
                "action_type": "⚙️ 系統備份",
                "target": "System Database",
                "detail": "完成年度系統資料庫例行自動備份",
                "status": "🟢 正常"
            }
        ]

    # 自動同步倉儲或其它模組連線過來的紀錄至 IT 全域日誌
    if "inventory_logs" in st.session_state and st.session_state.inventory_logs:
        existing_log_ids = {log["log_id"] for log in st.session_state.system_audit_logs}
        for inv in st.session_state.inventory_logs:
            if inv.get("log_id") and inv["log_id"] not in existing_log_ids:
                dt_str = inv.get("date", str(datetime.date.today()))
                parts = dt_str.split("-")
                yr = parts[0] if len(parts) > 0 else "2026"
                mo = parts[1] if len(parts) > 1 else "09"
                dy = parts[2] if len(parts) > 2 else "27"
                
                st.session_state.system_audit_logs.append({
                    "log_id": inv["log_id"],
                    "timestamp": dt_str + " 10:00:00",
                    "year": yr,
                    "month": mo,
                    "day": dy,
                    "operator": inv.get("operator", "System User"),
                    "dept_module": "📦 倉儲管理",
                    "action_type": inv.get("type", "庫存變更"),
                    "target": str(inv.get("item_code", "-")) + " (" + str(inv.get("item_name", "")) + ")",
                    "detail": str(inv.get("remark", "")) + " [數量: " + str(inv.get("change_qty", 0)) + " " + str(inv.get("unit", "")) + "]",
                    "status": "🚨 異常" if "異常" in inv.get("type", "") or "盤虧" in inv.get("type", "") else "🟢 正常"
                })

    # 四大功能頁籤 (包含原始 3 大功能 + 強化之系統操作軌跡與稽核)
    tabs = st.tabs([
        "🏢 跨國廠區與子公司管理", 
        "👥 人員帳號與網頁授權", 
        "🔒 模組權限矩陣設定",
        "📜 系統全域操作軌跡與稽核 (Audit Trail)"
    ])

    # ----------------------------------------------------
    # TAB 1: 跨國廠區與子公司動態管理 (保留完整原始功能)
    # ----------------------------------------------------
    with tabs[0]:
        st.subheader("🌐 全球廠區與海外子公司據點維護")
        st.caption("支援跨國企業動態擴張，隨時新增海外新設廠房、研發中心或子公司")

        col_f1, col_f2 = st.columns([1, 1])

        if "factory_list" not in st.session_state:
            st.session_state.factory_list = [
                {"id": "FACT-TW-01", "name": "🇹🇼 台灣總部研發中心", "country": "台灣", "currency": "TWD", "revenue": "NT$ 12.5M", "status": "🟢 營運中"},
                {"id": "FACT-DG-01", "name": "🇨🇳 東莞一廠 (橡膠/塑膠)", "country": "中國", "currency": "RMB", "revenue": "¥ 3.4M", "status": "🟢 營運中"},
                {"id": "FACT-BH-01", "name": "🇻🇳 越南平陽廠 (鞋底/大底)", "country": "越南", "currency": "VND", "revenue": "₫ 12.8B", "status": "🟢 營運中"}
            ]

        with col_f1:
            st.markdown("#### ➕ 新增海外廠房/分公司據點")
            with st.form("add_factory_form", clear_on_submit=True):
                f_id = st.text_input("廠區代碼*", placeholder="例如: FACT-ID-01 (印尼廠)")
                f_name = st.text_input("廠區/子公司名稱*", placeholder="例如: 🇮🇩 印尼爪哇新廠")
                f_country = st.text_input("所在國家/區域*", placeholder="例如: 印尼 (Indonesia)")
                f_currency = st.selectbox("當地記帳本位幣*", ["USD", "VND", "TWD", "RMB", "IDR", "MXN", "EUR"])
                f_status = st.selectbox("廠區營運狀態", ["🟢 營運中", "🏗️ 建廠/試產中", "🟡 規劃中"])

                if st.form_submit_button("💾 儲存並將新廠區加入集團戰情室"):
                    if not f_id or not f_name:
                        st.warning("請輸入廠區代碼與名稱！")
                    else:
                        st.session_state.factory_list.append({
                            "id": f_id, "name": f_name, "country": f_country, 
                            "currency": f_currency, "revenue": "$0.00", "status": f_status
                        })
                        
                        # 寫入 IT 操作軌跡
                        now_dt = datetime.datetime.now()
                        st.session_state.system_audit_logs.append({
                            "log_id": "AUD-" + now_dt.strftime('%Y%m%d-%H%M%S'),
                            "timestamp": now_dt.strftime('%Y-%m-%d %H:%M:%S'),
                            "year": str(now_dt.year),
                            "month": str(now_dt.month).zfill(2),
                            "day": str(now_dt.day).zfill(2),
                            "operator": "IT Admin",
                            "dept_module": "💻 資訊/IT",
                            "action_type": "🏭 新增廠區據點",
                            "target": f_name,
                            "detail": f"新增廠區代碼 [{f_id}]，幣別: {f_currency}，狀態: {f_status}",
                            "status": "🟢 正常"
                        })
                        
                        st.success(f"🎉 新廠區據點 [{f_name}] 已成功建立！集團戰情室與 KPI 面板已同步更新連動。")
                        st.rerun()

        with col_f2:
            st.markdown("#### 🌍 現有全球廠區據點一覽")
            df_factories = pd.DataFrame(st.session_state.factory_list)
            st.dataframe(df_factories, use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: 人員帳號與網頁授權 (保留完整原始功能)
    # ----------------------------------------------------
    with tabs[1]:
        st.subheader("新增人員與選單授權設定")
        col_form, col_list = st.columns([1, 1])

        with col_form:
            st.markdown("#### ➕ 新增/編輯系統帳號與權限")
            with st.form("add_user_form", clear_on_submit=True):
                username = st.text_input("登入帳號 (Email/工號)*", placeholder="alex.chen@global.com")
                full_name = st.text_input("使用者姓名*", placeholder="陳大明")
                password = st.text_input("初始密碼*", type="password")
                dept = st.selectbox("歸屬部門", ["IT 資訊部", "董事長室/總經理室", "業務部", "研發部", "財務部", "人事行政部"])
                role = st.selectbox("系統角色", ["Admin (系統管理員)", "Manager (主管/董事長)", "User (一般員工)"])

                st.markdown("**🔓 可開啟之網頁/模組授權**")
                auth_exec = st.checkbox("📈 營運戰情室 (Executive)", value=True)
                auth_sales = st.checkbox("💼 業務/行銷 (Sales & Marketing)", value=True)
                auth_rd = st.checkbox("🛠️ 研發/技術 (R&D & Engineering)", value=True)
                auth_finance = st.checkbox("🧾 財務 (Finance)", value=False)
                auth_hr = st.checkbox("👥 人事/行政 (HR & Admin)", value=False)

                submit_user = st.form_submit_button("💾 儲存並啟用帳號與授權")
                if submit_user:
                    if not username or not full_name:
                        st.warning("請填寫帳號與姓名！")
                    else:
                        now_dt = datetime.datetime.now()
                        st.session_state.system_audit_logs.append({
                            "log_id": "AUD-" + now_dt.strftime('%Y%m%d-%H%M%S'),
                            "timestamp": now_dt.strftime('%Y-%m-%d %H:%M:%S'),
                            "year": str(now_dt.year),
                            "month": str(now_dt.month).zfill(2),
                            "day": str(now_dt.day).zfill(2),
                            "operator": "IT Admin",
                            "dept_module": "💻 資訊/IT",
                            "action_type": "👤 新增/修改帳號",
                            "target": f"{full_name} ({username})",
                            "detail": f"角色: {role} | 部門: {dept}",
                            "status": "🟢 正常"
                        })
                        st.success(f"✅ 使用者 [{full_name}] 授權設定成功！已同步紀錄於 IT 全域日誌。")

        with col_list:
            st.markdown("#### 📋 目前全集團帳號清單")
            mock_users = pd.DataFrame({
                "帳號": ["admin@global.com", "ceo@global.com", "sales01@global.com"],
                "姓名": ["IT 管理員", "董事長", "Alex Chen"],
                "部門": ["資訊部", "董事長室", "業務部"],
                "角色": ["Admin", "Manager", "User"]
            })
            st.dataframe(mock_users, use_container_width=True)

    # ----------------------------------------------------
    # TAB 3: 模組權限矩陣設定 (保留完整原始功能)
    # ----------------------------------------------------
    with tabs[2]:
        st.subheader("🔒 角色與模組 Access Control List (ACL) 矩陣")
        acl_df = pd.DataFrame({
            "模組頁面名稱": ["📈 營運戰情室", "💼 業務/行銷", "🛠️ 研發/技術", "🧾 財務", "👥 人事/行政", "💻 資訊/IT"],
            "Admin (管理員)": [True, True, True, True, True, True],
            "Manager (高層/主管)": [True, True, True, True, True, False],
            "Sales (業務同仁)": [False, True, False, False, False, False]
        })
        st.data_editor(acl_df, use_container_width=True)

    # ----------------------------------------------------
    # TAB 4: 🆕 全系統操作軌跡與稽核中心 (含年月日多維度搜尋)
    # ----------------------------------------------------
    with tabs[3]:
        st.subheader("📜 系統操作與異動歷史紀錄 (System Audit Logs)")
        st.caption("即時追蹤與稽核全系統跨模組操作軌跡，支援依「年、月、日」分類篩選與全文關鍵字搜尋。")

        logs_data = st.session_state.system_audit_logs

        st.markdown("##### 🔎 紀錄搜尋與日期時間分類過濾")
        col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1, 1, 1])
        
        with col_f1:
            search_kw = st.text_input("🔍 關鍵字搜尋 (帳號/動作/品項/備註)：", "", key="audit_kw_search").strip().lower()
            
        available_years = sorted(list({str(l["year"]) for l in logs_data}), reverse=True)
        with col_f2:
            selected_year = st.selectbox("📅 選擇年份 (Year)", ["全部年份 (All)"] + available_years)

        months_list = ["全部月份 (All)"] + [str(i).zfill(2) for i in range(1, 13)]
        with col_f3:
            selected_month = st.selectbox("📆 選擇月份 (Month)", months_list)

        with col_f4:
            selected_module = st.selectbox("🏢 篩選系統模組", ["全部模組 (All)", "📦 倉儲管理", "👥 人事/行政", "🧾 財務管理", "💻 資訊/IT", "💼 業務/行銷"])

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            use_exact_date = st.checkbox("🎯 啟用特定單日精確過濾 (Specific Day Filter)", value=False)
        with col_d2:
            exact_date_val = st.date_input("選擇特定年月日", value=datetime.date(2026, 9, 27), disabled=not use_exact_date)

        st.markdown("---")

        # ------------------------------------------------
        # 📊 資料過濾與呈現邏輯
        # ------------------------------------------------
        filtered_logs = []
        for log in logs_data:
            match_kw = True
            if search_kw:
                combined_text = (
                    str(log["log_id"]) + " " +
                    str(log["operator"]) + " " +
                    str(log["dept_module"]) + " " +
                    str(log["action_type"]) + " " +
                    str(log["target"]) + " " +
                    str(log["detail"])
                ).lower()
                match_kw = search_kw in combined_text

            match_year = (selected_year == "全部年份 (All)" or str(log["year"]) == selected_year)
            match_month = (selected_month == "全部月份 (All)" or str(log["month"]) == selected_month)
            match_module = (selected_module == "全部模組 (All)" or log["dept_module"] == selected_module)

            match_exact_date = True
            if use_exact_date:
                match_exact_date = (str(log["year"]) == str(exact_date_val.year) and 
                                    str(log["month"]).zfill(2) == str(exact_date_val.month).zfill(2) and 
                                    str(log["day"]).zfill(2) == str(exact_date_val.day).zfill(2))

            if match_kw and match_year and match_month and match_module and match_exact_date:
                filtered_logs.append({
                    "紀錄編號": log["log_id"],
                    "時間 (YYYY-MM-DD HH:MM:SS)": log["timestamp"],
                    "年份": log["year"],
                    "月份": log["month"] + "月",
                    "日期": log["day"] + "日",
                    "操作人員 (User)": log["operator"],
                    "系統模組": log["dept_module"],
                    "動作類型": log["action_type"],
                    "操作對象/標的": log["target"],
                    "詳細內容與備註": log["detail"],
                    "狀態": log.get("status", "🟢 正常")
                })

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📜 總記錄筆數", str(len(logs_data)) + " 筆")
        col_m2.metric("🔍 符合條件紀錄", str(len(filtered_logs)) + " 筆")
        col_m3.metric("🚨 警示與異動事件", str(len([l for l in filtered_logs if "🚨" in l["狀態"]])) + " 筆")

        if filtered_logs:
            df_display = pd.DataFrame(filtered_logs)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("💡 查無符合目前日期（年/月/日）或關鍵字條件的操作紀錄。")

def show(sub_option="🏢 跨國廠區與子公司管理"):
    render_user_management_page(sub_option)

def main(sub_option="🏢 跨國廠區與子公司管理"):
    render_user_management_page(sub_option)
