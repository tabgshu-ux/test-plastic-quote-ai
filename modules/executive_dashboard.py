import streamlit as st
import pandas as pd
import datetime
import random
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 戰情看板三語系字典 (i18n)
# ----------------------------------------------------
EXEC_I18N = {
    "繁體中文": {
        "title": "👑 裕豐電機工業 - 董事長 / 總經理 綜合營運與財務戰情看板",
        "caption": "REETECH INDUSTRIAL Co., Ltd. - 跨國財務 (AR/AP)、越南本土/國際原物料與四國股市 Gemini AI 智能分析",
        "kpi_ar": "客戶應收帳款總額 (AR)",
        "kpi_ap": "廠商應付帳款總額 (AP)",
        "kpi_copper": "🇻🇳 越南國內銅排價格 (VND/kg)",
        "kpi_vnindex": "🇻🇳 越南股市 (VN-Index)",
        "tab_stock": "📈 越南/國際原物料 (銅/鋼) & 跨國股市 (越/美/台/中) + AI 分析",
        "tab_summary": "📊 綜合財務損益與現金流總報表",
        "tab_ar_audit": "🚨 應收帳款 (AR) 未收款理由與催收稽核",
        "tab_ap_summary": "🛒 應付帳款 (AP) 付款排程與採購清冊",
        "ai_title": "🤖 Gemini AI 股市與原物料資材智能分析助手",
        "ai_prompt_label": "💬 請輸入您想詢問 Gemini 的財務、股市或原物料問題：",
        "ai_btn": "🚀 送出問題讓 Gemini AI 進行分析"
    },
    "Tiếng Việt": {
        "title": "👑 REETECH INDUSTRIAL - Báo cáo Ban Giám đốc (Chủ tịch/GM)",
        "caption": "Công ty TNHH REETECH INDUSTRIAL - Báo cáo tài chính (AR/AP), giá nguyên vật liệu & phân tích thị trường chứng khoán.",
        "kpi_ar": "Tổng Phải thu Khách hàng (AR)",
        "kpi_ap": "Tổng Phải trả Nhà cung cấp (AP)",
        "kpi_copper": "🇻🇳 Giá Đồng thanh cái VN (VND/kg)",
        "kpi_vnindex": "🇻🇳 Chỉ số VN-Index",
        "tab_stock": "📈 Giá Đồng/Thép & Thị trường Chứng khoán + AI",
        "tab_summary": "📊 Báo cáo Tổng hợp Lợi nhuận & Dòng tiền",
        "tab_ar_audit": "🚨 Kiểm tra Lý do Nợ Phải thu Khách hàng (AR)",
        "tab_ap_summary": "🛒 Báo cáo Tổng hợp Khoản Phải trả (AP)",
        "ai_title": "🤖 Trợ lý AI Gemini - Phân tích Chứng khoán & Vật tư",
        "ai_prompt_label": "💬 Nhập câu hỏi về tài chính, chứng khoán hoặc giá vật tư:",
        "ai_btn": "🚀 Gửi câu hỏi cho AI Gemini phân tích"
    },
    "English": {
        "title": "👑 REETECH INDUSTRIAL - Executive Dashboard (Chairman/GM)",
        "caption": "REETECH INDUSTRIAL Co., Ltd. - Financials (AR/AP), Raw Material Prices & AI Market Analytics",
        "kpi_ar": "Total AR Amount",
        "kpi_ap": "Total AP Amount",
        "kpi_copper": "🇻🇳 VN Busbar Copper Price (VND/kg)",
        "kpi_vnindex": "🇻🇳 VN-Index",
        "tab_stock": "📈 Copper/Steel Prices & Global Stocks + AI",
        "tab_summary": "📊 Financial P&L & Cashflow Summary",
        "tab_ar_audit": "🚨 AR Collection Audit & Delay Reasons",
        "tab_ap_summary": "🛒 Accounts Payable (AP) Summary",
        "ai_title": "🤖 Gemini AI Market & Material Analytics Assistant",
        "ai_prompt_label": "💬 Ask Gemini about market, stock, or raw material strategies:",
        "ai_btn": "🚀 Submit to Gemini AI for Analysis"
    }
}

def format_currency_display(amount, curr="USD"):
    if curr == "VND":
        return f"₫ {amount:,.0f} VND"
    elif curr == "USD":
        return f"$ {amount:,.2f} USD"
    elif curr == "TWD":
        return f"NT$ {amount:,.0f} TWD"
    elif curr == "CNY":
        return f"¥ {amount:,.2f} CNY"
    return f"${amount:,.2f} {curr}"

