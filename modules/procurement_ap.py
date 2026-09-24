import streamlit as st
import pandas as pd
from datetime import date

# ----------------------------------------------------
# 🌐 採購與應付帳款模組多語系字典 (i18n)
# ----------------------------------------------------
AP_I18N = {
    "繁體中文": {
        "page_title": "🛒 採購與應付帳款管理系統 (Procurement & AP)",
        "sub_title": "管理供應商採購單 (PO) 開立與跨國應付帳款分期付款沖銷",
        "tab_po_add": "➕ 新增採購項目 (PO)",
        "tab_ap_manage": "💳 應付帳款與 3 期付款管理 (AP)",
        "po_heading": "📝 建立新採購單項目",
        "label_item_name": "品項名稱：",
        "label_qty": "採購數量：",
        "label_unit_price": "單價 (USD)：",
        "label_vendor_name": "採購廠商名稱：",
        "label_vendor_phone": "採購廠商電話：",
        "label_vendor_contact": "廠商聯絡人：",
        "btn_add_po": "🚀 提交採購單並建立應付帳款 (AP)",
        "po_success": "🎉 採購單建立成功！已自動拋轉至應付帳款資料庫。",
        "ap_heading": "💳 應付帳款 (AP) 與分期付款管理清單",
        "col_vendor": "廠商名稱",
        "col_item": "購買項目名稱",
        "col_total": "總金額",
        "col_prepaid": "預付金額",
        "col_remaining": "剩餘金額",
        "col_p1": "第1次付款 (日期/金額)",
        "col_p2": "第2次付款 (日期/金額)",
        "col_p3": "第3次付款 (日期/金額)",
        "payment_heading": "⚙️ 紀錄分期付款金額與日期",
        "select_ap_item": "選擇應付帳款項目：",
        "select_stage": "選擇付款期數：",
        "label_pay_amount": "本次付款金額 (USD)：",
        "label_pay_date": "付款日期：",
        "btn_save_payment": "💾 儲存付款紀錄並更新餘額",
        "pay_success": "✅ 已成功記錄付款並扣抵剩餘金額！"
    },
    "Tiếng Việt": {
        "page_title": "🛒 Quản Lý Mua Hàng & Phải Trả (Procurement & AP)",
        "sub_title": "Quản lý đơn mua hàng (PO) và thanh toán khoản phải trả theo 3 đợt",
        "tab_po_add": "➕ Thêm đơn mua hàng mới (PO)",
        "tab_ap_manage": "💳 Quản lý Khoản phải trả & Thanh toán 3 đợt (AP)",
        "po_heading": "📝 Tạo đơn mua hàng mới",
        "label_item_name": "Tên mặt hàng:",
        "label_qty": "Số lượng mua:",
        "label_unit_price": "Đơn giá (USD):",
        "label_vendor_name": "Tên nhà cung cấp:",
        "label_vendor_phone": "Số điện thoại NCC:",
        "label_vendor_contact": "Người liên hệ NCC:",
        "btn_add_po": "🚀 Tạo đơn mua hàng & Chuyển sang AP",
        "po_success": "🎉 Đã tạo đơn mua hàng thành công và chuyển vào CSDL AP!",
        "ap_heading": "💳 Danh sách Quản lý Phải trả (AP) & Thanh toán đợt",
        "col_vendor": "Tên NCC",
        "col_item": "Mặt hàng mua",
        "col_total": "Tổng tiền",
        "col_prepaid": "Đã đặt cọc",
        "col_remaining": "Còn lại",
        "col_p1": "Thanh toán Đợt 1",
        "col_p2": "Thanh toán Đợt 2",
        "col_p3": "Thanh toán Đợt 3",
        "payment_heading": "⚙️ Ghi nhận lịch sử thanh toán đợt",
        "select_ap_item": "Chọn khoản phải trả:",
        "select_stage": "Chọn đợt thanh toán:",
        "label_pay_amount": "Số tiền thanh toán (USD):",
        "label_pay_date": "Ngày thanh toán:",
        "btn_save_payment": "💾 Lưu lịch sử thanh toán & Cập nhật dư nợ",
        "pay_success": "✅ Đã lưu lịch sử thanh toán và trừ dư nợ thành công!"
    },
    "English": {
        "page_title": "🛒 Procurement & Accounts Payable System (AP)",
        "sub_title": "Manage purchase orders (PO) and installment payment schedules (3 stages)",
        "tab_po_add": "➕ Add New PO Item",
        "tab_ap_manage": "💳 AP & 3-Stage Payment Management",
        "po_heading": "📝 Create New Purchase Order",
        "label_item_name": "Item Name:",
        "label_qty": "Quantity:",
        "label_unit_price": "Unit Price (USD):",
        "label_vendor_name": "Vendor Name:",
        "label_vendor_phone": "Vendor Phone:",
        "label_vendor_contact": "Vendor Contact Person:",
        "btn_add_po": "🚀 Submit PO & Create AP Record",
        "po_success": "🎉 PO created successfully and posted to AP database!",
        "ap_heading": "💳 Accounts Payable & Payment Schedule List",
        "col_vendor": "Vendor Name",
        "col_item": "Item Name",
        "col_total": "Total Amount",
        "col_prepaid": "Prepaid",
        "col_remaining": "Remaining",
        "col_p1": "1st Payment",
        "col_p2": "2nd Payment",
        "col_p3": "3rd Payment",
        "payment_heading": "⚙️ Record Installment Payment",
        "select_ap_item": "Select AP Item:",
        "select_stage": "Payment Stage:",
        "label_pay_amount": "Payment Amount (USD):",
        "label_pay_date": "Payment Date:",
        "btn_save_payment": "💾 Save Payment & Update Balance",
        "pay_success": "✅ Payment recorded and remaining balance updated!"
    }
}

