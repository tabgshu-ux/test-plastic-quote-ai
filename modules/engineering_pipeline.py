import re
import datetime
import pandas as pd
import streamlit as st

# ==============================================================================
# 🌐 1. 多語系字典 (i18n)
# ==============================================================================
ENGINEERING_I18N = {
    "繁體中文": {
        "page_title": "🛠️ 工程部 — 配電盤與資材工程估價系統",
        "sub_title": "🛠️ 配電盤元件/銅排選配、工程工時估算與即時報價單總合系統",
        "sub_caption": "專供工程主管與業務使用：自由選擇配電盤所需材料、規格數量與加工工時，系統自動動態計算小計與最終報價總金額。",
        "sec_specs": "📝 1. 工程基本資訊與專案規格描述",
        "lbl_project_name": "工程專案名稱 / 客戶名稱 *",
        "lbl_spec_desc": "專案需求與規格說明",
        "sec_materials": "📦 2. 配電盤材料與資材費用選配 (下拉選擇與動態小計)",
        "col_item": "選擇資材品項/規格",
        "col_unit_price": "單價",
        "col_qty": "數量",
        "col_subtotal": "金額小計",
        "btn_add_row": "➕ 新增資材品項",
        "sec_labor": "⚙️️ 3. 工程加工、組裝與現場施工費用",
        "lbl_busbar_hours": "銅排加工與組裝工時 (小時)",
        "lbl_assembly_hours": "配電盤配線與測試工時 (小時)",
        "lbl_hourly_rate": "工程工時單價",
        "sec_summary": "💰 4. 報價單金額總合與正式預估報價單",
        "lbl_mat_total": "資材費用總合",
        "lbl_labor_total": "工程加工/工時費用總合",
        "lbl_grand_total": "報價總價 (Grand Total)",
        "btn_gen_quote": "🚀 產生正式工程報價單",
        "btn_download_quote": "📥 下載正式工程報價單 (.txt)"
    },
    "Tiếng Việt": {
        "page_title": "🛠️ Khối Kỹ Thuật — Hệ thống Báo giá Tủ điện & Vật tư",
        "sub_title": "🛠️ Dự toán Vật tư Tủ điện, Nhân công & Tổng hợp Bảng Báo giá",
        "sub_caption": "Dành cho quản lý kỹ thuật và kinh doanh: Tự do chọn vật tư, quy cách, số lượng và giờ công để hệ thống tự động tính tổng báo giá.",
        "sec_specs": "📝 1. Thông tin Dự án & Quy cách Kỹ thuật",
        "lbl_project_name": "Tên Dự án / Tên Khách hàng *",
        "lbl_spec_desc": "Mô tả yêu cầu kỹ thuật",
        "sec_materials": "📦 2. Chọn Vật tư Tủ điện & Thành tiền (Tự động tính)",
        "col_item": "Chọn vật tư / quy cách",
        "col_unit_price": "Đơn giá",
        "col_qty": "Số lượng",
        "col_subtotal": "Thành tiền",
        "btn_add_row": "➕ Thêm vật tư",
        "sec_labor": "⚙️ 3. Chi phí Gia công, Lắp ráp & Thi công",
        "lbl_busbar_hours": "Giờ công gia công thanh cái đồng (Giờ)",
        "lbl_assembly_hours": "Giờ công đấu nối & kiểm thử (Giờ)",
        "lbl_hourly_rate": "Đơn giá giờ công",
        "sec_summary": "💰 4. Tổng hợp Báo giá & Xuất Bảng Báo Giá Chính Thức",
        "lbl_mat_total": "Tổng chi phí vật tư",
        "lbl_labor_total": "Tổng chi phí gia công / nhân công",
        "lbl_grand_total": "TỔNG CỘNG BÁO GIÁ",
        "btn_gen_quote": "🚀 Xuất Bảng Báo Giá Chính Thức",
        "btn_download_quote": "📥 Tải Bảng Báo Giá (.txt)"
    },
    "English": {
        "page_title": "🛠️ R&D Engineering — Switchgear Quotation System",
        "sub_title": "🛠️ Material Selection, Labor Estimation & Quotation Summary",
        "sub_caption": "Select materials, specifications, quantities, and processing labor hours for dynamic quotation calculation.",
        "sec_specs": "📝 1. Project Information & Specifications",
        "lbl_project_name": "Project / Customer Name *",
        "lbl_spec_desc": "Technical Description",
        "sec_materials": "📦 2. Material Selection & Cost Breakdown",
        "col_item": "Select Item / Spec",
        "col_unit_price": "Unit Price",
        "col_qty": "Qty",
        "col_subtotal": "Subtotal",
        "btn_add_row": "➕ Add Material Item",
        "sec_labor": "⚙️ 3. Fabrication & Labor Costs",
        "lbl_busbar_hours": "Busbar Fabrication Labor (Hours)",
        "lbl_assembly_hours": "Wiring & Testing Labor (Hours)",
        "lbl_hourly_rate": "Labor Hourly Rate",
        "sec_summary": "💰 4. Quotation Grand Total & Summary",
        "lbl_mat_total": "Total Material Cost",
        "lbl_labor_total": "Total Labor Cost",
        "lbl_grand_total": "Grand Total",
        "btn_gen_quote": "🚀 Generate Official Quotation",
        "btn_download_quote": "📥 Download Quotation (.txt)"
    }
}

