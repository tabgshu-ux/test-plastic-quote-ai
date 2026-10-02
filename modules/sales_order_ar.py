import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# 🌐 AR 模組三語系字典
AR_I18N = {
    "繁體中文": {
        "title": "📋 管理部 - 客戶應收帳款 (AR) & 催收稽核軌跡",
        "caption": "即時記錄每次向客戶催討帳款的理由、更新預計付款時間，並保存修改人與催款稽核歷程。",
        "tab_list": "📑 客戶應收款項明細表",
        "tab_edit": "📝 編輯/登記催收歷程與修改理由",
        "tab_quote": "📄 配電盤工程報價單與合約內容",
        "tab_add": "➕ 登記新應收帳款/合約",
        "sec_list_title": "📋 客戶應收帳款追蹤清單",
        "sec_edit_title": "📝 登記催收歷程與更新付款承諾",
        "sec_edit_caption": "每次向客戶討要帳款後，在此輸入客戶給的最新理由、新承諾付款日期與催款經辦人。",
        "select_bill_label": "請選擇要更新催收進度的帳單：",
        "lbl_current_info": "🔍 目前帳單資訊：",
        "lbl_project": "工程專案：",
        "lbl_amount": "這次要收金額：",
        "lbl_due": "原本約定到期日：",
        "lbl_form_title": "✍️️ 填寫這次催款與修改資訊",
        "lbl_new_date": "客戶承諾延後至何時付款（新到期日）",
        "lbl_modifier": "修改/催款記錄人姓名 *",
        "lbl_mark_paid": "🎉 客戶已正式匯款（標記為已結清此筆應付款）",
        "lbl_reason": "客戶給的拖延/未付款理由 *",
        "btn_save": "💾 儲存催收歷程並更新狀態",
        "history_title": "📜 該筆帳單歷史催款與討要理由軌跡紀錄 (Audit Trail)"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Quản lý - Phải thu Khách hàng (AR) & Nhật ký Đôn đốc",
        "caption": "Ghi nhận lý do đôn đốc công nợ, cập nhật ngày hẹn thanh toán và lưu lịch sử kiểm toán.",
        "tab_list": "📑 Danh sách Phải thu Khách hàng",
        "tab_edit": "📝 Cập nhật Tiến độ Đôn đốc & Lý do",
        "tab_quote": "📄 Báo giá & Hợp đồng Tủ điện",
        "tab_add": "➕ Thêm Khoản Phải thu / Hợp đồng Mới",
        "sec_list_title": "📋 Theo dõi Chi tiết Phải thu Khách hàng",
        "sec_edit_title": "📝 Đăng ký Lịch sử Đôn đốc & Cam kết Thanh toán",
        "sec_edit_caption": "Nhập lý do khách hàng đưa ra, ngày hứa thanh toán mới và nhân viên phụ trách.",
        "select_bill_label": "Chọn hóa đơn cần cập nhật tiến độ đôn đốc:",
        "lbl_current_info": "🔍 Thông tin hóa đơn hiện tại:",
        "lbl_project": "Dự án / Công trình:",
        "lbl_amount": "Số tiền cần thu đợt này:",
        "lbl_due": "Hạn thanh toán ban đầu:",
        "lbl_form_title": "✍️ Điền thông tin đôn đốc & chỉnh sửa",
        "lbl_new_date": "Ngày khách hàng cam kết thanh toán mới",
        "lbl_modifier": "Tên nhân viên đôn đốc / ghi nhận *",
        "lbl_mark_paid": "🎉 Khách hàng đã chuyển khoản (Đánh dấu đã hoàn tất)",
        "lbl_reason": "Lý do trì hoãn / chưa thanh toán của khách *",
        "btn_save": "💾 Lưu Lịch sử Đôn đốc & Cập nhật",
        "history_title": "📜 Nhật ký Lịch sử Đôn đốc & Lý do Trì hoãn (Audit Trail)"
    },
    "English": {
        "title": "📋 Admin - Accounts Receivable (AR) & Collection Logs",
        "caption": "Record collection reasons, update promised payment dates, and keep audit trails.",
        "tab_list": "📑 AR Customer Ledger",
        "tab_edit": "📝 Update Collection Logs & Reasons",
        "tab_quote": "📄 Switchboard Quotations & Contracts",
        "tab_add": "➕ Add New AR / Contract",
        "sec_list_title": "📋 Customer AR Tracking List",
        "sec_edit_title": "📝 Record Collection Logs & Payment Promises",
        "sec_edit_caption": "Enter customer reasons, newly promised payment dates, and collector name.",
        "select_bill_label": "Select invoice to update collection status:",
        "lbl_current_info": "🔍 Current Invoice Info:",
        "lbl_project": "Project:",
        "lbl_amount": "Amount Due:",
        "lbl_due": "Original Due Date:",
        "lbl_form_title": "✍️ Enter Collection & Log Details",
        "lbl_new_date": "Promised Payment Date (New Due Date)",
        "lbl_modifier": "Collector / Logged By *",
        "lbl_mark_paid": "🎉 Customer Paid (Mark as Settled)",
        "lbl_reason": "Customer Delay / Non-payment Reason *",
        "btn_save": "💾 Save Collection History & Update",
        "history_title": "📜 Historical Collection Audit Trail"
    }
}

