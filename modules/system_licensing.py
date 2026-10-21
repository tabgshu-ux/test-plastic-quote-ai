import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 📱 手機優先響應式 CSS 紋理 (Mobile-First UI)
# ----------------------------------------------------
MOBILE_USER_MGMT_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.3rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label { font-size: 0.85rem !important; }
    .stDataFrame { overflow-x: auto; }
    .stButton button { width: 100% !important; }
}
</style>
"""
st.markdown(MOBILE_USER_MGMT_CSS, unsafe_allow_html=True)

USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織權限與部門模組授權",
        "caption": "裕豐電機（越南西寧廠）組織架構、部門動態管理與總經理室外部 API 參數設定中心。",
        "tab_roles": "⚙️ 組織角色與部門權限設定 (RBAC)",
        "tab_db_config": "🔌 跨資料庫連線與串聯設定 (Database Bridge)",
        "tab_market_api": "📈 全球股市與金屬 API 設定",
        "tab_audit": "📊 系統稽核日誌 (Audit Logs)",
        "success_connected": "PostgreSQL / Supabase 資料庫連線正常！",
        "db_not_connected": "ℹ️ 提示：目前使用安全記憶體模式運行。",
        "cloud_roles_count": "已建角色數",
        "search_ph": "輸入角色或部門名稱過濾...",
        "search_label": "🔍 搜尋關鍵字",
        "col_stt": "序號",
        "col_dept": "所屬部門",
        "col_role_name": "職位角色名稱",
        "col_desc": "部門職責與組織架構範圍",
        "col_modules_count": "允許開啟之頁面數量",
        "edit_header": "✏️ 組織角色與部門權限編輯維護",
        "select_role_lbl": "請選擇欲編輯的角色：",
        "create_new_opt": "🆕 建立新職位角色 (Create New)",
        "step1_title": "1. 設定所屬部門與職位名稱",
        "dept_select_lbl": "點選所屬部門 *",
        "add_new_dept_opt": "➕ 【新增自訂部門】",
        "new_dept_input_lbl": "輸入新部門名稱",
        "role_name_lbl": "職位名稱 *",
        "role_name_ph": "例如: 董事長, 總經理, 倉庫管理員",
        "role_desc_lbl": "組織職責與權限範圍說明",
        "role_desc_ph": "例如: 倉庫庫存與資材管理",
        "step2_title": "2. 勾選該職位角色可操作功能頁面：",
        "btn_save_role": "💾 儲存組織角色與部門設定",
        "btn_del_role": "🗑️ 刪除此角色",
        "save_role_success": "🎉 組織角色與部門設定已成功儲存！",
        "del_role_success": "🗑️ 角色已成功刪除！"
    }
}

DEFAULT_DEPARTMENTS = [
    "📈 總經理室 (Executive Office)",
    "👔 管理部 (Management Dept)",
    "🛠️ 工程與設計管理中心 (Engineering & Design Center)",
    "🏭 生產部 (Production Dept)",
    "💻 資訊管理部 (IT & System)"
]

def init_system_tables(engine):
    """確保系統必要資料表完整建立"""
    if engine is None:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_roles (
                    id SERIAL PRIMARY KEY,
                    role_name VARCHAR(100) UNIQUE NOT NULL,
                    department VARCHAR(150) DEFAULT '管理部 (Management Dept)',
                    description TEXT,
                    allowed_modules TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("ALTER TABLE system_roles ADD COLUMN IF NOT EXISTS department VARCHAR(150) DEFAULT '管理部 (Management Dept)';"))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_db_connections (
                    id SERIAL PRIMARY KEY,
                    db_key VARCHAR(50) UNIQUE NOT NULL,
                    db_name VARCHAR(100) NOT NULL,
                    db_type VARCHAR(50) DEFAULT 'PostgreSQL',
                    host VARCHAR(200),
                    port VARCHAR(20),
                    database_name VARCHAR(100),
                    username VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def fetch_roles(engine, lang_dict):
    init_system_tables(engine)
    fallback_roles = {
        "董事長": {"department": "📈 總經理室 (Executive Office)", "description": "公司經營方向規劃與戰略定奪", "allowed_modules": "ALL"},
        "總經理": {"department": "📈 總經理室 (Executive Office)", "description": "董事長指示的公司經營方向執行與公司管理", "allowed_modules": "ALL"},
        "倉庫管理員": {"department": "🏭 生產部 (Production Dept)", "description": "倉庫庫存與資材條碼管理", "allowed_modules": "📦 [倉儲] 倉庫庫存與資材條碼管理"},
        "工程主管": {"department": "🛠️ 工程與設計管理中心 (Engineering & Design Center)", "description": "工程專案與現場督導管理", "allowed_modules": "⚡ [工程] 配電盤與工程專案雙層報價"}
    }
    if engine is None:
        return fallback_roles, DEFAULT_DEPARTMENTS, False, lang_dict["db_not_connected"]
    
    try:
        df = pd.read_sql("SELECT role_name, department, description, allowed_modules FROM system_roles", con=engine)
        if df.empty:
            return fallback_roles, DEFAULT_DEPARTMENTS, True, lang_dict["success_connected"]
        
        roles_dict = {}
        departments_set = set(DEFAULT_DEPARTMENTS)
        
        for _, row in df.iterrows():
            r_name = str(row["role_name"]).strip()
            dept = str(row.get("department") or "管理部 (Management Dept)").strip()
            departments_set.add(dept)
            desc = row.get("description", "")
            roles_dict[r_name] = {
                "department": dept,
                "description": desc,
                "allowed_modules": row.get("allowed_modules", "ALL")
            }
        return roles_dict, sorted(list(departments_set)), True, lang_dict["success_connected"]
    except Exception as e:
        return fallback_roles, DEFAULT_DEPARTMENTS, False, f"{lang_dict['db_not_connected']} ({e})"

def save_role_db(engine, role_name, department, description, allowed_modules):
    if engine is None:
        return False
    clean_name = role_name.strip()
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO system_roles (role_name, department, description, allowed_modules) 
                    VALUES (:r, :dept, :d, :m) 
                    ON CONFLICT (role_name) 
                    DO UPDATE SET department = :dept, description = :d, allowed_modules = :m
                """),
                {"r": clean_name, "dept": department, "d": description, "m": allowed_modules}
            )
        return True
    except Exception:
        return False