# 預設材料庫下拉資料
DEFAULT_MATERIAL_CATALOG = [
    {"code": "CU-BUS-10100", "name": "高純度導電銅排 Busbar 10x100mm (6m/支)", "unit": "kg", "unit_price": 12.5, "currency": "USD"},
    {"code": "CU-BUS-08080", "name": "高純度導電銅排 Busbar 8x80mm (6m/支)", "unit": "kg", "unit_price": 11.0, "currency": "USD"},
    {"code": "CB-MCCB-100A", "name": "塑殼斷路器 MCCB 100A (Schneider Electric)", "unit": "pcs", "unit_price": 45.0, "currency": "USD"},
    {"code": "CB-ACB-2000A", "name": "空氣斷路器 ACB 2000A (Schneider Electric)", "unit": "pcs", "unit_price": 1850.0, "currency": "USD"},
    {"code": "CAB-SECC-001", "name": "配電盤鍍鋅鋼板外殼 RAL 7035 粉體塗裝", "unit": "套", "unit_price": 320.0, "currency": "USD"},
    {"code": "POWDER-RAL7035", "name": "粉體塗裝烤漆粉 RAL 7035 淺灰色", "unit": "kg", "unit_price": 1.8, "currency": "USD"},
    {"code": "WIRE-CU-35MM", "name": "耐熱電氣線材 35mm²", "unit": "米", "unit_price": 4.5, "currency": "USD"},
    {"code": "TERMINAL-SET", "name": "絕緣壓著端子與線槽套件", "unit": "組", "unit_price": 25.0, "currency": "USD"}
]

def get_i18n():
    lang = st.session_state.get("current_lang", "繁體中文")
    return ENGINEERING_I18N.get(lang, ENGINEERING_I18N["繁體中文"])

