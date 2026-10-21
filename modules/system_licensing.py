import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 商業 ERP 授權、Storage 與外部 API 串聯管理模組多語系字典 (i18n)
# ----------------------------------------------------
LICENSING_I18N = {
    "繁體中文": {
        "title": "🔑 IT 商業授權、Storage 與外部 API 資訊管理中心",
        "caption": "管理外部企業租戶（Tenant）之合約方案、模組開關、到期日，以及系統雲端 Storage 儲存庫路徑與外部 API 串聯設定。",
        "tab_tenants": "🏢 客戶租戶與授權總覽",
        "tab_add_tenant": "➕ 新增客戶租戶合約",
        "tab_manage_tenant": "⚙️ 編輯客戶模組權限與到期日",
        "tab_storage": "💾 系統 Storage 儲存庫路徑設定",
        "tab_market_api": "🔌 外部 API 與資料庫串聯 (股市/金屬)",
        "table_header": "📋 全系統客戶租戶授權與模組開關清冊",
        "no_records": "目前尚無客戶租戶授權紀錄。",
        "col_index": "STT",
        "col_company": "客戶公司名稱",
        "col_tax": "統一編號 / 稅號",
        "col_plan": "授權方案",
        "col_seats": "席位數",
        "col_expiry": "合約到期日",
        "col_modules": "已啟用模組開關",
        "col_status": "狀態"
    },
    "Tiếng Việt": {
        "title": "🔑 Trung tâm Bản quyền Thương mại, Storage & API",
        "caption": "Quản lý hợp đồng khách hàng, bật/tắt module, cấu hình đường dẫn Storage và API hệ thống.",
        "tab_tenants": "🏢 Tổng quan Khách hàng & Bản quyền",
        "tab_add_tenant": "➕ Thêm Khách hàng mới",
        "tab_manage_tenant": "⚙️ Chỉnh sửa Phân quyền",
        "tab_storage": "💾 Cấu hình đường dẫn Storage",
        "tab_market_api": "🔌 Cấu hình API ngoài (Chứng khoán/Kim loại)",
        "table_header": "📋 Danh sách khách hàng và module",
        "no_records": "Chưa có bản ghi khách hàng nào.",
        "col_index": "STT",
        "col_company": "Tên công ty",
        "col_tax": "Mã số thuế",
        "col_plan": "Gói cước",
        "col_seats": "Số ghế",
        "col_expiry": "Ngày hết hạn",
        "col_modules": "Module đang bật",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "🔑 Commercial Licensing, Storage & External API Center",
        "caption": "Manage enterprise tenant contracts, module feature flags, cloud storage paths, and external API integrations.",
        "tab_tenants": "🏢 Tenants & Licensing Overview",
        "tab_add_tenant": "➕ Register New Tenant Contract",
        "tab_manage_tenant": "⚙️ Edit Tenant Modules & Expiry",
        "tab_storage": "💾 System Storage Path Settings",
        "tab_market_api": "🔌 External API & Database Bridge",
        "table_header": "📋 Enterprise Tenant License & Module Matrix",
        "no_records": "No tenant license records found.",
        "col_index": "No.",
        "col_company": "Company Name",
        "col_tax": "Tax ID / MST",
        "col_plan": "Subscription Plan",
        "col_seats": "User Seats",
        "col_expiry": "Expiry Date",
        "col_modules": "Enabled Modules",
        "col_status": "Status"
    }
}

