import streamlit as st
import pandas as pd

def render(engine, t):
    st.title("👑 裕豐電機工業 - 董事長 / 總經理 營運戰情看板")
    st.caption("REETECH INDUSTRIAL Co., Ltd. - 跨國財務與工程利潤即時分析")
    
    try:
        df_inv = pd.read_sql("SELECT * FROM invoices", engine)
        df_prj = pd.read_sql("SELECT * FROM projects", engine)

        total_ar = df_inv[df_inv['invoice_type'] == 'AR']['amount_usd'].sum() if 'amount_usd' in df_inv.columns else 0.0
        total_ap = df_inv[df_inv['invoice_type'] == 'AP']['amount_usd'].sum() if 'amount_usd' in df_inv.columns else 0.0

        c1, c2, c3 = st.columns(3)
        c1.metric("應收帳款 (折合 USD)", f"USD ${total_ar:,.2f}")
        c2.metric("應付貨款 (折合 USD)", f"USD ${total_ap:,.2f}")
        c3.metric("在手工程項目數", f"{len(df_prj)} 項")

        st.markdown("---")
        st.subheader("🏗️ 配電盤工程項目成本與利潤監控")
        st.dataframe(df_prj, use_container_width=True)
    except Exception as e:
        st.error(f"資料讀取失敗，請確認資料庫狀態：{e}")

def show(engine, t):
    render(engine, t)

def main(engine, t):
    render(engine, t)