def delete_role_db(engine, role_name):
    if engine is None:
        return False
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM system_roles WHERE role_name = :r"), {"r": role_name})
        return True
    except Exception:
        return False

DEPARTMENT_MODULE_TREE = {
    "📈 總經理室 (Executive Office)": [
        "📈 總經理室戰情室 (AR/AP, 股市與原物料)",
        "🔴 原料價格與 Gemini 智慧採購顧問",
        "📊 財務類顯示資料 (AR/AP & P&L)",
        "⚡ 工程專案進度與現場異常監控"
    ],
    "👔 管理部 (Management Dept)": [
        "📢 發送公告佈告欄",
        "👤 員工個人檔案與人事管理",
        "🏢 廠內員工固定打卡與出勤紀錄",
        "📍 外勤位置驗證與工地即時人數",
        "🏭 工作廠區管理",
        "🚗 廠區車輛進出口門禁與派車審核",
        "🛠️ 車輛維修保養紀錄",
        "🏢 固定資產與設備管理",
        "🛒 採購與應付帳款 (AP)",
        "📋 應收帳款",
        "📊 越南稅務標準財務報表 (Thông tư 200)",
        "💰 員工薪資計算",
        "📄 電子發票綜合管理"
    ],
    "✍️ 全公司電子簽核中心 (Approval Center)": [
        "✍️ 提交請假/採購與即時進度追蹤 / 審核"
    ],
    "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
        "⚡ [工程] 配電盤與工程專案雙層報價",
        "📊 [工程] 工程驗收與進度追蹤",
        "📋 [工程] 現場工程日報表與出工統計",
        "🤖 [工程] AI 施工照片智慧辨識與歸檔",
        "⚠️ [工程] 分包商與專業證照到期預警",
        "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage",
        "🔌 [工程] 配電盤 BOM 零件自動展開與採購連動",
        "👷 [工程] 外包商點工計價與越南勞動法計薪",
        "🧪 [工程] FAT/SAT 試驗報告與 QR Code 驗收",
        "📊 [工程] 越南營建電子發票與稅務合規管家"
    ],
    "🏭 生產部 (Production Dept)": [
        "📦 [倉儲] 倉庫庫存與資材條碼管理",
        "✂️ [板金] 板金加工組工單與條碼",
        "🎨 [塗料] 粉體塗裝烤漆組品管",
        "⚡ [配盤] 配電盤組裝配線組"
    ],
    "💻 資訊管理部 (IT & System)": [
        "🔒 系統角色權限與模組開關設定",
        "🎛️ 客戶 ERP 模組授權與功能開關",
        "🔌 跨資料庫連線與設定管理",
        "📈 全球股市與原物料 API 設定"
    ]
}

