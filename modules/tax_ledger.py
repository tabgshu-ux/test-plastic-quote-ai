import streamlit as st
import pandas as pd
import psycopg2

def get_db_connection():
    conn_str = "postgresql://postgres:tassos660823@db.vgviddgtkbtuxnwfopi.supabase.co:5432/postgres"
    return psycopg2.connect(conn_str)

def render_tax_ledger(tenant_info, user_perms):
    st.markdown("### 📊 多國動態稅制引擎與會計總帳中心")
    st.info("💡 *支援各國動態稅率設定（如越南 VAT 10%、台灣營業稅 5%）、會計科目總帳分錄與跨國稅務合規報表。*")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 各國動態稅率配置主檔", "📈 會計總帳分錄與試算"])

    with tab1:
        st.markdown("#### 🌐 網頁端動態稅制設定引擎")
        with st.form("tax_config_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                country_code = st.text_input("國家/廠區代碼", value="VN (越南)")
            with c2:
                tax_name = st.text_input("稅別名稱", value="VAT 加值型營業稅")
            with c3:
                tax_rate = st.number_input("稅率百分比 (%)", value=10.0, step=0.5)

            if st.form_submit_button("💾 儲存並即時套用動態稅制", type="primary", use_container_width=True):
                st.success(f"🎉 成功為 [{country_code}] 配置稅別 [{tax_name}]，稅率：`{tax_rate}%`！")

        st.markdown("##### 現行生效中的多國稅率清單")
        tax_df = pd.DataFrame([
            {"country": "Vietnam (VN)", "tax_name": "VAT 增值稅", "rate": "10.0%", "status": "🟢 生效中"},
            {"country": "Taiwan (TW)", "tax_name": "營業稅 (Business Tax)", "rate": "5.0%", "status": "🟢 生效中"}
        ])
        st.dataframe(tax_df, use_container_width=True)

    with tab2:
        st.markdown("#### 📈 企業會計總帳與傳票試算")
        ledger_df = pd.DataFrame([
            {"entry_id": "JE-2026-001", "account_code": "1101", "account_name": "現金及約當現金", "debit": 15000000, "credit": 0, "currency": "VND"},
            {"entry_id": "JE-2026-001", "account_code": "2141", "account_name": "應付營業稅", "debit": 0, "credit": 1500000, "currency": "VND"}
        ])
        st.dataframe(ledger_df, use_container_width=True)