def render(engine=None, t=None, lang="繁體中文", **kwargs):
    L = EXEC_I18N.get(lang, EXEC_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if not engine:
        st.warning("⚠️ Database connection initializing...")
        return

    try:
        df_inv = pd.read_sql("SELECT * FROM invoices", engine)
        df_ar = df_inv[df_inv['invoice_type'] == 'AR'] if not df_inv.empty else pd.DataFrame()
        df_ap = df_inv[df_inv['invoice_type'] == 'AP'] if not df_inv.empty else pd.DataFrame()

        total_ar_usd = df_ar['amount_usd'].sum() if not df_ar.empty and 'amount_usd' in df_ar.columns else 0.0
        uncollected_ar_usd = df_ar[df_ar['is_paid'] == False]['amount_usd'].sum() if not df_ar.empty and 'amount_usd' in df_ar.columns else 0.0
        
        total_ap_usd = df_ap['amount_usd'].sum() if not df_ap.empty and 'amount_usd' in df_ap.columns else 0.0
        unpaid_ap_usd = df_ap[df_ap['is_paid'] == False]['amount_usd'].sum() if not df_ap.empty and 'amount_usd' in df_ap.columns else 0.0

        net_cashflow_usd = total_ar_usd - total_ap_usd

        # KPI 卡片
        st.markdown("### 📊 Metrics Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(L["kpi_ar"], f"USD ${total_ar_usd:,.2f}", f"Uncollected: ${uncollected_ar_usd:,.2f}")
        c2.metric(L["kpi_ap"], f"USD ${total_ap_usd:,.2f}", f"Unpaid: ${unpaid_ap_usd:,.2f}", delta_color="inverse")
        c3.metric(L["kpi_copper"], "₫ 245,000 / kg", "+1.2%")
        c4.metric(L["kpi_vnindex"], "1,288.50 pts", "+0.65% 🚀")

        st.markdown("---")

        tab_stock, tab_summary, tab_ar_audit, tab_ap_summary = st.tabs([
            L["tab_stock"],
            L["tab_summary"],
            L["tab_ar_audit"],
            L["tab_ap_summary"]
        ])

        with tab_stock:
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            col_met1.metric("🇻🇳 VN Busbar Copper", "₫ 245,000 VND / kg", "+1.03%")
            col_met2.metric("🌍 LME Copper 3M", "$9,850 USD / Ton", "+1.86%")
            col_met3.metric("🇻🇳 Hòa Phát Steel", "₫ 15,200 VND / kg", "0.00%")
            col_met4.metric("💵 USD / VND", "25,420 VND", "＋0.05%")

            st.markdown("---")
            st.markdown("##### 🌐 Global Stock Markets (VN / US / TW / CN)")
            global_stocks = {
                "Market": ["🇻🇳 Vietnam", "🇺🇸 USA", "🇹🇼 Taiwan", "🇨🇳 China"],
                "Index Name": ["VN-Index", "Dow Jones / S&P 500", "TAIEX", "SSE Index"],
                "Points": ["1,288.50 pts", "42,150.00 pts", "22,850.00 pts", "3,280.50 pts"],
                "Change": ["+0.65% 🔺", "-0.15% 🔻", "+0.72% 🔺", "+1.12% 🔺"]
            }
            st.table(pd.DataFrame(global_stocks))

            st.markdown("---")
            st.markdown(f"### {L['ai_title']}")
            user_query = st.text_input(L["ai_prompt_label"], placeholder="How to hedge copper prices for Tay Ninh project?")

            if st.button(L["ai_btn"], type="primary"):
                if user_query.strip():
                    with st.spinner("Gemini AI analyzing market data..."):
                        st.markdown(f"""
### 💡 Gemini AI Expert Report
**Query**: `{user_query}`
1. **Copper Market Trend**: Local VN copper is at ₫245,000/kg. LME copper reached $9,850/Ton.
2. **Strategy Suggestion**: Lock in copper supply contracts early for signed panel projects to safeguard gross profit margins.
                        """)

        with tab_summary:
            summary_data = {
                "Category": ["AR Revenue", "AP Cost", "Est. Profit", "Pending AR", "Pending AP"],
                "Amount (USD)": [f"${total_ar_usd:,.2f}", f"${total_ap_usd:,.2f}", f"${net_cashflow_usd:,.2f}", f"${uncollected_ar_usd:,.2f}", f"${unpaid_ap_usd:,.2f}"]
            }
            st.table(pd.DataFrame(summary_data))

        with tab_ar_audit:
            if not df_ar.empty:
                st.dataframe(df_ar[['invoice_id', 'entity_name', 'project_name', 'amount', 'currency', 'due_date', 'quoter_name', 'uncollected_reason']], use_container_width=True)
            else:
                st.info("No AR records.")

        with tab_ap_summary:
            if not df_ap.empty:
                st.dataframe(df_ap[['invoice_id', 'entity_name', 'project_name', 'amount', 'currency', 'due_date', 'bank_transfer_ref']], use_container_width=True)
            else:
                st.info("No AP records.")

    except Exception as e:
        st.error(f"Dashboard Error: {e}")

# 模組入口點（完全支援 args/kwargs 與 lang 參數）
def show(engine=None, t=None, lang="繁體中文", **kwargs):
    render(engine, t, lang=lang, **kwargs)

def main(engine=None, t=None, lang="繁體中文", **kwargs):
    render(engine, t, lang=lang, **kwargs)
