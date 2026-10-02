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
    st.title("🛒 管理部 - 採購應付帳款 (AP) & 廠商發票與水單")
    st.caption("管理對廠商之資材採購請款單據、付款到期日與銀行轉帳水單 (UNC) 核銷。")

    tab_list, tab_pay = st.tabs([
        "💳 採購應付帳款明細表",
        "🏦 銀行付款水單 (UNC) 登記"
    ])

    with tab_list:
        st.subheader("🛒 廠商應付貨款清單")
        if engine:
            try:
                df_ap = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
                if not df_ap.empty:
                    display_data = []
                    for _, row in df_ap.iterrows():
                        display_data.append({
                            "請款單號": row.get("invoice_id"),
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

    with tab_pay:
        st.subheader("🏦 銀行轉帳水單 (Ủy Nhiệm Chi - UNC) 登記")
        st.info("選擇採購單並輸入 Vietcombank / BIDV 轉帳水單號碼以完成付款核銷。")

def show(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def main(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)
