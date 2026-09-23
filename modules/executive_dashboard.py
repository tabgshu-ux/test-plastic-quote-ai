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
# 預設股市觀察清單主資料
# ----------------------------------------------------
NEW_STOCK_WATCHLIST_DATA = [
    {"market": "🇹🇼 台灣 (Taiwan)", "ticker": "2330.TW", "symbol": "TSMC (2330.TW)", "name": "台積電", "price": 2480.0, "change": "+35.0 (+1.44%)", "signal": "🟢 偏多（適合逢低定額）", "note": "AI 晶片先進封裝獨占，長線穩定成長"},
    {"market": "🇹🇼 台灣 (Taiwan)", "ticker": "2383.TW", "symbol": "Elite (2383.TW)", "name": "台光電", "price": 5490.0, "change": "+15.0 (+0.27%)", "signal": "🟡 觀望（高檔區間震盪）", "note": "伺服器高階 PCB 板材，受惠 AI 升級"},
    {"market": "🇹🇼 台灣 (Taiwan)", "ticker": "2881.TW", "symbol": "Fubon (2881.TW)", "name": "富邦金", "price": 92.5, "change": "+1.2 (+1.31%)", "signal": "🟢 防禦（高股息避風港）", "note": "配息能力強，提供穩健現金流保護"},
    {"market": "🇨🇳 中國/香港 (China/HK)", "ticker": "600519.SS", "symbol": "Moutai (600519.SS)", "name": "貴州茅台", "price": 1450.0, "change": "-12.0 (-0.82%)", "signal": "🟡 觀望（消費打底整理）", "note": "中國內需消費龍頭，現金流極強"},
    {"market": "🇨🇳 中國/香港 (China/HK)", "ticker": "0700.HK", "symbol": "Tencent (0700.HK)", "name": "騰訊控股", "price": 382.0, "change": "+4.5 (+1.19%)", "signal": "🟢 偏多（雲端與 AI 復甦）", "note": "港股科技巨頭，庫藏股實施支撐股價"},
    {"market": "🇺🇸 美國 (USA)", "ticker": "NVDA", "symbol": "NVIDIA (NVDA)", "name": "輝達", "price": 128.5, "change": "+3.2 (+2.55%)", "signal": "🟢 偏多（全球算力龍頭）", "note": " Blackwell 晶片量產，AI 伺服器需求爆發"},
    {"market": "🇺🇸 美國 (USA)", "ticker": "AAPL", "symbol": "Apple (AAPL)", "name": "蘋果電腦", "price": 225.0, "change": "+1.1 (+0.49%)", "signal": "🟢 偏多（Apple Intelligence 換機潮）", "note": "Edge AI 終端載體，供應鏈訂單增溫"},
    {"market": "🇻🇳 越南 (Vietnam)", "ticker": "^VNINDEX.HM", "symbol": "VN-INDEX", "name": "越南胡志明指數", "price": 1797.9, "change": "-4.2 (-0.23%)", "signal": "🟡 觀望（區間整理）", "note": "供應鏈移轉長期紅利，東南亞製造中心"},
    {"market": "🇻🇳 越南 (Vietnam)", "ticker": "FPT.HM", "symbol": "FPT Group (FPT)", "name": "FPT 科技集團", "price": 132000.0, "change": "+1500.0 (+1.15%)", "signal": "🟢 偏多（越南科技龍頭）", "note": "承接全球軟體外包與 AI 數位轉型需求"},
    {"market": "🛢️ 原物料與匯率 (Commodities/FX)", "ticker": "CL=F", "symbol": "Crude Oil (PP Ref)", "name": "原油/塑膠原物料", "price": 71.5, "change": "+0.45 (+0.63%)", "signal": "🟠 提示（原物料成本微升）", "note": "建議採購提前準備 1~2 個月原料庫存"},
    {"market": "🛢️ 原物料與匯率 (Commodities/FX)", "ticker": "VND=X", "symbol": "USD/VND", "name": "美金/越南盾匯率", "price": 24850.0, "change": "-10.0 (-0.04%)", "signal": "🟢 穩定（匯率波幅平緩）", "note": "有利平陽廠出口報價與薪資結算"},
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

def render_stock_module(selected_stock_market="🌐 全部市場 (All Markets)"):
    st.subheader("🏛️ 集團核心客戶與國際匯率即時監控")
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)

    p_tsm, c_tsm, _ = fetch_realtime_stock_data("2330.TW", 2480.0, "+35.0 (+1.44%)")
    p_nke, c_nke, _ = fetch_realtime_stock_data("NKE", 78.4, "-0.85 (-1.07%)")
    p_add, c_add, _ = fetch_realtime_stock_data("ADDYY", 108.2, "+2.10 (+1.98%)")
    p_vnd, c_vnd, _ = fetch_realtime_stock_data("VND=X", 24850.0, "-10.0 (-0.04%)")

    col_k1.metric("台積電 (2330.TW)", f"{p_tsm:,.2f}", delta=c_tsm)
    col_k2.metric("Nike 核心客戶 (NKE)", f"${p_nke:,.2f}", delta=c_nke)
    col_k3.metric("Adidas 品牌 (ADDYY)", f"${p_add:,.2f}", delta=c_add)
    col_k4.metric("美金/越南盾 (USD/VND)", f"₫ {p_vnd:,.0f}", delta=c_vnd)

    st.divider()

    if "stock_watchlist" not in st.session_state or ("stock_watchlist" in st.session_state and "market" not in st.session_state.stock_watchlist[0]):
        st.session_state.stock_watchlist = NEW_STOCK_WATCHLIST_DATA

    col_select, col_refresh = st.columns([3, 1])
    with col_select:
        st.write(f"#### 🌐 目前檢視區域：【{selected_stock_market}】")
    with col_refresh:
        if st.button("🔄 刷新最新市場行情", type="primary", key="btn_refresh_stocks"):
            st.rerun()

    filtered_watchlist = st.session_state.stock_watchlist if selected_stock_market == "🌐 全部市場 (All Markets)" else [item for item in st.session_state.stock_watchlist if item.get("market") == selected_stock_market]

    if filtered_watchlist:
        cols_stock = st.columns(min(len(filtered_watchlist), 5))
        for idx_s, item in enumerate(filtered_watchlist):
            cur_price, cur_change, cur_history = fetch_realtime_stock_data(item.get("ticker", "2330.TW"), item["price"], item["change"])
            with cols_stock[idx_s % 5]:
                st.metric(label=f"{item['name']} ({item['symbol']})", value=f"{cur_price:,.2f}", delta=cur_change)
                st.caption(f"**區域**: {item.get('market', '全區')}")
                st.caption(f"**建議**: {item['signal']}")
                st.line_chart(cur_history, height=85)

    st.divider()

    with st.expander("👑 董事長/總經理 專屬觀察重點與理由", expanded=True):
        for item in filtered_watchlist:
            st.write(f"• **{item['name']} ({item['symbol']})**：{item['signal']} — *{item['note']}*")