# ==============================================================================
# 🖥️ 主畫面渲染
# ==============================================================================
def render_engineering_page(*args, **kwargs):
    L = get_i18n()
    
    st.title(L["page_title"])
    st.caption(L["sub_caption"])

    # 1. 專案基本資訊
    st.markdown(f"### {L['sec_specs']}")
    c1, c2 = st.columns([1, 1])
    with c1:
        prj_name = st.text_input(L["lbl_project_name"], value="西寧紡織廠 2000A 主配電櫃新建工程")
    with c2:
        currency = st.selectbox("計價幣別", ["USD", "VND", "TWD"], index=0)
    
    prj_desc = st.text_area(L["lbl_spec_desc"], value="包含高純度銅排母線加工、2000A ACB 空氣斷路器組裝與現場高壓耐壓測試。")

    st.markdown("---")

    # 2. 下拉式材料選配與費用小計
    st.markdown(f"### {L['sec_materials']}")

    if "quote_items" not in st.session_state:
        st.session_state.quote_items = [
            {"item_code": "CU-BUS-10100", "qty": 150.0},
            {"item_code": "CB-ACB-2000A", "qty": 2.0},
            {"item_code": "CAB-SECC-001", "qty": 1.0}
        ]

    # 材料選擇對照字典
    catalog_dict = {f"[{item['code']}] {item['name']} (${item['unit_price']} USD/{item['unit']})": item for item in DEFAULT_MATERIAL_CATALOG}
    catalog_labels = list(catalog_dict.keys())

    calculated_materials = []
    total_material_cost = 0.0

    st.caption("請由下拉式選單選擇所需的配電盤資材，並填入數量：")
    
    # 動態材料列表顯示
    for idx, row in enumerate(st.session_state.quote_items):
        col_m1, col_m2, col_m3, col_m4 = st.columns([3, 1, 1, 1])
        
        # 尋找當前項目的預設索引
        current_catalog_item = next((k for k, v in catalog_dict.items() if v["code"] == row["item_code"]), catalog_labels[0])
        selected_label = col_m1.selectbox(f"資材品項 #{idx+1}", catalog_labels, index=catalog_labels.index(current_catalog_item), key=f"mat_select_{idx}")
        
        mat_info = catalog_dict[selected_label]
        row["item_code"] = mat_info["code"]
        
        unit_p = mat_info["unit_price"]
        qty = col_m2.number_input(f"數量 ({mat_info['unit']})", min_value=0.1, value=float(row["qty"]), step=1.0, key=f"mat_qty_{idx}")
        row["qty"] = qty
        
        subtotal = unit_p * qty
        col_m3.text_input(f"單價 (${mat_info['currency']})", value=f"${unit_p:,.2f}", disabled=True, key=f"mat_p_{idx}")
        col_m4.text_input("小計 (USD)", value=f"${subtotal:,.2f}", disabled=True, key=f"mat_sub_{idx}")

        total_material_cost += subtotal
        calculated_materials.append({
            "code": mat_info["code"],
            "name": mat_info["name"],
            "unit": mat_info["unit"],
            "unit_price": unit_p,
            "qty": qty,
            "subtotal": subtotal
        })

    if st.button(L["btn_add_row"]):
        st.session_state.quote_items.append({"item_code": "CU-BUS-10100", "qty": 10.0})
        st.rerun()

    st.markdown("---")

    # 3. 加工工時與施工費用
    st.markdown(f"### {L['sec_labor']}")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        busbar_hours = st.number_input(L["lbl_busbar_hours"], min_value=0.0, value=24.0, step=1.0)
    with col_l2:
        assembly_hours = st.number_input(L["lbl_assembly_hours"], min_value=0.0, value=16.0, step=1.0)
    with col_l3:
        hourly_rate = st.number_input(L["lbl_hourly_rate"] + " ($/hr)", min_value=0.0, value=15.0, step=1.0)

    total_labor_hours = busbar_hours + assembly_hours
    total_labor_cost = total_labor_hours * hourly_rate

    # 4. 總合與報價計算
    st.markdown("---")
    st.markdown(f"### {L['sec_summary']}")

    grand_total = total_material_cost + total_labor_cost

    m1, m2, m3 = st.columns(3)
    m1.metric(L["lbl_mat_total"], f"${total_material_cost:,.2f} USD")
    m2.metric(L["lbl_labor_total"], f"${total_labor_cost:,.2f} USD", f"{total_labor_hours:.1f} 工時")
    m3.metric(L["lbl_grand_total"], f"${grand_total:,.2f} USD", delta="含稅估價", delta_color="normal")

    st.markdown("---")

    # 5. 產生報價單文字與下載
    if st.button(L["btn_gen_quote"], type="primary"):
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        mat_rows_txt = ""
        for i, item in enumerate(calculated_materials, 1):
            mat_rows_txt += f"  {i}. {item['name']} | 數量: {item['qty']} {item['unit']} | 單價: ${item['unit_price']} | 小計: ${item['subtotal']:,.2f} USD\n"

        quote_txt = f"""======================================================================
              REETECH INDUSTRIAL CO., LTD. (裕豐電機工業)
                   OFFICIAL SWITCHGEAR ENGINEERING QUOTATION
======================================================================

Date: {today_str}
Project Name: {prj_name}
Currency: {currency}
Project Description: {prj_desc}

----------------------------------------------------------------------
1. MATERIAL COSTS (配電盤資材費用明細)
----------------------------------------------------------------------
{mat_rows_txt}
  • Material Subtotal: ${total_material_cost:,.2f} USD

----------------------------------------------------------------------
2. FABRICATION & ASSEMBLY LABOR (加工與配線工時費用)
----------------------------------------------------------------------
  • Busbar Fabrication: {busbar_hours} Hours
  • Wiring & Testing: {assembly_hours} Hours
  • Hourly Rate: ${hourly_rate:,.2f} USD / Hour
  • Labor Subtotal: ${total_labor_cost:,.2f} USD

======================================================================
💰 GRAND TOTAL (工程報價總金額): ${grand_total:,.2f} USD
======================================================================
"""
        st.code(quote_txt, language="text")
        st.download_button(
            label=L["btn_download_quote"],
            data=quote_txt,
            file_name=f"Quotation_{prj_name}_{today_str}.txt",
            mime="text/plain",
            type="primary"
        )

def show(*args, **kwargs):
    render_engineering_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_page(*args, **kwargs)
