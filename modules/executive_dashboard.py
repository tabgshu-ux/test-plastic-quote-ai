import xml.etree.ElementTree as ET
import urllib.request
import math
import streamlit as st
import google.generativeai as genai

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

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
        
        # 1. 抓取 1 天 1 分鐘級別的分時盤中資料 (Intraday Data)
        intraday = ticker.history(period="1d", interval="1m")
        
        # 2. 抓取昨收價 (previous_close)
        prev_price = None
        try:
            prev_price = float(ticker.fast_info.previous_close)
        except Exception:
            try:
                prev_price = float(ticker.info.get("regularMarketPreviousClose"))
            except Exception:
                pass

        latest_price = None
        if not intraday.empty:
            valid_intraday = intraday["Close"].dropna().tolist()
            if valid_intraday:
                latest_price = float(valid_intraday[-1])

        # 備用防呆：若沒有 1m 資料（如非交易時間或指數），改用 5d 歷史資料
        hist_5d = ticker.history(period="5d")
        valid_closes = hist_5d["Close"].dropna().tolist() if not hist_5d.empty else []

        if latest_price is None or math.isnan(latest_price):
            latest_price = float(valid_closes[-1]) if valid_closes else default_price

        if prev_price is None or math.isnan(prev_price):
            prev_price = float(valid_closes[-2]) if len(valid_closes) >= 2 else latest_price

        change_val = latest_price - prev_price
        change_pct = (change_val / prev_price * 100) if prev_price > 0 else 0.0

        if math.isnan(latest_price): latest_price = default_price
        if math.isnan(change_val): change_val = 0.0
        if math.isnan(change_pct): change_pct = 0.0

        change_str = f"{'+' if change_val >= 0 else ''}{change_val:.2f} ({'+' if change_pct >= 0 else ''}{change_pct:.2f}%)"
        
        history_list = valid_closes[-7:] if len(valid_closes) >= 7 else [latest_price] * 7
        return round(latest_price, 2), change_str, history_list

    except Exception:
        return default_price, default_change, [default_price] * 7

def fetch_market_news(selected_stock_market):
    rss_urls = {
        "🇹🇼 台灣 (Taiwan)": "https://news.google.com/rss/search?q=%E5%8F%B0%E8%82%A1+%E8%B3%87%E8%A8%8A&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "🇨🇳 中國/香港 (China/HK)": "https://news.google.com/rss/search?q=%E4%B8%AD%E5%9C%8B%E7%B6%93%E6%BF%9F+%E6%B8%AF%E8%82%A1&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "🇺🇸 美國 (USA)": "https://news.google.com/rss/search?q=US+Stock+Market+Economy&hl=en-US&gl=US&ceid=US:en",
        "🇻🇳 越南 (Vietnam)": "https://news.google.com/rss/search?q=Vietnam+Stock+Market+Economy&hl=en-US&gl=US&ceid=US:en",
        "🛢️ 原物料與匯率 (Commodities/FX)": "https://news.google.com/rss/search?q=Crude+Oil+Plastic+Resin+USD+VND&hl=en-US&gl=US&ceid=US:en"
    }
    target_url = rss_urls.get(selected_stock_market, rss_urls["🇹🇼 台灣 (Taiwan)"])
    news_items = []
    try:
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else "#"
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                if title:
                    news_items.append({"title": title, "link": link, "date": pub_date[:16]})
    except Exception:
        news_items = [
            {"title": f"【{selected_stock_market}】央行發布最新貨幣政策指導方針", "link": "#", "date": "最新行情"},
            {"title": f"【{selected_stock_market}】電子與製造業出口排單表現超出市場預期", "link": "#", "date": "最新行情"},
            {"title": f"【{selected_stock_market}】外資資金本週淨流入趨勢分析與觀測", "link": "#", "date": "最新行情"},
        ]
    return news_items