def get_ap_lang_dict(lang_param=None):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return AP_I18N.get(lang, AP_I18N["繁體中文"])

def render_procurement_ap_page(sub_option=None, lang=None):
    L = get_ap_lang_dict(lang)
    current_lang = lang or "繁體中文"

    st.title(L["page_title"])
    st.caption(L["sub_title"])

    # 初始化 AP 資料庫 Session State
    if "ap_db" not in st.session_state:
        st.session_state.ap_db = [
            {
                "id": "AP-2026-001",
                "vendor_name": "住友化學 (Sumitomo Chemical)",
                "vendor_phone": "+886-2-2500-1234",
                "vendor_contact": "林經理 (Mr. Lin)",
                "item_name": "PP 塑膠顆粒原料 (50 噸)",
                "total_amount": 45000.0,
                "prepaid": 15000.0,
                "remaining": 30000.0,
                "p1": "2026-03-01 ($15,000)",
                "p2": "未付款",
                "p3": "未付款"
            },
            {
                "id": "AP-2026-002",
                "vendor_name": "日精樹脂機械 (NISSEI)",
                "vendor_phone": "+81-3-3210-5678",
                "vendor_contact": "Sato San",
                "item_name": "250T 伺服射出成型機",
                "total_amount": 85000.0,
                "prepaid": 25500.0,
                "remaining": 59500.0,
                "p1": "2026-02-15 ($25,500)",
                "p2": "未付款",
                "p3": "未付款"
            }
        ]

    tab1, tab2 = st.tabs([L["tab_po_add"], L["tab_ap_manage"]])

    # ----------------------------------------------------
    # 頁籤一：新增採購品項 (PO)
    # ----------------------------------------------------
    with tab1:
        st.markdown(f"### {L['po_heading']}")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            item_name = st.text_input(L["label_item_name"], value="ABS 工程塑膠原粒 (20 噸)", key=f"po_item_name_{current_lang}")
            qty = st.number_input(L["label_qty"], min_value=1, value=20, key=f"po_qty_{current_lang}")
            unit_price = st.number_input(L["label_unit_price"], min_value=0.1, value=1250.0, step=50.0, key=f"po_unit_price_{current_lang}")
            total_calc = qty * unit_price
            st.info(f"💰 **計算採購總金額**: `${total_calc:,.2f} USD`")

        with col_p2:
            vendor_name = st.text_input(L["label_vendor_name"], value="奇美實業 (CHIMEI Corp)", key=f"po_v_name_{current_lang}")
            vendor_phone = st.text_input(L["label_vendor_phone"], value="+886-6-266-3000", key=f"po_v_phone_{current_lang}")
            vendor_contact = st.text_input(L["label_vendor_contact"], value="張業務副理", key=f"po_v_contact_{current_lang}")
            prepaid_input = st.number_input("預付款 / 訂金金額 (USD)：", min_value=0.0, value=total_calc * 0.3, step=500.0, key=f"po_prepaid_{current_lang}")

        if st.button(L["btn_add_po"], type="primary", key=f"btn_save_po_{current_lang}"):
            new_ap_id = f"AP-2026-{len(st.session_state.ap_db)+1:03d}"
            rem_calc = total_calc - prepaid_input
            
            p1_str = f"{date.today().strftime('%Y-%m-%d')} (${prepaid_input:,.0f})" if prepaid_input > 0 else "未付款"
            
            st.session_state.ap_db.append({
                "id": new_ap_id,
                "vendor_name": vendor_name,
                "vendor_phone": vendor_phone,
                "vendor_contact": vendor_contact,
                "item_name": item_name,
                "total_amount": total_calc,
                "prepaid": prepaid_input,
                "remaining": rem_calc,
                "p1": p1_str,
                "p2": "未付款",
                "p3": "未付款"
            })
            st.success(L["po_success"])
            st.rerun()

    # ----------------------------------------------------
    # 頁籤二：應付帳款 (AP) 與分 3 期付款紀錄管理
    # ----------------------------------------------------
    with tab2:
        st.markdown(f"### {L['ap_heading']}")
        
        # 整理為 Pandas 資料表呈現
        ap_display_list = []
        for item in st.session_state.ap_db:
            ap_display_list.append({
                "AP 編號": item["id"],
                L["col_vendor"]: f"{item['vendor_name']}\n(📞 {item['vendor_phone']} | 👤 {item['vendor_contact']})",
                L["col_item"]: item["item_name"],
                L["col_total"]: f"${item['total_amount']:,.2f}",
                L["col_prepaid"]: f"${item['prepaid']:,.2f}",
                L["col_remaining"]: f"${item['remaining']:,.2f}",
                L["col_p1"]: item["p1"],
                L["col_p2"]: item["p2"],
                L["col_p3"]: item["p3"]
            })

        st.dataframe(pd.DataFrame(ap_display_list), use_container_width=True)

        st.divider()

        # ⚙️ 登記三次付款紀錄區塊
        st.markdown(f"### {L['payment_heading']}")
        
        col_pay1, col_pay2 = st.columns([1, 1])
        with col_pay1:
            ap_options = [f"{a['id']} — {a['vendor_name']} ({a['item_name']})" for a in st.session_state.ap_db]
            selected_ap_str = st.selectbox(L["select_ap_item"], ap_options, key=f"select_pay_ap_{current_lang}")
            
            # 解析選中的 AP ID
            target_id = selected_ap_str.split(" — ")[0]
            target_item = next((a for a in st.session_state.ap_db if a["id"] == target_id), None)

            stage = st.selectbox(L["select_stage"], ["第 1 次付款 (1st Payment)", "第 2 次付款 (2nd Payment)", "第 3 次付款 (3rd Payment)"], key=f"select_stage_{current_lang}")

        with col_pay2:
            pay_amount = st.number_input(L["label_pay_amount"], min_value=0.0, value=15000.0, step=1000.0, key=f"input_pay_amount_{current_lang}")
            pay_date = st.date_input(L["label_pay_date"], value=date.today(), key=f"input_pay_date_{current_lang}")

        if st.button(L["btn_save_payment"], type="primary", key=f"btn_save_pay_{current_lang}"):
            if target_item:
                p_str = f"{pay_date.strftime('%Y-%m-%d')} (${pay_amount:,.0f})"
                if "1" in stage:
                    target_item["p1"] = p_str
                elif "2" in stage:
                    target_item["p2"] = p_str
                elif "3" in stage:
                    target_item["p3"] = p_str

                # 更新剩餘金額與預付金額
                target_item["remaining"] = max(0.0, target_item["remaining"] - pay_amount)
                target_item["prepaid"] += pay_amount
                
                st.success(L["pay_success"])
                st.rerun()

def show(sub_option=None, lang=None):
    render_procurement_ap_page(sub_option, lang)

def main(sub_option=None, lang=None):
    render_procurement_ap_page(sub_option, lang)
