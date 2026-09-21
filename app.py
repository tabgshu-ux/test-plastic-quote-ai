import yfinance as yf
import streamlit as st

# 初始化 session state 變數 (確保切換代號時能自動刷新)
if "ticker_input" not in st.session_state:
    st.session_state.ticker_input = ""
if "fetched_name" not in st.session_state:
    st.session_state.fetched_name = ""
if "fetched_price" not in st.session_state:
    st.session_state.fetched_price = 0.0
if "fetched_change" not in st.session_state:
    st.session_state.fetched_change = "+0.00 (+0.00%)"

def fetch_stock_info():
    """輸入代號時觸發的自動抓取函式"""
    symbol = st.session_state.ticker_input.strip()
    if symbol:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            
            # 抓取最新價格與昨收價
            latest_price = info.get("lastPrice", 0.0) or info.get("regularMarketPrice", 0.0)
            prev_close = info.get("previousClose", 0.0) or info.get("regularMarketPreviousClose", 0.0)
            
            # 嘗試取得公司簡稱/名稱
            full_info = ticker.info
            short_name = full_info.get("shortName") or full_info.get("longName") or symbol
            
            # 計算漲跌數值與百分比
            if prev_close and prev_close > 0:
                change = latest_price - prev_close
                change_pct = (change / prev_close) * 100
                change_str = f"{change:+.2f} ({change_pct:+.2f}%)"
            else:
                change_str = "+0.00 (+0.00%)"
                
            # 更新至 session_state
            st.session_state.fetched_name = short_name
            st.session_state.fetched_price = float(round(latest_price, 2))
            st.session_state.fetched_change = change_str
            st.success(f"已成功抓取 {short_name} 最新數據！")
        except Exception as e:
            st.error(f"無法抓取代號 '{symbol}' 的即時資料，請確認代號是否正確（例如 3711.TW）。")

# --- UI 介面區塊 ---
st.markdown("### 🛠️ 管理自訂觀察關注標的")

with st.expander("➕ 新增觀察個股/指數", expanded=True):
    market_zone = st.selectbox(
        "選擇股票市場區域",
        ["tw 台灣 (Taiwan)", "cn_hk 中國/香港", "us 美國 (US)", "vn 越南 (Vietnam)", "raw 原物料/匯率"]
    )

    # 1. 股票代號輸入框 (綁定 on_change 自動觸發 API)
    symbol_input = st.text_input(
        "Yahoo 財經代碼 (如 2881.TW / NVDA / 0700.HK)",
        key="ticker_input",
        on_change=fetch_stock_info,
        placeholder="輸入後按 Enter 自動抓取..."
    )

    # 2. 自動帶入的名稱欄位
    stock_name = st.text_input(
        "名稱 (如 富邦金)",
        value=st.session_state.fetched_name
    )

    # 3. 自動帶入的最新價格欄位
    latest_price = st.number_input(
        "最新價格",
        value=st.session_state.fetched_price,
        step=0.01,
        format="%.2f"
    )

    # 4. 自動帶入的漲跌幅欄位
    price_change = st.text_input(
        "漲跌幅度 (如 +1.2 (+1.31%))",
        value=st.session_state.fetched_change
    )

    if st.button("✅ 新增至該市場清單"):
        if symbol_input and stock_name:
            # 這裡放置您原本寫入資料庫或 Session State 清單的邏輯
            st.success(f"已將 {stock_name} ({symbol_input}) 新增至市場清單！")
        else:
            st.warning("請填寫完整的代號與名稱。")
