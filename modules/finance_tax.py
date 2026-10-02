import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

EXCHANGE_RATES = {"USD": 1.0, "VND": 25400.0, "TWD": 32.0, "CNY": 7.23}

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

def render(engine, t):
    st.title("💰 管理部 - 財務與應收/應付帳款 (TT200 / 多幣別 / UNC)")
    st.caption("裕豐電機工業 REETECH INDUSTRIAL - 財務會計模組")

    tab_ar, tab_ap, tab_pay, tab_add = st.tabs([
        "📋 TK 131 客戶應收款項 (AR)", 
        "🛒 TK 331 採購與廠商應付款項 (AP)", 
        "🏦 銀行轉帳水單 (UNC)",
        "➕ 登記新單據/帳款"
    ])

    with tab_ar:
        try:
            df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
            st.subheader("📑 TK 131 應收帳款明細表")
            st.dataframe(df_ar, use_container_width=True)
        except Exception as e:
            st.info("尚無應收帳款資料或連線建置中。")

    with tab_ap:
        try:
            df_ap = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
            st.subheader("🛒 TK 331 採購應付帳款明細表")
            st.dataframe(df_ap, use_container_width=True)
        except Exception as e:
            st.info("尚無應付帳款資料或連線建置中。")

    with tab_pay:
        st.subheader("🏦 銀行轉帳水單登記 (Ủy Nhiệm Chi - UNC)")
        st.info("提供出納登記 Vietcombank / BIDV 轉帳水單號碼與簽核日期。")

    with tab_add:
        st.subheader("➕ 登記新單據")
        with st.form("add_inv_form"):
            col1, col2 = st.columns(2)
            with col1:
                inv_type = st.selectbox("帳款類別", ["AR - 應收帳款", "AP - 應付帳款"])
                entity_name = st.text_input("客戶/廠商名稱 *")
                project_name = st.text_input("工程名稱/採購品名 *")
            with col2:
                curr = st.selectbox("交易幣別", ["VND", "USD", "TWD", "CNY"])
                amount = st.number_input("金額 *", min_value=0.0)
                due_date = st.date_input("約定付款日", datetime.date.today() + datetime.timedelta(days=30))

            if st.form_submit_button("💾 儲存寫入資料庫"):
                if entity_name and project_name:
                    type_code = "AR" if "AR" in inv_type else "AP"
                    inv_id = f"{type_code}-2026-{datetime.datetime.now().strftime('%m%d%H%M')}"
                    calc_usd = amount / EXCHANGE_RATES.get(curr, 1.0)
                    
                    with engine.connect() as conn:
                        conn.execute(
                            text("INSERT INTO invoices (invoice_id, entity_name, project_name, amount, currency, amount_usd, due_date, invoice_type, is_paid) VALUES (:id, :entity, :prj, :amt, :curr, :usd, :due, :type, false)"),
                            {"id": inv_id, "entity": entity_name, "prj": project_name, "amt": amount, "curr": curr, "usd": calc_usd, "due": due_date, "type": type_code}
                        )
                        conn.commit()
                    st.success(f"單號 {inv_id} 已成功儲存！")
                    st.rerun()
                else:
                    st.error("請輸入名稱與項目！")

def show(engine, t):
    render(engine, t)

def main(engine, t):
    render(engine, t)