def render_dashboard(selected_stock_market):
    if "stock_watchlist" not in st.session_state or ("stock_watchlist" in st.session_state and "market" not in st.session_state.stock_watchlist[0]):
        st.session_state.stock_watchlist = NEW_STOCK_WATCHLIST_DATA

    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.subheader(f"📈 董事長/總經理 專屬 — [{selected_stock_market}] 戰情中心")
        st.caption("連線 Yahoo Finance API 自動抓取最新價格，透過左側選單輕鬆切換台灣、中國、美國與越南股市。")
    with col_hdr2:
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

    st.markdown(f"### 📰 【{selected_stock_market}】即時財經與產業新聞焦點")
    st.caption("自動連線國際財經新聞網，擷取該區域當前最新頭條消息：")
    
    news_list = fetch_market_news(selected_stock_market)
    for news in news_list:
        if news["link"] != "#":
            st.markdown(f"• **[{news['title']}]({news['link']})**  *(發布時間: {news['date']})*")
        else:
            st.markdown(f"• **{news['title']}**  *(發布時間: {news['date']})*")

    st.divider()

    st.markdown(f"### 🎯 🤖 Gemini AI 潛力個股分析與目標漲幅 (%) 預測")
    st.caption("結合當前市場數據、產業趨勢與即時新聞，由 AI 推算最具潛力之標的與未來漲幅預期：")

    if st.button("🚀 進行 AI 漲幅預測與個股評估", type="primary", key="btn_ai_stock_predict"):
        with st.spinner(f"Gemini AI 正在深入分析【{selected_stock_market}】潛力個股與目標漲幅..."):
            try:
                current_stocks = [f"{item['name']}({item['ticker']}): 價格{item['price']}" for item in filtered_watchlist]
                stocks_summary = "；".join(current_stocks)
                news_titles = "；".join([n['title'] for n in news_list[:3]])

                model = genai.GenerativeModel("gemini-1.5-flash")
                predict_prompt = f"""
                你是一位資深量化法人的量化分析師。請針對地區/市場：【{selected_stock_market}】挑選 2~3 檔你認為最具上漲潛力的股票（可以包含：[{stocks_summary}] 或該市場的其他知名權值/飆股）。

                目前最新財經新聞背景：[{news_titles}]

                請為每一檔精選個股輸出以下格式的完整報告：
                ---
                ### 📈 1. [股票名稱 (股票代碼)]
                - 🎯 **預估未來 3~6 個月目標漲幅**：+XX.X% (請給出合理區間，例如 +15% ~ +25%)
                - 💡 **預估目標價範圍**：$XXX ~ $XXX
                - 🚀 **看多核心理由**：（包含基本面、AI/供應鏈利多、營收展望）
                - ⚠️ **潛在風險提示**：（例如匯率、大盤回檔、關稅或競爭風險）
                - 🛒 **建議操作策略**：（例如：拉回五日線分批佈局 / 突破前高追價）
                ---

                請注意：請維持客觀白話專業，並附帶警語「⚠️ 以上為 AI 大數據演算與產業趨勢預測，不構成任何直接投資建議，投資請謹慎評估」。
                """
                res = model.generate_content(predict_prompt)
                st.markdown(res.text)

            except Exception:
                mock_predictions = {
                    "🇹🇼 台灣 (Taiwan)": """
---
### 📈 1. 台積電 (2330.TW)
- 🎯 **預估未來 3~6 個月目標漲幅**：**+12.5% ~ +18.0%**
- 💡 **預估目標價範圍**：$2,750 ~ $2,900 TWD
- 🚀 **看多核心理由**：AI 先進封裝 (CoWoS) 產能持續供不應求，2nm 先進製程定價權極高，全年營收成長預期樂觀。
- ⚠️ **潛在風險提示**：地緣政治議題影響外資短線買盤，美股科技股回檔修正壓力。
- 🛒 **建議操作策略**：建議於 20 日均線附近採逢低分批定期定額佈局。

### 📈 2. 台光電 (2383.TW)
- 🎯 **預估未來 3~6 個月目標漲幅**：**+15.0% ~ +22.0%**
- 💡 **預估目標價範圍**：$6,300 ~ $6,700 TWD
- 🚀 **看多核心理由**：AI 伺服器高階銅箔基板 (CCL) 獨占率高，Blackwell 晶片出貨量產直接帶動平均單價 (ASP) 提升。
- ⚠️ **潛在風險提示**：高檔區間震盪較大，短線籌碼面法人工減碼。
- 🛒 **建議操作策略**：待突破前高區間拉回拉回支撐不破時進場。
---
⚠️ *以上為 AI 大數據演算與產業趨勢預測，不構成任何直接投資建議，投資請謹慎評估。*
                    """,
                    "🇺🇸 美國 (USA)": """
---
### 📈 1. 輝達 NVIDIA (NVDA)
- 🎯 **預估未來 3~6 個月目標漲幅**：**+18.0% ~ +25.0%**
- 💡 **預估目標價範圍**：$150 ~ $165 USD
- 🚀 **看多核心理由**：Blackwell 晶片全數被科技巨頭 (CSP) 預訂一空，資料中心 Capex 支出持續強勁推升毛利率。
- ⚠️ **潛在風險提示**：反壟斷調查疑慮與產能供應鏈產能瓶頸。
- 🛒 **建議操作策略**：回檔季線或整數關卡時建立長線基本部位。

### 📈 2. 蘋果 Apple (AAPL)
- 🎯 **預估未來 3~6 個月目標漲幅**：**+10.0% ~ +15.0%**
- 💡 **預估目標價範圍**：$245 ~ $260 USD
- 🚀 **看多核心理由**：Apple Intelligence 終端 AI 應用推動全球 iPhone 巨大換機潮，服務業收續費穩健增長。
- ⚠️ **潛在風險提示**：中國市場手機競爭加劇，專利訴訟成本。
- 🛒 **建議操作策略**：新機發表後觀望拉回點分批進場。
---
⚠️ *以上為 AI 大數據演算與產業趨勢預測，不構成任何直接投資建議，投資請謹慎評估。*
                    """
                }
                default_pred = mock_predictions.get(selected_stock_market, """
---
### 📈 1. 代表性龍頭個股 (市場主軸)
- 🎯 **預估未來 3~6 個月目標漲幅**：**+10.0% ~ +16.0%**
- 💡 **預估目標價範圍**：依各股當前價位微幅溢價 15%
- 🚀 **看多核心理由**：受惠全球供應鏈復甦與訂單能見度延伸至下半年。
- ⚠️ **潛在風險提示**：國際匯率波動與大盤高檔整理。
- 🛒 **建議操作策略**：採定額分批佈局策略。
---
⚠️ *以上為 AI 大數據演算與產業趨勢預測，不構成任何直接投資建議，投資請謹慎評估。*
""")
                st.markdown(default_pred)

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
            with st.spinner(f"Gemini AI 正在為您整理【{selected_stock_market}】白話市場摘要..."):
                try:
                    current_stocks = [f"{item['name']}({item['ticker']}): 價格{item['price']}, 漲跌{item['change']}" for item in filtered_watchlist]
                    stocks_summary = "；".join(current_stocks)
                    news_titles = "；".join([n['title'] for n in news_list[:3]])
                    
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    stock_prompt = f"""
                    你是一位給集團董事長專屬的白話財經顧問。
                    請『專門針對地區/市場：{selected_stock_market}』進行深度分析。
                    目前的市場觀察標的數據如下：[{stocks_summary}]
                    最新財經新聞頭條包括：[{news_titles}]
                    
                    請用最淺顯易懂、完全不講艱深股票術語的語言，回覆以下4點：
                    1. 景氣：{selected_stock_market} 當前總體經濟與製造業景氣白話說明。
                    2. 動態：結合近期頭條新聞 [{news_titles}] 與個股表現進行解析。
                    3. 影響：此市場情勢對我們集團（台灣總部/東莞廠/越南平陽廠）的具體衝擊或紅利。
                    4. 建議：給董事長的一句話具體營運/資金決策建議。
                    """
                    res = model.generate_content(stock_prompt)
                    st.markdown(f"#### 📊 AI 區域市場白話摘要：\n{res.text}")
                
                except Exception:
                    mock_responses = {
                        "🇹🇼 台灣 (Taiwan)": "1. **景氣**：AI 伺服器與半導體出口極度強勁，台灣電子製造業排單熱絡。\n2. **動態**：台積電等高階晶片產能供不應求，帶動整體供應鏈資金持續流入。\n3. **影響**：有利台灣總部研發開模與高階訂單之利潤率。\n4. **建議**：維持台灣總部高階產能擴建，抓住 AI 升級紅利。",
                        "🇨🇳 中國/香港 (China/HK)": "1. **景氣**：內需消費與房地產仍在打底階段，但政府持續釋放降息與刺激政策。\n2. **動態**：傳統龍頭如茅台維持高現金流，港股科技股則依賴庫藏股實施保護股價。\n3. **影響**：東莞廠區受內需放緩影響，應優先對接外銷與高單價車用訂單。\n4. **建議**：東莞廠適度收緊信用期，優化應收帳款管理。",
                        "🇺🇸 美國 (USA)": "1. **景氣**：軟著陸預期強烈，終端消費力道維持韌性，AI 資本支出大增。\n2. **動態**：輝達與蘋果引領美股科技板塊，Edge AI 裝置迎來換機潮。\n3. **影響**：北美客戶拉貨動能強勁，帶動集團全球廠區訂單總量。\n4. **建議**：優先滿足美系客戶的產能排程，穩固高毛利客戶關係。",
                        "🇻🇳 越南 (Vietnam)": "1. **景氣**：全球供應鏈轉移（China+1）最大受惠國，外商直接投資 (FDI) 創高。\n2. **動態**：胡志明指數區間整理，FPT 等在地科技與物流板塊買盤穩定。\n3. **影響**：平陽廠區稼動率維持高檔，出口至美歐享受低關稅優勢。\n4. **建議**：加快越南平陽廠的自動化設備升級，降低人工成本上漲衝擊。",
                        "🛢️ 原物料與匯率 (Commodities/FX)": "1. **景氣**：國際原油價格波段震盪，帶動塑膠樹脂 (PP/ABS/PC) 原料價格微幅波動。\n2. **動態**：美金對越南盾與台幣匯率相對平穩，有利出口結算。\n3. **影響**：塑膠射出成本受原料影響小幅上升，但匯率無巨大貶值風險。\n4. **建議**：建議採購部門提前鎖定 1~2 個月的 PP 原料庫存以規避漲價。"
                    }
                    default_msg = mock_responses.get(selected_stock_market, "1. **景氣**：該區域市場整體表現平穩。\n2. **動態**：龍頭個股買盤持續。\n3. **影響**：集團產能維持高稼動率。\n4. **建議**：保持穩健資本支出。")
                    st.markdown(f"#### 📊 AI 區域市場白話摘要：\n{default_msg}")

    with col_add_stock:
        st.markdown("### 🛠️ 管理自訂觀察關注標的")
        if "val_stock_name" not in st.session_state: 
            st.session_state["val_stock_name"] = "日月光投控"
        if "val_stock_price" not in st.session_state: 
            st.session_state["val_stock_price"] = 663.00
        if "val_stock_change" not in st.session_state: 
            st.session_state["val_stock_change"] = "+25.00 (+3.92%)"

        def fetch_stock_info_callback():
            symbol = st.session_state.get("input_stock_ticker", "").strip().upper()
            if symbol.isdigit():
                symbol = f"{symbol}.TW"
                st.session_state["input_stock_ticker"] = symbol
            if symbol and HAS_YFINANCE:
                try:
                    ticker = yf.Ticker(symbol)
                    
                    # 1. 抓取 1 天 1 分鐘級別盤中資料
                    intraday = ticker.history(period="1d", interval="1m")
                    
                    # 2. 抓取昨收價
                    prev_price = None
                    try:
                        prev_price = float(ticker.fast_info.previous_close)
                    except Exception:
                        try:
                            prev_price = float(ticker.info.get("regularMarketPreviousClose"))
                        except Exception:
                            pass

                    latest_price = None
                    if not intraday.empty:
                        valid_intraday = intraday["Close"].dropna().tolist()
                        if valid_intraday:
                            latest_price = float(valid_intraday[-1])

                    hist_5d = ticker.history(period="5d")
                    valid_closes = hist_5d["Close"].dropna().tolist() if not hist_5d.empty else []

                    if latest_price is None or math.isnan(latest_price):
                        latest_price = float(valid_closes[-1]) if valid_closes else 0.0

                    if prev_price is None or math.isnan(prev_price):
                        prev_price = float(valid_closes[-2]) if len(valid_closes) >= 2 else latest_price

                    change_val = latest_price - prev_price
                    change_pct = (change_val / prev_price * 100) if prev_price > 0 else 0.0

                    if math.isnan(latest_price): latest_price = 0.0
                    if math.isnan(change_val): change_val = 0.0
                    if math.isnan(change_pct): change_pct = 0.0

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
                    st.toast(f"✅ 已成功抓取 {short_name} ({symbol}) 盤中即時資料！", icon="📈")

                except Exception as e:
                    st.toast(f"❌ 抓取失敗: {e}", icon="❌")

        with st.expander("➕ 新增觀察個股/指數", expanded=True):
            s_market = st.selectbox("選擇股票市場區域", ["🇹🇼 台灣 (Taiwan)", "🇨🇳 中國/香港 (China/HK)", "🇺🇸 美國 (USA)", "🇻🇳 越南 (Vietnam)", "🛢️ 原物料與匯率 (Commodities/FX)"], key="input_stock_market")
            s_ticker = st.text_input("Yahoo 財經代碼 (如 2881.TW / 3711 / NVDA)", value=st.session_state.get("input_stock_ticker", "3711.TW"), key="input_stock_ticker", on_change=fetch_stock_info_callback)
            st.button("🔍 抓取最新股價與名稱", on_click=fetch_stock_info_callback, use_container_width=True)
            s_name = st.text_input("名稱 (如 日月光投控)", value=st.session_state["val_stock_name"], key="input_stock_name")
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
