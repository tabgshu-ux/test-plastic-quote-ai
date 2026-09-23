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
    """即時抓取 Yahoo Finance 股票資料（具備美股 NaN 自動清洗與 Fallback 保護）"""
    if not HAS_YFINANCE:
        return default_price, default_change, [default_price * (1 + i * 0.002) for i in range(-3, 4)]
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="7d")
        
        # 清除歷史數據中的 NaN 空值
        if not hist.empty:
            close_series = hist["Close"].dropna()
            if len(close_series) >= 2:
                latest_price = float(close_series.iloc[-1])
                prev_price = float(close_series.iloc[-2])
                
                # 檢查數值是否有效（非 nan）
                if not math.isnan(latest_price) and not math.isnan(prev_price) and prev_price > 0:
                    change_val = latest_price - prev_price
                    change_pct = (change_val / prev_price) * 100
                    change_str = f"{'+' if change_val >= 0 else ''}{change_val:.2f} ({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)"
                    return round(latest_price, 2), change_str, close_series.tolist()
            elif len(close_series) == 1:
                latest_price = float(close_series.iloc[-1])
                if not math.isnan(latest_price):
                    return round(latest_price, 2), default_change, [latest_price] * 7

        # 若抓取失敗或數值為 NaN，自動退回預設備援數據
        return default_price, default_change, [default_price] * 7
    except Exception:
        return default_price, default_change, [default_price] * 7

def render_stock_module():
    """完整的股票管理與 AI 解讀模組"""
    if "stock_watchlist" not in st.session_state or ("stock_watchlist" in st.session_state and "market" not in st.session_state.stock_watchlist[0]):
        st.session_state.stock_watchlist = NEW_STOCK_WATCHLIST_DATA

    col_select, col_refresh = st.columns([3, 1])
    with col_select:
        selected_stock_market = st.selectbox(
            "請選擇欲觀察的股市/匯率區域：",
            ["🌐 全部市場 (All Markets)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)"],
            key="select_stock_market_filter"
        )
    with col_refresh:
        st.write("<br>", unsafe_allow_html=True)
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
    else:
        st.info("該分頁目前無觀察標的，您可以在右側表單自由新增或刪除。")

    st.divider()

    with st.expander("👑 董事長/總經理 專屬觀察重點與理由 (無需看懂線圖)", expanded=True):
        st.markdown(f"#### 💡 目前檢視分頁：【{selected_stock_market}】15 秒快速導讀觀點")
        for item in filtered_watchlist:
            st.write(f"• **{item['name']} ({item['symbol']})**：{item['signal']} — *{item['note']}*")

    st.divider()
    col_ai_stock, col_add_stock = st.columns([2, 1])

    with col_ai_stock:
        st.markdown(f"### 🤖 Gemini AI 跨國白話財經摘要 [{selected_stock_market}]")
        st.caption("點擊下方按鈕，讓 AI 為您用最白話的方式解讀該市場之最新趨勢與製造業策略。")
        if st.button("🚀 生成該區域白話重點與決策報告", key="btn_gen_stock_ai"):
            with st.spinner("Gemini AI 正在為您整理白話市場摘要..."):
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    stock_prompt = f"你是一位給集團董事長/總經理的專屬白話財經顧問。請針對區域：『{selected_stock_market}』，用最淺顯易懂、完全不講艱深股票術語的語言，撰寫一份簡短報告（150字以內）：1.景氣現況 2.個股/指數 3.對集團塑膠射出廠影響 4.一句話建議。"
                    res = model.generate_content(stock_prompt)
                    st.markdown(f"#### 📊 AI 區域市場白話摘要：\n{res.text}")
                except Exception:
                    st.info(f"#### 📊 AI 區域市場白話摘要（示範）：\n1. **景氣**：表現穩定。\n2. **動態**：主力科技與製造買盤持續。\n3. **影響**：工廠稼動率維持高檔，材料報價穩定。\n4. **建議**：適度保留現金流。")

    with col_add_stock:
        st.markdown("### 🛠️ 管理自訂觀察關注標的")
        if "val_stock_name" not in st.session_state: st.session_state["val_stock_name"] = "日月光投控"
        if "val_stock_price" not in st.session_state: st.session_state["val_stock_price"] = 663.00
        if "val_stock_change" not in st.session_state: st.session_state["val_stock_change"] = "+25.00 (+3.92%)"

        def fetch_stock_info_callback():
            symbol = st.session_state.get("input_stock_ticker", "").strip().upper()
            if symbol.isdigit():
                symbol = f"{symbol}.TW"
                st.session_state["input_stock_ticker"] = symbol
            if symbol and HAS_YFINANCE:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d")
                    if hist.empty and symbol.endswith(".TW") and symbol[:-3].isdigit():
                        symbol = f"{symbol[:-3]}.TWO"
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="5d")
                    if not hist.empty:
                        close_series = hist["Close"].dropna()
                        if not close_series.empty:
                            latest_price = float(close_series.iloc[-1])
                            prev_price = float(close_series.iloc[-2]) if len(close_series) >= 2 else latest_price
                            change_val = latest_price - prev_price
                            change_pct = (change_val / prev_price * 100) if prev_price > 0 else 0.0
                            change_str = f"{'+' if change_val >= 0 else ''}{change_val:.2f} ({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)"
                            try:
                                info = ticker.info
                                short_name = info.get("shortName") or info.get("longName") or symbol
                            except Exception:
                                short_name = symbol

                            st.session_state["val_stock_name"] = short_name
                            st.session_state["val_stock_price"] = float(round(latest_price, 2))
                            st.session_state["val_stock_change"] = change_str
                            st.session_state["input_stock_name"] = short_name
                            st.session_state["input_stock_price"] = float(round(latest_price, 2))
                            st.session_state["input_stock_change"] = change_str
                            st.toast(f"✅ 已成功抓取 {short_name} ({symbol})！", icon="📈")
                except Exception as e:
                    st.toast(f"❌ 抓取失敗: {e}", icon="❌")

        with st.expander("➕ 新增觀察個股/指數", expanded=True):
            s_market = st.selectbox("選擇股票市場區域", ["🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)"], key="input_stock_market")
            s_ticker = st.text_input("Yahoo 財經代碼 (如 2881.TW / 2855 / NVDA)", value=st.session_state.get("input_stock_ticker", "2855.TW"), key="input_stock_ticker", on_change=fetch_stock_info_callback)
            st.button("🔍 抓取最新股價與名稱", on_click=fetch_stock_info_callback, use_container_width=True)
            s_name = st.text_input("名稱 (如 統一證)", value=st.session_state["val_stock_name"], key="input_stock_name")
            s_price = st.number_input("最新價格", min_value=0.0, value=st.session_state["val_stock_price"], step=0.5, format="%.2f", key="input_stock_price")
            s_change = st.text_input("漲跌幅度 (如 +0.50 (+2.10%))", value=st.session_state["val_stock_change"], key="input_stock_change")

            if st.button("✅ 新增至該市場清單", type="primary", key="btn_add_stock_to_list"):
                if s_ticker and s_name:
                    st.session_state.stock_watchlist.append({"market": s_market, "ticker": s_ticker, "symbol": f"{s_name} ({s_ticker})", "name": s_name, "price": s_price, "change": s_change, "signal": "🟢 偏多（穩健觀察）", "note": "自訂關注標的"})
                    st.success(f"已成功新增 `{s_name}` 至 【{s_market}】！")
                    st.rerun()

        with st.expander("🗑️ 管理與刪除已關注標的", expanded=True):
            if st.session_state.stock_watchlist:
                manageable_stocks = st.session_state.stock_watchlist if selected_stock_market == "🌐 全部市場 (All Markets)" else [item for item in st.session_state.stock_watchlist if item.get("market") == selected_stock_market]
                if manageable_stocks:
                    stock_options = [f"{idx} - {item['name']} ({item['ticker']})" for idx, item in enumerate(manageable_stocks)]
                    selected_del_stock_str = st.selectbox("選擇要移除的標的", stock_options, key="del_stock_select")
                    if st.button("🗑️ 確認將此標的從關注清單移除", type="primary", key="btn_del_stock_confirm"):
                        target_ticker = selected_del_stock_str.split(" (")[-1].replace(")", "")
                        st.session_state.stock_watchlist = [item for item in st.session_state.stock_watchlist if item['ticker'] != target_ticker]
                        st.success(f"🗑️ 已成功將 `{target_ticker}` 從關注清單移除！")
                        st.rerun()

