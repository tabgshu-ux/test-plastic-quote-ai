import streamlit as st
import pandas as pd
import numpy as np
import math
import google.generativeai as genai

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

# ----------------------------------------------------
# 多語系文字卡片對照表
# ----------------------------------------------------
DASHBOARD_I18N = {
    "繁體中文": {
        "title": "📈 董事长/總經理 跨國營運戰情室",
        "tab1": "📈 股市與匯率戰情中心",
        "tab2": "💵 全球廠區 AR / AP 財務統計",
        "tab3": "📊 全球廠區營運 KPI 與機台稼動",
        "ar_title": "集團總應收帳款 (AR)",
        "ap_title": "集團總應付帳款 (AP)",
        "net_cash": "預估淨營運現金流",
        "dso": "平均應收帳款週轉天數 (DSO)"
    },
    "Tiếng Việt": {
        "title": "📈 Bảng Điều Hành Doanh Nghiệp Toàn Cầu",
        "tab1": "📈 Thị Trường Chứng Khoán & Tỷ Giá",
        "tab2": "💵 Thống Kê Tài Chính AR / AP",
        "tab3": "📊 KPI Vận Hành Nhà Máy & Năng Suất Máy",
        "ar_title": "Tổng Phải Thu Khách Hàng (AR)",
        "ap_title": "Tổng Phải Trả Nhà Cung Cấp (AP)",
        "net_cash": "Dòng Tiền Hoạt Động Dụ Kiến",
        "dso": "Số Ngày Thu Hồi Nợ Trung Bình (DSO)"
    },
    "简体中文": {
        "title": "📈 董事长/总经理 跨国营运战情室",
        "tab1": "📈 股市与汇率战情中心",
        "tab2": "💵 全球厂区 AR / AP 财务统计",
        "tab3": "📊 全球厂区营运 KPI 与机台稼动",
        "ar_title": "集团总应收账款 (AR)",
        "ap_title": "集团总应付账款 (AP)",
        "net_cash": "预估净营运现金流",
        "dso": "平均应收账款周转天数 (DSO)"
    },
    "English": {
        "title": "📈 Global Executive Dashboard",
        "tab1": "📈 Stock & FX Market Watch",
        "tab2": "💵 Global Factory AR / AP Finance",
        "tab3": "📊 Factory KPI & Machine OEE",
        "ar_title": "Total Accounts Receivable (AR)",
        "ap_title": "Total Accounts Payable (AP)",
        "net_cash": "Net Operating Cash Flow",
        "dso": "Days Sales Outstanding (DSO)"
    },
    "Bahasa Indonesia": {
        "title": "📈 Dasbor Eksekutif Global",
        "tab1": "📈 Pasar Saham & Valas",
        "tab2": "💵 Keuangan AR / AP Pabrik Global",
        "tab3": "📊 KPI Pabrik & OEE Mesin",
        "ar_title": "Total Piutang Usaha (AR)",
        "ap_title": "Total Hutang Usaha (AP)",
        "net_cash": "Arus Kas Operasional Bersih",
        "dso": "Rata-rata Hari Piutang (DSO)"
    }
}

NEW_STOCK_WATCHLIST_DATA = [
    {"market": "🇹🇼 台灣 (Taiwan)", "ticker": "2330.TW", "symbol": "TSMC (2330.TW)", "name": "台積電", "price": 2480.0, "change": "+35.0 (+1.44%)", "signal": "🟢 偏多", "note": "AI 晶片先進封裝獨占，長線穩定成長"},
    {"market": "🇺🇸 美國 (USA)", "ticker": "NVDA", "symbol": "NVIDIA (NVDA)", "name": "輝達", "price": 128.5, "change": "+3.2 (+2.55%)", "signal": "🟢 偏多", "note": " Blackwell 晶片量產，AI 伺服器需求爆發"},
    {"market": "🇻🇳 越南 (Vietnam)", "ticker": "^VNINDEX.HM", "symbol": "VN-INDEX", "name": "越南胡志明指數", "price": 1797.9, "change": "-4.2 (-0.23%)", "signal": "🟡 觀望", "note": "供應鏈移轉長期紅利，東南亞製造中心"},
    {"market": "🛢️ 原物料與匯率 (Commodities/FX)", "ticker": "VND=X", "symbol": "USD/VND", "name": "美金/越南盾匯率", "price": 24850.0, "change": "-10.0 (-0.04%)", "signal": "🟢 穩定", "note": "有利平陽廠出口報價與薪資結算"}
]

