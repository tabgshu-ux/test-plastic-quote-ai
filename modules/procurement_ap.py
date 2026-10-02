import streamlit as st
import pandas as pd
import datetime
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
    st.caption("管理對廠商之資材採購請款單據、付款到期日與銀行轉帳水單 (UNC) 核銷。")

    tab_list, tab_add, tab_pay = st.tabs([
        "💳 廠商應付貨款明細表",
        "➕ 新增採購單與廠商發票 (PO / Invoice)",
        "🏦 銀行轉帳水單 (UNC) 登記"
    ])

    # 1. 檢視應付帳款清冊
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

    # 2. 新增採購單與發票 (建立應付帳款)
    with tab_add:
        st.subheader("➕ 登記新採購進貨單與廠商發票 (AP)")
        st.caption("輸入向廠商採購資材或外包的發票與單據，儲存後系統會自動建立應付帳款。")
        
        with st.form("add_ap_form"):
            col1, col2 = st.columns(2)
            with col1:
                entity_name = st.text_input("廠商 / 供應商名稱 *", placeholder="例如: 正泰電器 (CHINT) 或 施耐德")
                project_name = st.text_input("採購品名與規格 *", placeholder="例如: 高壓斷路器 (MCCB 100A / ACB 2000A) 批次進貨")
                project_period = st.text_input("採購單號 (PO) / 廠商發票號碼", placeholder="例如: PO-2026-0315")
                quoter_name = st.text_input("採購經辦人", value=st.session_state.get("user_name", ""))
            with col2:
                currency = st.selectbox("交易幣別", ["VND (越南盾)", "USD (美金)", "CNY (人民幣)", "TWD (台幣)"])
                curr_code = currency.split(" ")[0]
                amount = st.number_input(f"應付金額 ({curr_code}) *", min_value=0.0)
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
                                    "quoter": quoter_name, "curr": curr_code, "amt": amount, "terms": payment_terms,
                                    "due": due_date, "reason": uncollected_reason, "file": file_name
                                }
                            )
                            conn.commit()
                    st.success(f"採購應付單據 {inv_id} 已成功建立！")
                    st.rerun()
                else:
                    st.error("請填寫廠商名稱與採購品名！")

    # 3. 銀行轉帳水單 (UNC) 登記
    with tab_pay:
        st.subheader("🏦 銀行轉帳水單 (Ủy Nhiệm Chi - UNC) 登記")
        st.info("出納經 Vietcombank / BIDV 轉帳後，在此選擇採購單並輸入轉帳水單號碼以完成付款結清。")

def show(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def main(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)