def render_kpi_module():
    """營運 KPI 與 AR 預警模組"""
    st.subheader("📊 跨國三廠營運 KPI 總覽")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("本月集團總營收 (USD)", "$1,280,000", "+8.5%")
    col2.metric("台灣總部 (TWD)", "NT$ 12,500,000", "+3.2%")
    col3.metric("東莞廠 (RMB)", "¥ 3,400,000", "-1.5%")
    col4.metric("越南平陽廠 (VND)", "₫ 12.8 Billion", "+12.4%")

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📉 近半季三廠營收成長趨勢 (USD)")
        chart_data = pd.DataFrame(
            np.random.randn(20, 3) * 10000 + [50000, 40000, 35000],
            columns=['台灣總部 (TW)', '東莞廠 (DG)', '平陽廠 (BH)']
        )
        st.line_chart(chart_data)

    with col_right:
        st.subheader("🚨 AR / DSO 應收帳款預警")
        st.warning("⚠️ **Nike Vietnam**: 帳款逾期 15 天 ($45,000 USD)")
        st.info("ℹ️ **Adidas Taiwan**: 預計 3 天內入帳 (NT$ 1,200,000)")
        st.success("✅ **Shopee Seller A**: 帳款已全數結清")

def render_executive_dashboard_page():
    """主進入點：雙分頁架構"""
    st.title("📈 董事長/總經理 跨國營運戰情室")
    
    tab1, tab2 = st.tabs(["📈 董事長/總經理 股市與匯率戰情中心", "📊 集團三廠營運 KPI 與 AR 預警"])
    
    with tab1:
        render_stock_module()
        
    with tab2:
        render_kpi_module()

# 相容 app.py 的動態載入
def show():
    render_executive_dashboard_page()

def main():
    render_executive_dashboard_page()