def render_ar_ap_module():
    """動態跨國廠區 AR / AP 財務應收應付總覽"""
    st.subheader("💵 全球廠區與子公司 AR / AP 財務統計")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("集團總應收帳款 (AR)", "$ 485,000 USD", "+5.2%")
    m2.metric("集團總應付帳款 (AP)", "$ 210,000 USD", "-2.1%")
    m3.metric("預估淨營運現金流", "$ 275,000 USD", "+8.4%")
    m4.metric("平均應收帳款週轉天數 (DSO)", "42 天", "-3 天")

    st.markdown("---")
    col_ar, col_ap = st.columns([1, 1])

    with col_ar:
        st.markdown("### 🚨 客戶應收帳款 (AR) 逾期預警")
        ar_data = pd.DataFrame({
            "客戶名稱": ["Nike Vietnam", "Adidas Taiwan", "Shopee Seller A", "Foxconn DG"],
            "歸屬廠區": ["🇻🇳 平陽廠", "🇹🇼 台灣總部", "🇻🇳 平陽廠", "🇨🇳 東莞廠"],
            "應收金額 (USD)": ["$ 125,000", "$ 85,000", "$ 32,000", "$ 110,000"],
            "逾期天數": ["⚠️ 逾期 14 天", "🟢 未逾期", "🔴 逾期 23 天", "🟢 未逾期"]
        })
        st.dataframe(ar_data, use_container_width=True)

    with col_ap:
        st.markdown("### 📦 應付帳款 (AP) 付款審核")
        ap_data = pd.DataFrame({
            "供應商名稱": ["奇美實業 (ABS)", "台塑橡膠 (SBR)", "東莞精雕 CNC"],
            "付款廠區": ["🇹🇼 台灣總部", "🇻🇳 平陽廠", "🇨🇳 東莞廠"],
            "應付金額": ["NT$ 1,200,000", "₫ 450,000,000", "¥ 180,000"],
            "狀態": ["⏳ 審核中", "🟢 準備支付", "⏳ 簽核中"]
        })
        st.dataframe(ap_data, use_container_width=True)

def render_kpi_module():
    """動態讀取全球所有廠區的 KPI 總覽"""
    st.subheader("📊 全球廠區營運 KPI 總覽 (動態廠區連動)")
    
    # 動態讀取 IT 模組建立的廠區清單
    factories = st.session_state.get("factory_list", [
        {"name": "🇹🇼 台灣總部研發中心", "revenue": "NT$ 12.5M", "status": "🟢 營運中"},
        {"name": "🇨🇳 東莞一廠", "revenue": "¥ 3.4M", "status": "🟢 營運中"},
        {"name": "🇻🇳 越南平陽廠", "revenue": "₫ 12.8B", "status": "🟢 營運中"}
    ])

    st.markdown(f"**目前全集團營運據點數：`{len(factories)} 個廠區/子公司`**")
    
    # 動態展示各廠區 KPI 卡片
    cols_f = st.columns(min(len(factories), 4))
    for idx, f in enumerate(factories):
        with cols_f[idx % 4]:
            st.metric(label=f["name"], value=f.get("revenue", "$0.00"), delta=f.get("status", "🟢"))

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📉 各廠區營收成長動態趨勢")
        factory_names = [f["name"] for f in factories]
        chart_data = pd.DataFrame(
            np.random.randn(20, len(factories)) * 10000 + 40000,
            columns=factory_names
        )
        st.line_chart(chart_data)

    with col_right:
        st.subheader("🏭 全球廠區機台平均稼動率 (OEE)")
        for f in factories:
            st.progress(0.85, text=f"{f['name']}: 85.0% (運作正常)")

def render_executive_dashboard_page(selected_stock_market="🌐 全部市場 (All Markets)"):
    st.title("📈 董事長/總經理 跨國營運戰情室")
    
    tab1, tab2, tab3 = st.tabs([
        "📈 董事長/總經理 股市與匯率戰情中心", 
        "💵 全球廠區 AR / AP 應收應付財務統計", 
        "📊 全球廠區營運 KPI 與機台稼动"
    ])
    
    with tab1:
        render_stock_module(selected_stock_market)
    with tab2:
        render_ar_ap_module()
    with tab3:
        render_kpi_module()

def show(selected_stock_market="🌐 全部市場 (All Markets)"):
    render_executive_dashboard_page(selected_stock_market)

def main(selected_stock_market="🌐 全部市場 (All Markets)"):
    render_executive_dashboard_page(selected_stock_market)