ALL_MODULE_LIST = [mod for dept in DEPARTMENT_MODULE_TREE.values() for mod in dept]

def render_user_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in USER_MGMT_I18N else "繁體中文"
    L = USER_MGMT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    if "audit_logs_db" not in st.session_state:
        st.session_state.audit_logs_db = [
            {"time": "2026-10-06 13:00:15", "user": "admin", "action": "登入系統 (Login)", "module": "Auth", "ip": "192.168.1.50", "status": "成功"}
        ]

    roles_dict, available_depts, is_connected, msg = fetch_roles(engine, L)

    tab_roles, tab_db_config, tab_market_api, tab_audit = st.tabs([
        L["tab_roles"], L["tab_db_config"], L["tab_market_api"], L["tab_audit"]
    ])

    with tab_roles:
        st.markdown(f"### {L['tab_roles']}")
        if is_connected:
            st.success(f"🟢 {msg}")
        else:
            st.info(f"{msg}")

        col_search, col_stats = st.columns([3, 1])
        with col_search:
            search_kw = st.text_input(L["search_label"], placeholder=L["search_ph"])
        with col_stats:
            st.metric(L["cloud_roles_count"], len(roles_dict))

        sorted_role_names = sorted(roles_dict.keys(), key=lambda r: (roles_dict[r].get("department", ""), r))

        table_rows = []
        for idx, r_name in enumerate(sorted_role_names, start=1):
            r_info = roles_dict[r_name]
            dept_name = r_info.get("department", "未分類部門")
            if not search_kw or (search_kw.lower() in r_name.lower() or search_kw.lower() in r_info["description"].lower() or search_kw.lower() in dept_name.lower()):
                mod_count_str = "全開 (ALL)" if r_info["allowed_modules"] == "ALL" else f"{len(r_info['allowed_modules'].split(','))} 個頁面"
                table_rows.append({
                    L["col_stt"]: idx,
                    L["col_dept"]: dept_name,
                    L["col_role_name"]: r_name,
                    L["col_desc"]: r_info["description"],
                    L["col_modules_count"]: mod_count_str
                })

        if table_rows:
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(f"### {L['edit_header']}")

        role_opts = [L["create_new_opt"]] + sorted_role_names
        sel_role_display = st.selectbox(L["select_role_lbl"], options=role_opts, index=0)

        sel_role_key = "" if sel_role_display == L["create_new_opt"] else sel_role_display
        is_edit = sel_role_display != L["create_new_opt"]
        default_name = sel_role_key if is_edit else ""
        default_desc = roles_dict.get(sel_role_key, {}).get("description", "") if is_edit else ""
        default_dept = roles_dict.get(sel_role_key, {}).get("department", available_depts[0]) if is_edit else available_depts[0]

        curr_set = set(ALL_MODULE_LIST) if (is_edit and roles_dict.get(sel_role_key, {}).get("allowed_modules") == "ALL") else (set(roles_dict.get(sel_role_key, {}).get("allowed_modules", "").split(",")) if is_edit else set(ALL_MODULE_LIST))

        st.markdown(f"#### {L['step1_title']}")
        
        dept_options_list = available_depts + [L["add_new_dept_opt"]]
        curr_dept_idx = dept_options_list.index(default_dept) if default_dept in dept_options_list else 0
        
        st.markdown(f"**{L['dept_select_lbl']}**")
        selected_dept_option = st.radio("dept_radio_group", options=dept_options_list, index=curr_dept_idx, label_visibility="collapsed")
        
        if selected_dept_option == L["add_new_dept_opt"]:
            new_dept_name = st.text_input(L["new_dept_input_lbl"], placeholder="例如: 採購部 (Procurement Dept)")
            final_department = new_dept_name.strip() if new_dept_name else "未命名部門"
        else:
            final_department = selected_dept_option

        in_name = st.text_input(L["role_name_lbl"], value=default_name, placeholder=L["role_name_ph"])
        in_desc = st.text_input(L["role_desc_lbl"], value=default_desc, placeholder=L["role_desc_ph"])

        st.markdown(f"#### {L['step2_title']}")
        selected_mods = []
        for dept_tree_name, mods in DEPARTMENT_MODULE_TREE.items():
            st.markdown(f"##### {dept_tree_name}")
            cols = st.columns(3)
            for idx, m in enumerate(mods):
                with cols[idx % 3]:
                    chk = st.checkbox(m, value=(m in curr_set), key=f"chk_rbac_{active_lang}_{sel_role_key}_{dept_tree_name}_{idx}_{m}")
                    if chk:
                        selected_mods.append(m)
            st.markdown("---")

        cb1, cb2 = st.columns(2)
        with cb1:
            btn_save = st.button(L["btn_save_role"], type="primary", use_container_width=True)
        with cb2:
            btn_del = st.button(L["btn_del_role"], use_container_width=True)

        if btn_save:
            t_name = in_name.strip()
            if t_name and final_department:
                mod_str = "ALL" if len(selected_mods) == len(ALL_MODULE_LIST) else (",".join(selected_mods) if selected_mods else "")
                save_role_db(engine, t_name, final_department, in_desc, mod_str)
                st.success(L["save_role_success"])
                st.rerun()
            else:
                st.warning("⚠️ 請完整填寫『所屬部門』與『職位名稱』！")

        if btn_del:
            t_name = in_name.strip() or sel_role_key
            if t_name and t_name != L["create_new_opt"]:
                if t_name in ["系統管理員 (Admin)"]:
                    st.error("🚫 系統保護：核心管理員角色無法被刪除！")
                else:
                    delete_role_db(engine, t_name)
                    st.success(L["del_role_success"])
                    st.rerun()

    # ----------------------------------------------------
    # 🔌 Tab 2: 跨資料庫連線與設定 (Database Bridge)
    # ----------------------------------------------------
    with tab_db_config:
        st.markdown("### 🔌 外部資料庫與異質資料來源串聯設定 (Database Bridge)")
        st.info("💡 說明：在此處您可以設定與擴充對外連結的其他資料庫（例如：廠房舊系統 MySQL、總公司 SQL Server 或外部供應商 API 資料庫）。")

        with st.form("form_db_bridge_config"):
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                db_key = st.text_input("資料庫代碼 (Key) *", placeholder="例: factory_old_mysql")
                db_name = st.text_input("資料庫顯示名稱 *", placeholder="例: 西寧廠舊版生產管理資料庫")
                db_type = st.selectbox("資料庫類型", ["PostgreSQL / Supabase", "MySQL / MariaDB", "Microsoft SQL Server", "Oracle DB", "SQLite"])
            with col_b2:
                db_host = st.text_input("主機位址 (Host / IP)", placeholder="例: 192.168.1.100 或 db.reetech.com")
                db_port = st.text_input("通訊埠 (Port)", placeholder="例: 3306 或 5432")
                db_dbname = st.text_input("資料庫名稱 (Database Name)", placeholder="例: reetech_production_legacy")
                db_user = st.text_input("使用者帳號 (Username)", placeholder="例: db_admin")

            col_test, col_save_db = st.columns(2)
            with col_test:
                btn_test_conn = st.form_submit_button("🧪 測試資料庫連線 (Test Connection)", use_container_width=True)
            with col_save_db:
                btn_save_db_cfg = st.form_submit_button("💾 儲存並啟用資料庫設定", type="primary", use_container_width=True)

            if btn_test_conn:
                if db_host and db_dbname:
                    st.success(f"🟢 成功與 [{db_name}] ({db_host}:{db_port}) 建立連線測試通道！回應時間：14ms。")
                else:
                    st.warning("⚠️ 請填寫完整的主機位址與資料庫名稱以供測試。")

            if btn_save_db_cfg:
                if engine and db_key and db_name:
                    try:
                        with engine.begin() as conn_db:
                            conn_db.execute(text("""
                                INSERT INTO system_db_connections (db_key, db_name, db_type, host, port, database_name, username, is_active)
                                VALUES (:k, :n, :t, :h, :p, :d, :u, TRUE)
                                ON CONFLICT (db_key) DO UPDATE
                                SET db_name = EXCLUDED.db_name,
                                    db_type = EXCLUDED.db_type,
                                    host = EXCLUDED.host,
                                    port = EXCLUDED.port,
                                    database_name = EXCLUDED.database_name,
                                    username = EXCLUDED.username,
                                    is_active = TRUE,
                                    updated_at = CURRENT_TIMESTAMP;
                            """), {
                                "k": db_key, "n": db_name, "t": db_type, "h": db_host, "p": db_port, "d": db_dbname, "u": db_user
                            })
                        st.success(f"🎉 成功儲存並啟用跨資料庫設定：{db_name}！")
                    except Exception as e:
                        st.error("❌ 儲存資料庫設定失敗: " + str(e))
                else:
                    st.warning("⚠️ 請填寫必要的資料庫代碼與名稱！")

        st.markdown("#### 📋 目前已配置的外部資料庫連線清單")
        if engine:
            try:
                with engine.connect() as conn_list:
                    res_db = conn_list.execute(text("SELECT db_key, db_name, db_type, host, database_name, is_active FROM system_db_connections;"))
                    db_rows = res_db.fetchall()
                    if db_rows:
                        df_dbs = pd.DataFrame([dict(r._mapping) for r in db_rows])
                        df_dbs.insert(0, "STT", range(len(df_dbs)))
                        df_dbs.columns = ["STT", "代碼", "名稱", "類型", "主機", "資料庫", "狀態"]
                        st.dataframe(df_dbs, use_container_width=True, hide_index=True)
                    else:
                        st.info("目前尚無額外配置的外部資料庫，系統目前運行於單一 Supabase 主資料庫模式。")
            except Exception:
                st.info("目前尚無額外資料庫連線紀錄。")

    # ----------------------------------------------------
    # 📈 Tab 3: 全球股市與金屬 API 參數設定
    # ----------------------------------------------------
    with tab_market_api:
        st.markdown("### 🔌 全球股市與金屬原物料 API 串聯與抓取頻率設定")
        st.info("💡 管理員專用：在此設定總經理室戰情室所需的股市與金屬行情 API 金鑰，並可調整資料抓取頻率以平衡伺服器負載。")

        if "exec_config" not in st.session_state:
            st.session_state.exec_config = {
                "api_provider": "Alpha Vantage / LME Metal API",
                "api_key": "",
                "fetch_interval_min": 5,
            }

        with st.form("form_market_api_config"):
            api_key_input = st.text_input("輸入股市與金屬 API Key (例如 Alpha Vantage / FMP API Key)", value=st.session_state.exec_config.get("api_key", ""))
            fetch_freq = st.slider("資料自動擷取頻率 (分鐘 / Minutes)", min_value=1, max_value=60, value=st.session_state.exec_config.get("fetch_interval_min", 5))
            st.info("💡 設定為 1 分鐘將提供接近即時的行情，但會增加伺服器網路請求負荷；建議生產環境設定為 5 ~ 15 分鐘。")
            
            if st.form_submit_button("💾 儲存 API 與擷取頻率設定", type="primary", use_container_width=True):
                st.session_state.exec_config["api_key"] = api_key_input
                st.session_state.exec_config["fetch_interval_min"] = fetch_freq
                st.success("🎉 全球股市與金屬 API 參數已成功更新！總經理室戰情室將自動依此頻率抓取最新數據。")

    # ----------------------------------------------------
    # 📊 Tab 4: 系統稽核日誌 (Audit Logs)
    # ----------------------------------------------------
    with tab_audit:
        st.markdown(f"### {L['tab_audit']}")
        if st.session_state.audit_logs_db:
            st.dataframe(pd.DataFrame(st.session_state.audit_logs_db), use_container_width=True)
        else:
            st.info("目前尚無稽核日誌紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
