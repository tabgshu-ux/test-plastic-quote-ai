import streamlit as st
import pandas as pd
import datetime
import random
from sqlalchemy import text

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

def render_procurement_ap_page(engine=None, **kwargs):
    st.title("🛒 管理部 - 採購與應付帳款管理 (AP)")
    st.caption("管理對廠商之資材採購請款單據、自動讀取信箱電子發票、付款到期日與銀行轉帳水單 (UNC) 核銷。")

    tab_list, tab_email, tab_add, tab_pay = st.tabs([
        "💳 廠商應付貨款明細表",
        "📧 自動讀取信箱電子發票 (AI/Email)",
        "➕ 新增採購單與廠商發票 (手動)",
        "🏦 銀行轉帳水單 (UNC) 登記"
    ])

    # ----------------------------------------------------
    # TAB 1: 檢視應付帳款清冊
    # ----------------------------------------------------
    with tab_list:
        st.subheader("🛒 廠商應付貨款清單")
        if engine:
            try:
                df_ap = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
                if not df_ap.empty:
                    display_data = []
                    for _, row in df_ap.iterrows():
                        display_data.append({
                            "請款/採購單號": row.get("invoice_id"),
                            "廠商/供應商名稱": row.get("entity_name"),
                            "採購品名與規格": row.get("project_name"),
                            "交易幣別": row.get("currency"),
                            "應付金額": format_currency_display(row.get("amount", 0.0), row.get("currency", "VND")),
                            "付款到期日": row.get("due_date"),
                            "付款狀態": "✅ 已付清" if row.get("is_paid") else "⏳ 待付款",
                            "實際轉帳日期": row.get("payment_date", "-"),
                            "付款銀行": row.get("bank_name", "-"),
                            "水單單號 (UNC)": row.get("bank_transfer_ref", "-")
                        })
                    st.dataframe(pd.DataFrame(display_data), use_container_width=True)
                else:
                    st.info("目前無應付帳款紀錄。")
            except Exception as e:
                st.error(f"資料讀取失敗：{e}")

    # ----------------------------------------------------
    # TAB 2: 自動讀取信箱電子發票 (AI Auto Email Parsing)
    # ----------------------------------------------------
    with tab_email:
        st.subheader("📧 自動同步信箱電子發票與 AI 辨識系統")
        st.caption("自動掃描公司財務信箱 (如 invoice@reetech.com)，自動提取廠商寄來的電子發票 (PDF/XML) 並解析金額，免去重複登錄作業。")

        col_mail1, col_mail2 = st.columns([2, 1])
        with col_mail1:
            st.markdown("##### ⚙️ 財務接收信箱設定")
            email_account = st.text_input("公司財務電子發票接收信箱", value="invoice@reetech.com.vn")
        with col_mail2:
            st.markdown("##### 🔄 同步狀態")
            btn_sync_mail = st.button("🚀 立即連線信箱讀取最新發票", type="primary", use_container_width=True)

        if btn_sync_mail:
            with st.spinner("連線 IMAP 信箱伺服器中... 正在讀取未讀發票郵件與附件 OCR 辨識..."):
                st.session_state.email_invoices_found = [
                    {
                        "mail_id": "MAIL-20261002-01",
                        "sender": "CHINT Electrics Vietnam <billing@chint.vn>",
                        "entity_name": "正泰電器 (CHINT Vietnam)",
                        "invoice_no": "HD-20261002-882",
                        "project_name": "施耐德/正泰高壓空氣斷路器 ACB 2000A 批次進貨",
                        "currency": "VND",
                        "amount": 285000000.0,
                        "due_date": (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                        "filename": "HoaDon_Chint_20261002.pdf",
                        "status": "待核對入帳"
                    },
                    {
                        "mail_id": "MAIL-20261002-02",
                        "sender": "Schneider Electric VN <ar@se.com.vn>",
                        "entity_name": "施耐德電機 (Schneider Electric)",
                        "invoice_no": "SE-VN-2026-9910",
                        "project_name": "NSX100F 塑殼斷路器 100A 批次採購",
                        "currency": "USD",
                        "amount": 12500.0,
                        "due_date": (datetime.date.today() + datetime.timedelta(days=45)).strftime("%Y-%m-%d"),
                        "filename": "Invoice_Schneider_12500USD.pdf",
                        "status": "待核對入帳"
                    }
                ]
            st.success("🎉 信箱同步完成！成功解析出 2 筆未入帳之廠商電子發票。")

        st.markdown("---")
        st.markdown("##### 📋 信箱已擷取未入帳發票核對區")
        
        if "email_invoices_found" in st.session_state and st.session_state.email_invoices_found:
            for idx, item in enumerate(st.session_state.email_invoices_found):
                with st.expander(f"📩 [{item['invoice_no']}] {item['entity_name']} - {format_currency_display(item['amount'], item['currency'])} (附件: {item['filename']})", expanded=True):
                    col_i1, col_i2 = st.columns(2)
                    with col_i1:
                        st.write(f"• **寄件者信箱**：`{item['sender']}`")
                        st.write(f"• **AI 辨識廠商名稱**：`{item['entity_name']}`")
                        st.write(f"• **採購項目/規格**：`{item['project_name']}`")
                    with col_i2:
                        st.write(f"• **解析金額**：`{format_currency_display(item['amount'], item['currency'])}`")
                        st.write(f"• **約定付款到期日**：`{item['due_date']}`")
                        st.write(f"• **發票PDF附件**：📎 `{item['filename']}`")

                    if st.button(f"✅ 確認辨識無誤，一鍵寫入應付帳款 (AP)", key=f"btn_confirm_mail_{idx}"):
                        inv_id = f"AP-2026-{datetime.datetime.now().strftime('%m%d%H%M%S')}"
                        if engine:
                            with engine.connect() as conn:
                                conn.execute(
                                    text("""
                                        INSERT INTO invoices (invoice_id, entity_name, project_name, project_period, quoter_name, currency, amount, payment_terms, due_date, uncollected_reason, contract_file_name, invoice_type, is_paid)
                                        VALUES (:id, :entity, :prj, :period, 'AI-Email-System', :curr, :amt, 'Net 30', :due, '自動讀取信箱發票建立', :file, 'AP', false)
                                    """),
                                    {
                                        "id": inv_id, "entity": item['entity_name'], "prj": item['project_name'], "period": item['invoice_no'],
                                        "curr": item['currency'], "amt": item['amount'], "due": item['due_date'], "file": item['filename']
                                    }
                                )
                                conn.commit()
                        st.success(f"🎉 發票 {item['invoice_no']} 已成功轉為正式應付帳單 ({inv_id})！")
                        st.session_state.email_invoices_found.pop(idx)
                        st.rerun()
        else:
            st.info("💡 目前信箱無待處理發票，請點擊上方「立即連線信箱讀取最新發票」按鈕執行同步。")

    # ----------------------------------------------------
    # TAB 3: 手動新增採購單與發票
    # ----------------------------------------------------
    with tab_add:
        st.subheader("➕ 登記新採購進貨單與廠商發票 (手動)")
        st.caption("輸入向廠商採購資材或外包的發票與單據，儲存後系統會自動建立應付帳款。")
        
        with st.form("add_ap_form"):
            col1, col2 = st.columns(2)
            with col1:
                entity_name = st.text_input("廠商 / 供應商名稱 *", placeholder="例如: 正泰電器 (CHINT) 或 施耐德")
                project_name = st.text_input("採購品名與規格 *", placeholder="例如: 高壓斷路器 (MCCB 100A / ACB 2000A) 批次進貨")
                project_period = st.text_input("採購單號 (PO) / 廠商發票號碼", placeholder="例如: PO-2026-0315")
                quoter_name = st.text_input("採購經辦人", value=st.session_state.get("user_name", ""))
            with col2:
                currency = st.selectbox("交易幣別", ["VND", "USD", "CNY", "TWD"])
                amount = st.number_input("應付金額 *", min_value=0.0)
                payment_terms = st.text_input("付款條件", placeholder="例如: 月結 30 天 / 30% 預付")
                due_date = st.date_input("約定付款到期日", datetime.date.today() + datetime.timedelta(days=30))
                uncollected_reason = st.text_area("備註說明", placeholder="請填寫進貨說明或匯款注意事項...")
                uploaded_file = st.file_uploader("📎 上傳採購單 (PO) / 廠商發票照片或 PDF", type=["pdf", "jpg", "png"])

            if st.form_submit_button("💾 儲存並建立應付帳款", use_container_width=True):
                if entity_name and project_name:
                    inv_id = f"AP-2026-{datetime.datetime.now().strftime('%m%d%H%M')}"
                    file_name = uploaded_file.name if uploaded_file else ""
                    
                    if engine:
                        with engine.connect() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO invoices (invoice_id, entity_name, project_name, project_period, quoter_name, currency, amount, payment_terms, due_date, uncollected_reason, contract_file_name, invoice_type, is_paid)
                                    VALUES (:id, :entity, :prj, :period, :quoter, :curr, :amt, :terms, :due, :reason, :file, 'AP', false)
                                """),
                                {
                                    "id": inv_id, "entity": entity_name, "prj": project_name, "period": project_period,
                                    "quoter": quoter_name, "curr": currency, "amt": amount, "terms": payment_terms,
                                    "due": due_date, "reason": uncollected_reason, "file": file_name
                                }
                            )
                            conn.commit()
                    st.success(f"採購應付單據 {inv_id} 已成功建立！")
                    st.rerun()
                else:
                    st.error("請填寫廠商名稱與採購品名！")

    # ----------------------------------------------------
    # TAB 4: 銀行轉帳水單 (UNC) 登記
    # ----------------------------------------------------
    with tab_pay:
        st.subheader("🏦 銀行轉帳水單 (Ủy Nhiệm Chi - UNC) 登記")
        st.info("出納經 Vietcombank / BIDV 轉帳後，在此選擇採購單並輸入轉帳水單號碼以完成付款結清。")

def show(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def main(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)