def fetch_realtime_stock_data(ticker_symbol, default_price, default_change):
    if not HAS_YFINANCE:
        return default_price, default_change, [default_price * (1 + i * 0.002) for i in range(-3, 4)]
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="7d")
        if not hist.empty:
            close_series = hist["Close"].dropna()
            if len(close_series) >= 2:
                latest_price = float(close_series.iloc[-1])
                prev_price = float(close_series.iloc[-2])
                if not math.isnan(latest_price) and not math.isnan(prev_price) and prev_price > 0:
                    change_val = latest_price - prev_price
                    change_pct = (change_val / prev_price) * 100
                    change_str = f"{'+' if change_val >= 0 else ''}{change_val:.2f} ({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)"
                    return round(latest_price, 2), change_str, close_series.tolist()
        return default_price, default_change, [default_price] * 7
    except Exception:
        return default_price, default_change, [default_price] * 7

def render_executive_dashboard_page(selected_stock_market="🌐 全部市場 (All Markets)", lang="繁體中文"):
    txt = DASHBOARD_I18N.get(lang, DASHBOARD_I18N["繁體中文"])
    st.title(txt["title"])

    tab1, tab2, tab3 = st.tabs([txt["tab1"], txt["tab2"], txt["tab3"]])

    with tab1:
        st.subheader("🏛️ 集團核心客戶與國際匯率即時監控")
        c1, c2, c3, c4 = st.columns(4)
        p_tsm, c_tsm, _ = fetch_realtime_stock_data("2330.TW", 2480.0, "+35.0 (+1.44%)")
        p_nke, c_nke, _ = fetch_realtime_stock_data("NKE", 78.4, "-0.85 (-1.07%)")
        p_add, c_add, _ = fetch_realtime_stock_data("ADDYY", 108.2, "+2.10 (+1.98%)")
        p_vnd, c_vnd, _ = fetch_realtime_stock_data("VND=X", 24850.0, "-10.0 (-0.04%)")

        c1.metric("台積電 (2330.TW)", f"{p_tsm:,.2f}", delta=c_tsm)
        c2.metric("Nike (NKE)", f"${p_nke:,.2f}", delta=c_nke)
        c3.metric("Adidas (ADDYY)", f"${p_add:,.2f}", delta=c_add)
        c4.metric("USD / VND", f"₫ {p_vnd:,.0f}", delta=c_vnd)

    with tab2:
        st.subheader(f"💵 {txt['tab2']}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(txt["ar_title"], "$ 485,000 USD", "+5.2%")
        m2.metric(txt["ap_title"], "$ 210,000 USD", "-2.1%")
        m3.metric(txt["net_cash"], "$ 275,000 USD", "+8.4%")
        m4.metric(txt["dso"], "42 天", "-3 天")

    with tab3:
        st.subheader(f"📊 {txt['tab3']}")
        factories = st.session_state.get("factory_list", [
            {"name": "🇹🇼 台灣總部研發中心", "revenue": "NT$ 12.5M", "status": "🟢 營運中"},
            {"name": "🇨🇳 東莞一廠", "revenue": "¥ 3.4M", "status": "🟢 營运中"},
            {"name": "🇻🇳 越南平陽廠", "revenue": "₫ 12.8B", "status": "🟢 營運中"}
        ])
        cols_f = st.columns(min(len(factories), 4))
        for idx, f in enumerate(factories):
            with cols_f[idx % 4]:
                st.metric(label=f["name"], value=f.get("revenue", "$0.00"), delta=f.get("status", "🟢"))

def show(selected_stock_market="🌐 全部市場 (All Markets)", lang="繁體中文"):
    render_executive_dashboard_page(selected_stock_market, lang)

def main(selected_stock_market="🌐 全部市場 (All Markets)", lang="繁體中文"):
    render_executive_dashboard_page(selected_stock_market, lang)