def format_currency_display(amount, curr):
    if curr == "VND":
        return f"₫ {amount:,.0f} VND"
    elif curr == "USD":
        return f"$ {amount:,.2f} USD"
    elif curr == "TWD":
        return f"NT$ {amount:,.0f} TWD"
    elif curr == "CNY":
        return f"¥ {amount:,.2f} CNY"
    return f"{amount:,.2f} {curr}"

def render_sales_order_ar_page(engine=None, t=None, lang="繁體中文", *args, **kwargs):
    curr_lang = kwargs.get("lang", st.session_state.get("lang", lang))
    if curr_lang not in AR_I18N:
        curr_lang = "繁體中文"
    L = AR_I18N[curr_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_edit, tab_quote, tab_add = st.tabs([
        L["tab_list"], L["tab_edit"], L["tab_quote"], L["tab_add"]
    ])

    with tab_list:
        st.subheader(L["sec_list_title"])
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    display_data = []
                    for _, row in df_ar.iterrows():
                        display_data.append({
                            "ID": row.get("invoice_id"),
                            "Customer": row.get("entity_name"),
                            "Project": row.get("project_name"),
                            "Currency": row.get("currency"),
                            "Amount": format_currency_display(row.get("amount", 0.0), row.get("currency", "VND")),
                            "Due Date": f"{row.get('due_date')}",
                            "Collector": row.get("quoter_name", "-"),
                            "Status": "✅ Paid" if row.get("is_paid") else "⏳ Unpaid",
                            "Delay Reason": row.get("uncollected_reason") if row.get("uncollected_reason") else "-"
                        })
                    st.dataframe(pd.DataFrame(display_data), use_container_width=True)
                else:
                    st.info("No records found.")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab_edit:
        st.subheader(L["sec_edit_title"])
        st.caption(L["sec_edit_caption"])

        if engine:
            try:
                df_ar_edit = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR' AND is_paid = false", engine)
                if not df_ar_edit.empty:
                    ar_options = {f"{row['invoice_id']} - {row['entity_name']} ({format_currency_display(row['amount'], row['currency'])})": row['invoice_id'] for _, row in df_ar_edit.iterrows()}
                    selected_ar_label = st.selectbox(L["select_bill_label"], list(ar_options.keys()))
                    target_id = ar_options[selected_ar_label]
                    target_row = df_ar_edit[df_ar_edit['invoice_id'] == target_id].iloc[0]

                    st.markdown("---")
                    st.markdown(f"#### {L['lbl_current_info']} `{target_id}` - {target_row['entity_name']}")
                    st.write(f"• **{L['lbl_project']}** {target_row['project_name']}")
                    st.write(f"• **{L['lbl_amount']}** `{format_currency_display(target_row['amount'], target_row['currency'])}`")
                    st.write(f"• **{L['lbl_due']}** `{target_row['due_date']}`")

                    with st.form("form_update_collection_history"):
                        st.markdown(f"##### {L['lbl_form_title']}")
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            new_due_date = st.date_input(L["lbl_new_date"], value=datetime.date.today() + datetime.timedelta(days=15))
                            modifier_name = st.text_input(L["lbl_modifier"], value=st.session_state.get("user_name", "admin"))
                        with col_e2:
                            mark_as_paid = st.checkbox(L["lbl_mark_paid"])
                            delay_reason = st.text_area(L["lbl_reason"])

                        btn_save_history = st.form_submit_button(L["btn_save"], use_container_width=True)

                        if btn_save_history:
                            if not delay_reason or not modifier_name:
                                st.error("Please complete required fields!")
                            else:
                                now_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                old_reason = target_row['uncollected_reason'] if target_row['uncollected_reason'] else ""
                                audit_log_entry = f"【{now_timestamp} Collector: {modifier_name}】New Due Date: {new_due_date}. Reason: {delay_reason}\n"
                                updated_full_reason = f"{audit_log_entry}\n{old_reason}"

                                with engine.connect() as conn:
                                    conn.execute(
                                        text("""
                                            UPDATE invoices 
                                            SET due_date = :due, uncollected_reason = :reason, quoter_name = :quoter, is_paid = :paid
                                            WHERE invoice_id = :id
                                        """),
                                        {"due": new_due_date, "reason": updated_full_reason, "quoter": modifier_name, "paid": mark_as_paid, "id": target_id}
                                    )
                                    conn.commit()
                                st.success("Updated successfully!")
                                st.rerun()

                    st.markdown("---")
                    st.markdown(f"#### {L['history_title']}")
                    if target_row['uncollected_reason']:
                        st.text_area("Audit Log Details", value=target_row['uncollected_reason'], height=200, disabled=True)
            except Exception as e:
                st.error(f"Error: {e}")

def render(engine=None, t=None, lang="繁體中文", *args, **kwargs):
    render_sales_order_ar_page(engine, t, lang, *args, **kwargs)

def show(engine=None, t=None, lang="繁體中文", *args, **kwargs):
    render_sales_order_ar_page(engine, t, lang, *args, **kwargs)

def main(engine=None, t=None, lang="繁體中文", *args, **kwargs):
    render_sales_order_ar_page(engine, t, lang, *args, **kwargs)
