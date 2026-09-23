import streamlit as st
import pandas as pd

# ----------------------------------------------------
# 🌐 資產管理模組多語系字典 (i18n Dictionary for Asset Module)
# ----------------------------------------------------
ASSET_I18N = {
    "繁體中文": {
        "page_title": "📦 跨國資產與模具管理系統",
        "sub_title": "管理台灣總部、東莞廠與平陽廠之射出機台、模具與固定資產",
        "tab_overview": "📑 資產總覽與查詢",
        "tab_add": "➕ 新增資產",
        "tab_maintenance": "🛠️ 維修保養登記",
        "section_list": "廠區資產清單",
        "filter_site": "廠區篩選",
        "filter_category": "資產類別",
        "filter_status": "資產狀態",
        "option_all": "全部",
        "col_id": "資產編號",
        "col_name": "資產名稱",
        "col_category": "分類",
        "col_site": "廠區",
        "col_status": "狀態",
        "col_currency": "計價幣別",
        "col_cost": "採購金額",
        "status_in_use": "在用",
        "status_repair": "維修中",
        "status_idle": "閒置",
        "cat_molding": "射出機",
        "cat_mold": "模具",
        "cat_aux": "週邊設備",
        "site_bh": "BH (平陽)",
        "site_dg": "DG (東莞)",
        "site_tw": "TW (台灣總部)",
        "add_heading": "➕ 登記新固定資產或模具",
        "label_asset_name": "資產/模具名稱：",
        "label_site": "存放廠區：",
        "label_cost": "採購/開發金額 (USD)：",
        "btn_add": "💾 登錄至跨國資產資料庫",
        "add_success": "🎉 成功登錄新資產！",
        "maint_heading": "🛠️ 模具與機台維修保養紀錄",
        "label_asset_select": "選擇維修/保養資產：",
        "label_maint_type": "保養項目：",
        "type_routine": "定期保養 (Clean & Grease)",
        "type_repair": "故障修繕 (Core/Cavity Repair)",
        "type_mod": "模具修改 (Engineering Change)",
        "label_notes": "保養說明與維修紀錄：",
        "btn_maint_save": "💾 儲存維修保養紀錄",
        "maint_success": "✅ 已成功記錄保養履歷！"
    },
    "Tiếng Việt": {
        "page_title": "📦 Quản Lý Tài Sản & Khuôn Mẫu Đa Quốc Gia",
        "sub_title": "Quản lý máy ép phun, khuôn mẫu và tài sản cố định tại Trụ sở Đài Loan, Nhà máy Đông Hoản và Nhà máy Bình Dương",
        "tab_overview": "📑 Tổng quan & Tra cứu tài sản",
        "tab_add": "➕ Thêm tài sản mới",
        "tab_maintenance": "🛠️ Nhật ký bảo trì & Sửa chữa",
        "section_list": "Danh Sách Tài Sản Nhà Máy",
        "filter_site": "Lọc theo nhà máy",
        "filter_category": "Phân loại tài sản",
        "filter_status": "Trạng thái tài sản",
        "option_all": "Tất cả",
        "col_id": "Mã tài sản",
        "col_name": "Tên tài sản",
        "col_category": "Phân loại",
        "col_site": "Nhà máy",
        "col_status": "Trạng thái",
        "col_currency": "Tiền tệ",
        "col_cost": "Giá trị mua",
        "status_in_use": "Đang sử dụng",
        "status_repair": "Đang bảo trì",
        "status_idle": "Nhàn rỗi",
        "cat_molding": "Máy ép phun",
        "cat_mold": "Khuôn mẫu",
        "cat_aux": "Thiết bị phụ trợ",
        "site_bh": "BH (Bình Dương)",
        "site_dg": "DG (Đông Hoản)",
        "site_tw": "TW (Đài Loan)",
        "add_heading": "➕ Đăng ký tài sản cố định hoặc khuôn mới",
        "label_asset_name": "Tên tài sản / khuôn mẫu:",
        "label_site": "Vị trí nhà máy:",
        "label_cost": "Giá trị mua / phát triển (USD):",
        "btn_add": "💾 Lưu vào CSDL tài sản đa quốc gia",
        "add_success": "🎉 Đã thêm thành công tài sản mới!",
        "maint_heading": "🛠️ Nhật ký bảo trì máy móc & khuôn mẫu",
        "label_asset_select": "Chọn tài sản bảo trì / sửa chữa:",
        "label_maint_type": "Hạng mục bảo trì:",
        "type_routine": "Bảo trì định kỳ (Vệ sinh & Bôi trơn)",
        "type_repair": "Sửa chữa sự cố (Sửa lõi/lòng khuôn)",
        "type_mod": "Sửa đổi khuôn (Thay đổi kỹ thuật ECN)",
        "label_notes": "Chi tiết bảo trì & Nội dung sửa chữa:",
        "btn_maint_save": "💾 Lưu nhật ký bảo trì",
        "maint_success": "✅ Đã ghi nhận lịch sử bảo trì thành công!"
    },
    "English": {
        "page_title": "📦 Global Assets & Mold Management System",
        "sub_title": "Manage injection machines, molds, and fixed assets across Taiwan HQ, Dongguan, and Binh Duong plants",
        "tab_overview": "📑 Asset Overview & Search",
        "tab_add": "➕ Add New Asset",
        "tab_maintenance": "🛠️ Maintenance & Repair Logs",
        "section_list": "Plant Asset List",
        "filter_site": "Filter by Plant",
        "filter_category": "Asset Category",
        "filter_status": "Asset Status",
        "option_all": "All",
        "col_id": "Asset ID",
        "col_name": "Asset Name",
        "col_category": "Category",
        "col_site": "Plant Site",
        "col_status": "Status",
        "col_currency": "Currency",
        "col_cost": "Purchase Cost",
        "status_in_use": "In Use",
        "status_repair": "Under Repair",
        "status_idle": "Idle",
        "cat_molding": "Molding Machine",
        "cat_mold": "Mold / Tooling",
        "cat_aux": "Auxiliary Equipment",
        "site_bh": "BH (Binh Duong)",
        "site_dg": "DG (Dongguan)",
        "site_tw": "TW (Taiwan HQ)",
        "add_heading": "➕ Register New Fixed Asset or Mold",
        "label_asset_name": "Asset / Mold Name:",
        "label_site": "Plant Location:",
        "label_cost": "Purchase Cost (USD):",
        "btn_add": "💾 Save to Global Asset DB",
        "add_success": "🎉 Successfully added new asset!",
        "maint_heading": "🛠️ Machine & Mold Maintenance Logs",
        "label_asset_select": "Select Asset for Maintenance:",
        "label_maint_type": "Maintenance Type:",
        "type_routine": "Routine Service (Clean & Grease)",
        "type_repair": "Breakdown Repair (Core/Cavity Repair)",
        "type_mod": "Mold Modification (ECN)",
        "label_notes": "Maintenance Notes & Actions Taken:",
        "btn_maint_save": "💾 Save Maintenance Record",
        "maint_success": "✅ Successfully recorded maintenance log!"
    },
    "简体中文": {
        "page_title": "📦 跨国资产与模具管理系统",
        "sub_title": "管理台湾总部、东莞厂与平阳厂之注塑机台、模具与固定资产",
        "tab_overview": "📑 资产总览与查询",
        "tab_add": "➕ 新增资产",
        "tab_maintenance": "🛠️ 维修保养登记",
        "section_list": "厂区资产清单",
        "filter_site": "厂区筛选",
        "filter_category": "资产类别",
        "filter_status": "资产状态",
        "option_all": "全部",
        "col_id": "资产编号",
        "col_name": "资产名称",
        "col_category": "分类",
        "col_site": "厂区",
        "col_status": "状态",
        "col_currency": "计价币别",
        "col_cost": "采购金额",
        "status_in_use": "在用",
        "status_repair": "维修中",
        "status_idle": "闲置",
        "cat_molding": "注塑机",
        "cat_mold": "模具",
        "cat_aux": "周边设备",
        "site_bh": "BH (平阳)",
        "site_dg": "DG (东莞)",
        "site_tw": "TW (台湾总部)",
        "add_heading": "➕ 登记新固定资产或模具",
        "label_asset_name": "资产/模具名称：",
        "label_site": "存放厂区：",
        "label_cost": "采购/开发金额 (USD)：",
        "btn_add": "💾 登录至跨国资产数据库",
        "add_success": "🎉 成功登录新资产！",
        "maint_heading": "🛠️ 模具与机台维修保养纪录",
        "label_asset_select": "选择维修/保养资产：",
        "label_maint_type": "保养项目：",
        "type_routine": "定期保养 (Clean & Grease)",
        "type_repair": "故障修缮 (Core/Cavity Repair)",
        "type_mod": "模具修改 (Engineering Change)",
        "label_notes": "保养说明与维修纪录：",
        "btn_maint_save": "💾 保存维修保养纪录",
        "maint_success": "✅ 已成功记录保养履历！"
    },
    "Bahasa Indonesia": {
        "page_title": "📦 Manajemen Aset Global & Cetakan",
        "sub_title": "Kelola mesin cetak, cetakan, dan aset tetap di Kantor Pusat Taiwan, Pabrik Dongguan, dan Pabrik Binh Duong",
        "tab_overview": "📑 Ikhtisar & Pencarian Aset",
        "tab_add": "➕ Tambah Aset Baru",
        "tab_maintenance": "🛠️ Log Pemeliharaan & Perbaikan",
        "section_list": "Daftar Aset Pabrik",
        "filter_site": "Filter Berdasarkan Pabrik",
        "filter_category": "Kategori Aset",
        "filter_status": "Status Aset",
        "option_all": "Semua",
        "col_id": "ID Aset",
        "col_name": "Nama Aset",
        "col_category": "Kategori",
        "col_site": "Pabrik",
        "col_status": "Status",
        "col_currency": "Mata Uang",
        "col_cost": "Biaya Pembelian",
        "status_in_use": "Mata Uang",
        "status_repair": "Dalam Perbaikan",
        "status_idle": "Khas",
        "cat_molding": "Mesin Cetak",
        "cat_mold": "Cetakan / Tooling",
        "cat_aux": "Peralatan Pendukung",
        "site_bh": "BH (Binh Duong)",
        "site_dg": "DG (Dongguan)",
        "site_tw": "TW (Pusat Taiwan)",
        "add_heading": "➕ Daftarkan Aset Tetap atau Cetakan Baru",
        "label_asset_name": "Nama Aset / Cetakan:",
        "label_site": "Lokasi Pabrik:",
        "label_cost": "Biaya Pembelian (USD):",
        "btn_add": "💾 Simpan ke DB Aset Global",
        "add_success": "🎉 Berhasil menambahkan aset baru!",
        "maint_heading": "🛠️ Log Pemeliharaan Mesin & Cetakan",
        "label_asset_select": "Pilih Aset untuk Pemeliharaan:",
        "label_maint_type": "Jenis Pemeliharaan:",
        "type_routine": "Layanan Rutin (Bersihkan & Gemuk)",
        "type_repair": "Perbaikan Kerusakan (Inti/Rongga)",
        "type_mod": "Modifikasi Cetakan (ECN)",
        "label_notes": "Catatan Pemeliharaan & Tindakan:",
        "btn_maint_save": "💾 Simpan Catatan Pemeliharaan",
        "maint_success": "✅ Berhasil mencatat log pemeliharaan!"
    }
}

