import streamlit as st
import pandas as pd

def render(*args, **kwargs):
    # 彈性擷取傳入的 engine 與 lang 參數
    engine = kwargs.get("engine", args[0] if len(args) > 0 else None)
    lang = kwargs.get("lang", "繁體中文")

    st.title("👑 裕豐電機工業 - 董事長 / 總經理 戰情看板")
    st.caption("REETECH INDUSTRIAL Co., Ltd. - 綜合營運與財務管理系統")

    if not engine:
        st.warning("⚠️ 資料庫連線建置中...")
        return

    try:
        df_inv = pd.read_sql("SELECT * FROM invoices", engine)
        df_ar = df_inv[df_inv['invoice_type'] == 'AR'] if not df_inv.empty else pd.DataFrame()
        df_ap = df_inv[df_inv['invoice_type'] == 'AP'] if not df_inv.empty else pd.DataFrame()

        total_ar = df_ar['amount'].sum() if not df_ar.empty and 'amount' in df_ar.columns else 0.0
        total_ap = df_ap['amount'].sum() if not df_ap.empty and 'amount' in df_ap.columns else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("客戶應收帳款 (AR)", f"${total_ar:,.2f}")
        c2.metric("廠商應付帳款 (AP)", f"${total_ap:,.2f}")
        c3.metric("🇻🇳 越南導電銅排價格", "₫ 245,000 / kg")
        c4.metric("🇻🇳 越南股市 (VN-Index)", "1,288.50 pts", "+0.65%")

        st.markdown("---")
        t1, t2 = st.tabs(["📊 綜合財務損益", "🚨 應收帳款專案清冊"])
        with t1:
            st.write(f"• **預估營運現金流結餘**：${(total_ar - total_ap):,.2f}")
        with t2:
            if not df_ar.empty:
                st.dataframe(df_ar, use_container_width=True)
            else:
                st.info("目前無應收帳款資料。")
    except Exception as e:
        st.error(f"戰情看板資料讀取錯誤: {e}")

def show(*args, **kwargs):
    render(*args, **kwargs)

def main(*args, **kwargs):
    render(*args, **kwargs)
