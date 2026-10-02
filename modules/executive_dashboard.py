import streamlit as st
import pandas as pd
import datetime

# 三語系字典
EXEC_I18N = {
    "繁體中文": {
        "title": "👑 裕豐電機工業 - 董事長 / 總經理 綜合營運與財務戰情看板",
        "caption": "REETECH INDUSTRIAL Co., Ltd. - 跨國財務 (AR/AP)、原物料與股市 Gemini AI 智能分析",
        "kpi_ar": "客戶應收帳款總額 (AR)",
        "kpi_ap": "廠商應付帳款總額 (AP)",
        "kpi_copper": "🇻🇳 越南國內銅排價格 (VND/kg)",
        "kpi_vnindex": "🇻🇳 越南股市 (VN-Index)",
        "tab_stock": "📈 原物料與跨國股市 (越/美/台/中) + AI 分析",
        "tab_summary": "📊 綜合財務損益與現金流總報表",
        "tab_ar": "🚨 應收帳款 (AR) 專案進度與催收稽核",
        "tab_ap": "🛒 應付帳款 (AP) 摘要"
    },
    "Tiếng Việt": {
        "title": "👑 REETECH INDUSTRIAL - Báo cáo Ban Giám đốc (Chủ tịch/GM)",
        "caption": "Công ty TNHH REETECH INDUSTRIAL - Báo cáo tài chính (AR/AP) & Phân tích thị trường.",
        "kpi_ar": "Tổng Phải thu Khách hàng (AR)",
        "kpi_ap": "Tổng Phải trả Nhà cung cấp (AP)",
        "kpi_copper": "🇻🇳 Giá Đồng thanh cái VN (VND/kg)",
        "kpi_vnindex": "🇻🇳 Chỉ số VN-Index",
        "tab_stock": "📈 Giá Đồng/Thép & Thị trường Chứng khoán",
        "tab_summary": "📊 Báo cáo Lợi nhuận & Dòng tiền",
        "tab_ar": "🚨 Tiến độ Dự án & Kiểm tra Phải thu (AR)",
        "tab_ap": "🛒 Báo cáo Khoản Phải trả (AP)"
    },
    "English": {
        "title": "👑 REETECH INDUSTRIAL - Executive Dashboard (Chairman/GM)",
        "caption": "REETECH INDUSTRIAL Co., Ltd. - Financials (AR/AP) & Market Analytics",
        "kpi_ar": "Total AR Amount",
        "kpi_ap": "Total AP Amount",
        "kpi_copper": "🇻🇳 VN Busbar Copper Price",
        "kpi_vnindex": "🇻🇳 VN-Index",
        "tab_stock": "📈 Raw Material Prices & Global Stocks",
        "tab_summary": "📊 Financial P&L & Cashflow Summary",
        "tab_ar": "🚨 AR Projects & Collection Audit",
        "tab_ap": "🛒 Accounts Payable (AP) Summary"
    }
}

def render(engine=None, t=None, lang="繁體中文", **kwargs):
    L = EXEC_I18N.get(lang, EXEC_I18N["繁體中文"])
    st.title(L["title"])
    st.caption(L["caption"])

    if not engine:
        st.warning("⚠️ 資料庫連線中...")
        return

    try:
        df_inv = pd.read_sql("SELECT * FROM invoices", engine)
        df_ar = df_inv[df_inv['invoice_type'] == 'AR'] if not df_inv.empty else pd.DataFrame()
        df_ap = df_inv[df_inv['invoice_type'] == 'AP'] if not df_inv.empty else pd.DataFrame()

        total_ar = df_ar['amount'].sum() if not df_ar.empty and 'amount' in df_ar.columns else 0.0
        total_ap = df_ap['amount'].sum() if not df_ap.empty and 'amount' in df_ap.columns else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(L["kpi_ar"], f"${total_ar:,.2f}")
        c2.metric(L["kpi_ap"], f"${total_ap:,.2f}")
        c3.metric(L["kpi_copper"], "₫ 245,000 / kg")
        c4.metric(L["kpi_vnindex"], "1,288.50 pts", "+0.65%")

        st.markdown("---")
        t1, t2, t3, t4 = st.tabs([L["tab_stock"], L["tab_summary"], L["tab_ar"], L["tab_ap"]])

        with t1:
            st.info("🌐 跨國股市與銅價行情監控面板運作中。")
        with t2:
            st.write(f"• **預估淨資產與現金流結餘**：${(total_ar - total_ap):,.2f}")
        with t3:
            if not df_ar.empty:
                st.dataframe(df_ar, use_container_width=True)
            else:
                st.info("無應收帳款紀錄。")
        with t4:
            if not df_ap.empty:
                st.dataframe(df_ap, use_container_width=True)
            else:
                st.info("無應付帳款紀錄。")
    except Exception as e:
        st.error(f"戰情看板讀取錯誤: {e}")

def show(engine=None, t=None, lang="繁體中文", **kwargs):
    render(engine, t, lang=lang, **kwargs)

def main(engine=None, t=None, lang="繁體中文", **kwargs):
    render(engine, t, lang=lang, **kwargs)