def get_asset_lang_dict():
    """獲取當前系統語言字典，預設繁體中文"""
    lang = st.session_state.get("lang", "繁體中文")
    return ASSET_I18N.get(lang, ASSET_I18N["繁體中文"])

def render_asset_management_page(sub_option=None):
    L = get_asset_lang_dict()
    
    st.title(L["page_title"])
    st.caption(L["sub_title"])

    # 初始化資產資料庫
    if "asset_db" not in st.session_state:
        st.session_state.asset_db = [
            {"id": "EQ-BH-001", "name": "NISSEI 250T Molding Machine", "category": L["cat_molding"], "site": L["site_bh"], "status": L["status_in_use"], "currency": "USD", "cost": "$85,000"},
            {"id": "MOLD-BH-088", "name": "Jordan 10 Outsole Mold", "category": L["cat_mold"], "site": L["site_bh"], "status": L["status_in_use"], "currency": "USD", "cost": "$7,200"},
            {"id": "EQ-DG-003", "name": "Oil Temperature Controller", "category": L["cat_aux"], "site": L["site_dg"], "status": L["status_repair"], "currency": "RMB", "cost": "¥24,000"}
        ]

    tab_overview, tab_add, tab_maint = st.tabs([L["tab_overview"], L["tab_add"], L["tab_maintenance"]])

    # ----------------------------------------------------
    # 頁籤 1：資產總覽與動態篩選
    # ----------------------------------------------------
    with tab_overview:
        st.markdown(f"### {L['section_list']}")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            site_filter = st.selectbox(L["filter_site"], [L["option_all"], L["site_bh"], L["site_dg"], L["site_tw"]], key="asset_site_filter")
        with col_f2:
            cat_filter = st.selectbox(L["filter_category"], [L["option_all"], L["cat_molding"], L["cat_mold"], L["cat_aux"]], key="asset_cat_filter")
        with col_f3:
            status_filter = st.selectbox(L["filter_status"], [L["option_all"], L["status_in_use"], L["status_repair"], L["status_idle"]], key="asset_status_filter")

        # 執行過濾邏輯
        filtered_assets = st.session_state.asset_db
        if site_filter != L["option_all"]:
            filtered_assets = [a for a in filtered_assets if a["site"] == site_filter]
        if cat_filter != L["option_all"]:
            filtered_assets = [a for a in filtered_assets if a["category"] == cat_filter]
        if status_filter != L["option_all"]:
            filtered_assets = [a for a in filtered_assets if a["status"] == status_filter]

        df_assets = pd.DataFrame(filtered_assets)
        if not df_assets.empty:
            df_assets.columns = [L["col_id"], L["col_name"], L["col_category"], L["col_site"], L["col_status"], L["col_currency"], L["col_cost"]]
            st.dataframe(df_assets, use_container_width=True)
        else:
            st.info("ℹ️ No assets found for selected filter.")

    # ----------------------------------------------------
    # 頁籤 2：新增資產登錄
    # ----------------------------------------------------
    with tab_add:
        st.markdown(f"### {L['add_heading']}")
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            new_name = st.text_input(L["label_asset_name"], value="TOSHIBA 350T Injection Machine", key="input_new_asset_name")
            new_cat = st.selectbox(L["filter_category"], [L["cat_molding"], L["cat_mold"], L["cat_aux"]], key="select_new_asset_cat")
        with col_a2:
            new_site = st.selectbox(L["label_site"], [L["site_bh"], L["site_dg"], L["site_tw"]], key="select_new_asset_site")
            new_cost = st.number_input(L["label_cost"], min_value=100.0, value=95000.0, step=1000.0, key="input_new_asset_cost")

        if st.button(L["btn_add"], type="primary", key="btn_save_new_asset"):
            new_id = f"EQ-NEW-{len(st.session_state.asset_db)+1:03d}"
            st.session_state.asset_db.append({
                "id": new_id,
                "name": new_name,
                "category": new_cat,
                "site": new_site,
                "status": L["status_in_use"],
                "currency": "USD",
                "cost": f"${new_cost:,.0f}"
            })
            st.success(L["add_success"])
            st.rerun()

    # ----------------------------------------------------
    # 頁籤 3：維修保養紀錄
    # ----------------------------------------------------
    with tab_maint:
        st.markdown(f"### {L['maint_heading']}")
        
        asset_options = [f"{a['id']} — {a['name']}" for a in st.session_state.asset_db]
        selected_asset = st.selectbox(L["label_asset_select"], asset_options, key="select_maint_asset")
        maint_type = st.selectbox(L["label_maint_type"], [L["type_routine"], L["type_repair"], L["type_mod"]], key="select_maint_type")
        maint_notes = st.text_area(L["label_notes"], value="Replaced hydraulic seal ring and lubricated guide pins.", key="input_maint_notes")

        if st.button(L["btn_maint_save"], type="primary", key="btn_save_maint"):
            st.success(L["maint_success"])

def show(sub_option=None):
    render_asset_management_page(sub_option)

def main(sub_option=None):
    render_asset_management_page(sub_option)