def render_system_licensing_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = LICENSING_I18N.get(active_lang, LICENSING_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 1. 初始化企業租戶授權資料庫
    if "tenant_licensing_db" not in st.session_state or not isinstance(st.session_state.tenant_licensing_db, list):
        st.session_state.tenant_licensing_db = [
            {
                "tenant_id": "TENANT-001",
                "company_name": "裕豐電機工業 (Reetech Industrial)",
                "tax_id": "0312345678",
                "plan": "企業旗艦統包版 (Enterprise)",
                "max_seats": 50,
                "expiry_date": "2027-12-31",
                "modules": ["人事薪資", "倉庫資材", "工程報價與BOM", "電子發票與財務", "車輛門禁", "總經理室戰情室"],
                "status": "🟢 正常運行 (Active)"
            },
            {
                "tenant_id": "TENANT-002",
                "company_name": "Công ty TNHH Xây lắp Tân Thuận",
                "tax_id": "0309876543",
                "plan": "基礎標準版 (Standard)",
                "max_seats": 15,
                "expiry_date": "2026-12-31",
                "modules": ["人事薪資", "倉庫資材"],
                "status": "🟡 試用期 (Trial)"
            }
        ]

    # 2. 初始化系統 Storage 配置
    if "system_storage_config" not in st.session_state:
        st.session_state.system_storage_config = {
            "storage_provider": "本地伺服器儲存 (Local NAS / Server)",
            "storage_path": "./storage_data/engineering_drawings/",
            "max_file_size_mb": 100.0,
            "auto_backup": True
        }

    # 3. 初始化總經理室戰情室所需的外部股市與金屬原物料 API 設定
    if "exec_config" not in st.session_state:
        st.session_state.exec_config = {
            "api_provider": "Alpha Vantage / LME Metal API",
            "api_key": "",
            "fetch_interval_min": 5, # 預設每 5 分鐘抓取一次
        }

    # 建立多分頁架構（嚴格限制僅資訊管理員可在此修改串接設定，一般員工無法觸及）
    tab_tenants, tab_add_tenant, tab_manage_tenant, tab_storage, tab_market_api = st.tabs([
        L["tab_tenants"], 
        L["tab_add_tenant"], 
        L["tab_manage_tenant"], 
        L["tab_storage"], 
        L["tab_market_api"]
    ])

    # ----------------------------------------------------
    # Tab 1: 客戶租戶與授權總覽
    # ----------------------------------------------------
    with tab_tenants:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.tenant_licensing_db:
            display_data = []
            for idx, tenant in enumerate(st.session_state.tenant_licensing_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    "客戶代碼": tenant["tenant_id"],
                    L["col_company"]: tenant["company_name"],
                    L["col_tax"]: tenant["tax_id"],
                    L["col_plan"]: tenant["plan"],
                    L["col_seats"]: f"{tenant['max_seats']} 席",
                    L["col_expiry"]: tenant["expiry_date"],
                    L["col_modules"]: ", ".join(tenant["modules"]),
                    L["col_status"]: tenant["status"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    # ----------------------------------------------------
    # Tab 2: 新增客戶租戶合約
    # ----------------------------------------------------
    with tab_add_tenant:
        st.markdown("### ➕ 註冊新企業客戶租戶與授權方案")
        with st.form("form_add_tenant_contract"):
            c1, c2 = st.columns(2)
            with c1:
                t_name = st.text_input("客戶公司名稱 (Company Name) *", value="Vietnam Power Engineering Corp")
                t_tax = st.text_input("統一編號 / 稅號 (Tax ID / MST)", value="0301122334")
                t_plan = st.selectbox("商業授權方案", ["基礎標準版 (Standard)", "進階製造版 (Advanced)", "企業旗艦統包版 (Enterprise)"])
            with c2:
                t_seats = st.number_input("最高授權使用者席位數 (Max Seats)", min_value=1, max_value=500, value=25)
                t_expiry = st.date_input("合約到期日 (Expiry Date)", value=datetime.date(2027, 12, 31))
                t_status = st.selectbox("合約狀態", ["🟢 正常運行 (Active)", "🟡 試用期 (Trial)", "🔴 授權到期 (Expired)"])

            st.markdown("---")
            st.markdown("##### 🧩 啟用模組功能開關 (Module Feature Flags)")
            m1, m2, m3 = st.columns(3)
            with m1:
                mod_hr = st.checkbox("👤 人事薪資與打卡考勤", value=True)
                mod_wh = st.checkbox("📦 倉庫庫存與資材管理", value=True)
            with m2:
                mod_eng = st.checkbox("⚡ 工程專案雙層報價與 BOM", value=True)
                mod_fin = st.checkbox("📊 財務應付帳款與電子發票", value=False)
            with m3:
                mod_veh = st.checkbox("🚗 廠區車輛維修與門禁保全", value=False)
                mod_exec = st.checkbox("📈 總經理室戰情室 (股市/原物料/損益)", value=True)

            if st.form_submit_button("🚀 建立新客戶租戶授權", type="primary", use_container_width=True):
                if t_name:
                    new_tenant_id = f"TENANT-{len(st.session_state.tenant_licensing_db)+1:03d}"
                    active_modules = []
                    if mod_hr: active_modules.append("人事薪資")
                    if mod_wh: active_modules.append("倉庫資材")
                    if mod_eng: active_modules.append("工程報價與BOM")
                    if mod_fin: active_modules.append("電子發票與財務")
                    if mod_veh: active_modules.append("車輛門禁")
                    if mod_exec: active_modules.append("總經理室戰情室")

                    st.session_state.tenant_licensing_db.append({
                        "tenant_id": new_tenant_id,
                        "company_name": t_name,
                        "tax_id": t_tax,
                        "plan": t_plan,
                        "max_seats": t_seats,
                        "expiry_date": str(t_expiry),
                        "modules": active_modules,
                        "status": t_status
                    })
                    st.success(f"🎉 成功建立新客戶租戶 [{t_name}]！代碼：`{new_tenant_id}`")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫客戶公司名稱！")

    # ----------------------------------------------------
    # Tab 3: 編輯客戶模組權限與到期日
    # ----------------------------------------------------
    with tab_manage_tenant:
        st.markdown("### ⚙️ 調整客戶租戶模組權限、到期日與席位")
        if st.session_state.tenant_licensing_db:
            tenant_opts = [f"{t['tenant_id']} - {t['company_name']}" for t in st.session_state.tenant_licensing_db]
            sel_target_tenant = st.selectbox("選擇要調整的企業客戶", tenant_opts)
            target_tid = sel_target_tenant.split(" - ")[0]
            target_obj = next((t for t in st.session_state.tenant_licensing_db if t["tenant_id"] == target_tid), None)

            if target_obj:
                with st.form("form_edit_tenant"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        ed_name = st.text_input("客戶公司名稱", value=target_obj["company_name"])
                        ed_plan = st.selectbox("授權方案", ["基礎標準版 (Standard)", "進階製造版 (Advanced)", "企業旗艦統包版 (Enterprise)"], index=0 if "標準" in target_obj["plan"] else (1 if "進階" in target_obj["plan"] else 2))
                        ed_seats = st.number_input("最高授權席位數", min_value=1, max_value=500, value=target_obj["max_seats"])
                    with ec2:
                        ed_expiry = st.text_input("合約到期日 (YYYY-MM-DD)", value=target_obj["expiry_date"])
                        status_list = ["🟢 正常運行 (Active)", "🟡 試用期 (Trial)", "🔴 授權到期 (Expired)"]
                        ed_status = st.selectbox("合約狀態", status_list, index=0 if "正常" in target_obj["status"] else (1 if "試用" in target_obj["status"] else 2))

                    st.markdown("---")
                    st.markdown("##### 🧩 調整模組啟用開關")
                    current_mods = target_obj["modules"]
                    ed_mod_hr = st.checkbox("👤 人事薪資與打卡考勤", value="人事薪資" in current_mods)
                    ed_mod_wh = st.checkbox("📦 倉庫庫存與資材管理", value="倉庫資材" in current_mods)
                    ed_mod_eng = st.checkbox("⚡ 工程專案雙層報價與 BOM", value="工程報價與BOM" in current_mods)
                    ed_mod_fin = st.checkbox("📊 財務應付帳款與電子發票", value="電子發票與財務" in current_mods)
                    ed_mod_veh = st.checkbox("🚗 廠區車輛維修與門禁保全", value="車輛門禁" in current_mods)
                    ed_mod_exec = st.checkbox("📈 總經理室戰情室 (股市/原物料/損益)", value="總經理室戰情室" in current_mods)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        save_btn = st.form_submit_button("💾 儲存客戶授權變更", type="primary", use_container_width=True)
                    with col_b2:
                        del_btn = st.form_submit_button("🔥 終止並刪除此客戶合約", type="secondary", use_container_width=True)

                    if save_btn:
                        updated_mods = []
                        if ed_mod_hr: updated_mods.append("人事薪資")
                        if ed_mod_wh: updated_mods.append("倉庫資材")
                        if ed_mod_eng: updated_mods.append("工程報價與BOM")
                        if ed_mod_fin: updated_mods.append("電子發票與財務")
                        if ed_mod_veh: updated_mods.append("車輛門禁")
                        if ed_mod_exec: updated_mods.append("總經理室戰情室")

                        target_obj["company_name"] = ed_name
                        target_obj["plan"] = ed_plan
                        target_obj["max_seats"] = ed_seats
                        target_obj["expiry_date"] = ed_expiry
                        target_obj["status"] = ed_status
                        target_obj["modules"] = updated_mods
                        st.success(f"🎉 客戶 [{ed_name}] 的授權方案與模組開關已成功更新！")
                        st.rerun()

                    if del_btn:
                        st.session_state.tenant_licensing_db = [t for t in st.session_state.tenant_licensing_db if t["tenant_id"] != target_tid]
                        st.success(f"🗑️ 客戶租戶 [{target_tid}] 合約已終止並自系統中移除！")
                        st.rerun()
        else:
            st.info("目前尚無客戶租戶可供修改。")

    # ----------------------------------------------------
    # Tab 4: 系統 Storage 儲存庫路徑設定
    # ----------------------------------------------------
    with tab_storage:
        st.markdown("### 💾 系統雲端 Storage 儲存庫路徑與設定")
        st.info("💡 管理員專用：在此設定全系統設計圖檔、照片與附件儲存的實體或雲端 Storage 路徑。")
        
        with st.form("form_storage_settings"):
            cfg = st.session_state.system_storage_config
            s_provider = st.selectbox("儲存媒介類型 (Storage Type)", ["本地伺服器儲存 (Local NAS / Server)", "AWS S3 雲端儲存槽 (Cloud S3)", "Google Cloud Storage (GCS)"], index=0 if "本地" in cfg["storage_provider"] else 1)
            s_path = st.text_input("Storage 實體掛載路徑或 Bucket 名稱", value=cfg["storage_path"])
            s_max_size = st.number_input("單一上傳檔案大小上限 (MB)", min_value=1.0, max_value=1000.0, value=cfg["max_file_size_mb"])
            s_backup = st.checkbox("啟用每日自動備份至異地備份槽", value=cfg["auto_backup"])

            if st.form_submit_button("💾 儲存 Storage 系統設定", type="primary", use_container_width=True):
                st.session_state.system_storage_config = {
                    "storage_provider": s_provider,
                    "storage_path": s_path,
                    "max_file_size_mb": s_max_size,
                    "auto_backup": s_backup
                }
                st.success("🎉 系統 Storage 儲存庫路徑與設定已成功更新！")
                st.rerun()

    # ----------------------------------------------------
    # Tab 5: 外部 API 與資料庫串聯 (股市/金屬原物料 API 設定) —— 資訊管理部專屬安全防護
    # ----------------------------------------------------
    with tab_market_api:
        st.markdown("### 🔌 全球股市與金屬原物料 API 串聯與抓取頻率設定")
        st.warning("🔒 【資安防護提示】本區域專屬於「資訊管理部 / IT 管理員」，用以設定總經理室戰情室所需的外部 API 金鑰與更新頻率，一般員工無權限修改。")

        with st.form("form_market_api_config"):
            exec_cfg = st.session_state.exec_config
            api_key_input = st.text_input("輸入股市與金屬原物料 API Key (例如 Alpha Vantage / LME Metal API Key)", value=exec_cfg.get("api_key", ""))
            fetch_freq = st.slider("資料自動擷取頻率 (分鐘 / Minutes)", min_value=1, max_value=60, value=exec_cfg.get("fetch_interval_min", 5))
            st.info("💡 設定為 1 分鐘將提供接近即時的行情，但會增加伺服器網路請求負荷；建議生產環境設定為 5 ~ 15 分鐘。")
            
            if st.form_submit_button("💾 儲存 API 與擷取頻率設定", type="primary", use_container_width=True):
                st.session_state.exec_config["api_key"] = api_key_input
                st.session_state.exec_config["fetch_interval_min"] = fetch_freq
                st.success("🎉 全球股市與金屬原物料 API 參數已成功更新！總經理室戰情室將自動依此頻率抓取最新數據。")

# 相容性包裝函式
def show(lang="繁體中文", **kwargs):
    render_system_licensing_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_system_licensing_page(lang, **kwargs)

def render_system_licensing(*args, **kwargs):
    render_system_licensing_page(*args, **kwargs)

def render_licensing_control_page(*args, **kwargs):
    render_system_licensing_page(*args, **kwargs)
