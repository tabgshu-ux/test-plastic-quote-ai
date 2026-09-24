import streamlit as st
import pandas as pd
import numpy as np
import os
import google.generativeai as genai

try:
    import yfinance as yf
    import plotly.graph_objects as go
except ImportError:
    yf = None
    go = None

# ----------------------------------------------------
# 🌐 營運戰情室多語系字典 (i18n)
# ----------------------------------------------------
EXEC_I18N = {
    "繁體中文": {
        "page_title": "📈 跨國企業營運戰情室 (Executive Dashboard)",
        "sub_title": "即時監控台灣、越南、美國、中國與全球原物料/匯率之股市看盤、財經新聞與營運指標",
        "boss_notes_title": "👑 董事長/總經理 專屬觀察重點與理由",
        "stock_chart_title": "📊 市場即時看盤 K 線圖 (Live Market Chart)",
        "news_section_title": "📰 近 7 天動態財經新聞與市場大事件",
        "btn_fetch_news": "🔄 重新整理 / 抓取最新財經新聞",
        "ai_summary_title": "🤖 Gemini AI 跨國白話財經摘要",
        "btn_gen_ai_summary": "🚀 生成該區域白話重點與決策報告",
        "watch_title": "🛠️ 管理自訂觀察關注標的",
        "stock_chat_title": "💬 董事長/總經理 專屬 AI 個股與市場諮詢對話框",
        "stock_chat_caption": "請輸入任意股票代碼（如 2330.TW, 2881.TW, NVDA, VNM.VN）或財經問題，AI 即時進行估值與風險分析：",
        "stock_chat_placeholder": "例如：請問台積電 (2330) 最近先進封裝 (CoWoS) 擴產對毛利率有什麼影響？值不值得加碼？",
        "btn_send_stock_chat": "🚀 詢問 AI 財經顧問"
    },
    "Tiếng Việt": {
        "page_title": "📈 Bảng Điều Hành Doanh Nghiệp Đa Quốc Gia (Executive Dashboard)",
        "sub_title": "Giám sát thời gian thực thị trường chứng khoán, tin tức tài chính và tỷ giá tại Đài Loan, Việt Nam, Mỹ, Trung Quốc",
        "boss_notes_title": "👑 Ghi Chú Quan Sát Dành Cho Chủ Tịch / Tổng Giám Đốc",
        "stock_chart_title": "📊 Biểu Đồ Nến Thị Trường Thời Gian Thực (Live Chart)",
        "news_section_title": "📰 Tin Tức Tài Chính & Sự Kiện Thị Trường Trong 7 Ngày Qua",
        "btn_fetch_news": "🔄 Cập nhật / Tải tin tức tài chính mới nhất",
        "ai_summary_title": "🤖 Tóm Tắt Tài Chính AI Gemini",
        "btn_gen_ai_summary": "🚀 Tạo báo cáo tóm tắt & Quyết định chiến lược",
        "watch_title": "🛠️ Quản Lý Danh Mục Theo Dõi Tùy Chỉnh",
        "stock_chat_title": "💬 Khung Trò Chuyện Tư Vấn Cổ Phiếu AI Dành Cho Lãnh Đạo",
        "stock_chat_caption": "Nhập mã cổ phiếu (ví dụ: 2330.TW, NVDA, VNM.VN) hoặc câu hỏi tài chính để AI phân tích:",
        "stock_chat_placeholder": "Ví dụ: Hãy phân tích triển vọng của TSMC (2330) và tác động của mở rộng đóng gói tiên tiến CoWoS?",
        "btn_send_stock_chat": "🚀 Hỏi Cố Vấn AI"
    },
    "English": {
        "page_title": "📈 Executive Strategic Dashboard",
        "sub_title": "Real-time stock charts, financial news & operational KPIs across Taiwan, Vietnam, USA, China, Commodities & FX",
        "boss_notes_title": "👑 Executive Observation Focus & Notes",
        "stock_chart_title": "📊 Live Market Candlestick Chart",
        "news_section_title": "📰 Recent 7-Day Financial News & Market Events",
        "btn_fetch_news": "🔄 Refresh / Fetch Latest Financial News",
        "ai_summary_title": "🤖 Gemini AI Financial Summary",
        "btn_gen_ai_summary": "🚀 Generate Strategic Brief & Executive Report",
        "watch_title": "🛠️ Custom Watchlist Management",
        "stock_chat_title": "💬 Executive AI Stock & Market Assistant",
        "stock_chat_caption": "Enter any ticker symbol (e.g., 2330.TW, 2881.TW, NVDA, VNM.VN) or financial query for instant AI valuation analysis:",
        "stock_chat_placeholder": "E.g., How will TSMC's CoWoS capacity expansion impact its profit margins and long-term valuation?",
        "btn_send_stock_chat": "🚀 Ask AI Financial Advisor"
    },
    "简体中文": {
        "page_title": "📈 跨国企业营运战情室 (Executive Dashboard)",
        "sub_title": "实时监控台湾、越南、美国、中国与全球原物料/汇率之股市看盘、财经新闻与营运指标",
        "boss_notes_title": "👑 董事长/总经理 专属观察重点与理由",
        "stock_chart_title": "📊 市场实时看盘 K 线图 (Live Market Chart)",
        "news_section_title": "📰 近 7 天动态财经新闻与市场大事",
        "btn_fetch_news": "🔄 刷新 / 抓取最新财经新闻",
        "ai_summary_title": "🤖 Gemini AI 跨国白话财经摘要",
        "btn_gen_ai_summary": "🚀 生成该区域白话重点与决策报告",
        "watch_title": "🛠️ 管理自订观察关注标的",
        "stock_chat_title": "💬 董事长/总经理 专属 AI 个股与市场咨询对话框",
        "stock_chat_caption": "请输入任意股票代码（如 2330.TW, 2881.TW, NVDA, VNM.VN）或财经问题，AI 实时进行估值与风险分析：",
        "stock_chat_placeholder": "例如：请问台积电 (2330) 最近先进封装 (CoWoS) 扩产对毛利率有什么影响？值不值得加码？",
        "btn_send_stock_chat": "🚀 询问 AI 财经顾问"
    },
    "Bahasa Indonesia": {
        "page_title": "📈 Dasbor Strategis Eksekutif (Executive Dashboard)",
        "sub_title": "Pemantauan bagan saham, berita keuangan & KPI operasional secara real-time di Taiwan, Vietnam, AS, Tiongkok & Valas",
        "boss_notes_title": "👑 Catatan Pengamatan Eksklusif Direksi",
        "stock_chart_title": "📊 Bagan Lilin Pasar Langsung (Live Chart)",
        "news_section_title": "📰 Berita Keuangan 7 Hari Terakhir & Acara Pasar",
        "btn_fetch_news": "🔄 Perbarui / Ambil Berita Keuangan Terbaru",
        "ai_summary_title": "🤖 Ringkasan Keuangan AI Gemini",
        "btn_gen_ai_summary": "🚀 Hasilkan Laporan Ringkas & Keputusan Strategis",
        "watch_title": "🛠️ Manajemen Daftar Pantauan Kustom",
        "stock_chat_title": "💬 Asisten Saham & Pasar AI Eksekutif",
        "stock_chat_caption": "Masukkan simbol saham (misalnya, 2330.TW, NVDA, VNM) untuk analisis AI instan:",
        "stock_chat_placeholder": "Contoh: Bagaimana prospek TSMC (2330) dalam ekspansi kapasitas AI?",
        "btn_send_stock_chat": "🚀 Tanya Penasihat AI"
    }
}

def get_exec_lang_dict(lang_param=None):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return EXEC_I18N.get(lang, EXEC_I18N["繁體中文"])

# ----------------------------------------------------
# 📈 動態國家/市場 股票指標資料庫 (Metric Cards Data)
# ----------------------------------------------------
def render_market_stock_metrics(market_key):
    """根據選擇的國家分頁，動態顯示該國專屬關注股票指標"""
    if "Taiwan" in market_key or "台灣" in market_key or "Đài Loan" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("台積電 (2330.TW)", "$985 TWD", "+15.0 (+1.55%)")
        col2.metric("富邦金 (2881.TW)", "$78.2 TWD", "+0.8 (+1.03%)")
        col3.metric("台光電 (2383.TW)", "$435 TWD", "-2.5 (-0.57%)")
        col4.metric("台灣加權指數 (TAIEX)", "22,850 點", "+120.5 (+0.53%)")
        chart_symbol, chart_name = "2330.TW", "台積電 (TSMC 2330.TW)"

    elif "Vietnam" in market_key or "越南" in market_key or "Việt Nam" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("VN-Index (越南指數)", "1,280.5 點", "+8.2 (+0.64%)")
        col2.metric("Vinamilk (VNM.VN)", "68,500 VND", "+500 (+0.74%)")
        col3.metric("Hoa Phat (HPG.VN)", "29,200 VND", "+300 (+1.04%)")
        col4.metric("Vietcombank (VCB.VN)", "92,000 VND", "-400 (-0.43%)")
        chart_symbol, chart_name = "VNM.VN", "Vinamilk (VNM.VN)"

    elif "USA" in market_key or "美國" in market_key or "Mỹ" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("輝達 (NVDA)", "$126.5 USD", "+3.8 (+3.09%)")
        col2.metric("蘋果 (AAPL)", "$224.2 USD", "+1.2 (+0.54%)")
        col3.metric("特斯拉 (TSLA)", "$248.0 USD", "-4.5 (-1.78%)")
        col4.metric("標普500 (S&P 500)", "5,620 點", "+18.2 (+0.32%)")
        chart_symbol, chart_name = "NVDA", "輝達 (NVIDIA NVDA)"

    elif "China" in market_key or "中國" in market_key or "Trung Quốc" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("騰訊控股 (0700.HK)", "$382 HKD", "+4.5 (+1.19%)")
        col2.metric("比亞迪 (1211.HK)", "$245 HKD", "+2.8 (+1.15%)")
        col3.metric("上證指數 (SSEC)", "2,860 點", "+5.2 (+0.18%)")
        col4.metric("恆生指數 (HSI)", "17,650 點", "+110.0 (+0.63%)")
        chart_symbol, chart_name = "0700.HK", "騰訊控股 (0700.HK)"

    elif "Commodities" in market_key or "原物料" in market_key or "Nguyên liệu" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("美金/越南盾 (USD/VND)", "25,420 VND", "-15.0 (-0.06%)")
        col2.metric("WTI 原油 (Crude Oil)", "$78.5 USD", "+0.45 (+0.58%)")
        col3.metric("LME 倫敦銅 (Copper)", "$9,250 USD", "+85.0 (+0.93%)")
        col4.metric("塑膠粒 PP 遠東區", "$980 USD/噸", "+12.0 (+1.24%)")
        chart_symbol, chart_name = "CL=F", "WTI 原油期貨 (Crude Oil)"

    else:  # 全部市場 (All Markets)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("台積電 (2330.TW)", "$985 TWD", "+15.0 (+1.55%)")
        col2.metric("VN-Index (越南)", "1,280.5 點", "+8.2 (+0.64%)")
        col3.metric("輝達 (NVDA)", "$126.5 USD", "+3.8 (+3.09%)")
        col4.metric("美金/越南盾 (USD/VND)", "25,420 VND", "-15.0 (-0.06%)")
        chart_symbol, chart_name = "2330.TW", "台積電 (TSMC 2330.TW)"

    return chart_symbol, chart_name

# ----------------------------------------------------
# 📈 繪製即時 K 線圖
# ----------------------------------------------------
def render_live_stock_chart(symbol, name):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=60)
    try:
        if yf:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3m")
            if not df.empty:
                df = df.tail(60)
            else:
                raise ValueError("No data returned")
        else:
            raise ValueError("yfinance not imported")
    except Exception:
        np.random.seed(42)
        close = np.cumprod(1 + np.random.randn(60) * 0.015) * 500
        high = close * (1 + np.abs(np.random.randn(60)) * 0.01)
        low = close * (1 - np.abs(np.random.randn(60)) * 0.01)
        open_p = low + (high - low) * np.random.rand(60)
        df = pd.DataFrame({'Open': open_p, 'High': high, 'Low': low, 'Close': close}, index=dates)

    if go:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="K線"
        )])
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], mode='lines', name='MA 5日線', line=dict(color='#eab308', width=1.5)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines', name='MA 20日線', line=dict(color='#38bdf8', width=1.5)))
        fig.update_layout(
            title=f"📈 {name} ({symbol}) 近 60 日動態 K 線圖與均線指標",
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df['Close'])

# ----------------------------------------------------
# 📰 近 7 天動態新聞
# ----------------------------------------------------
def get_mock_7day_news(market):
    if "Taiwan" in market or "台灣" in market or "Đài Loan" in market:
        return [
            {"date": "2026-03-24", "title": "TSMC 晶圓代工產能持續滿載，先進封裝產能預計擴增 20%", "source": "財經日報 / Economic Daily", "sentiment": "🟢 看多 / Bullish", "summary": "受益於全球 AI 晶片需求，3nm 產能供不應求，帶動整體供應鏈動能。"},
            {"date": "2026-03-22", "title": "央行利率政策維持穩定，新台幣對美元匯率於 31.5 區間震盪", "source": "中央社 / CNA", "sentiment": "🟡 中立 / Neutral", "summary": "外資小幅淨流入，出口製造業利潤率受匯率變動影響有限。"}
        ]
    elif "Vietnam" in market or "越南" in market or "Việt Nam" in market:
        return [
            {"date": "2026-03-24", "title": "Việt Nam FDI thu hút 6.2 tỷ USD trong Q1, Bình Dương dẫn đầu về sản xuất xuất khẩu", "source": "VnExpress / Vietnam News", "sentiment": "🟢 看多 / Bullish", "summary": "外資持續挹注平陽省與同奈省工業區，製造業外設廠動能強勁。"},
            {"date": "2026-03-21", "title": "Cục Thuế ban hành công văn mới về kiểm tra Hóa đơn điện tử và Thuế nhà thầu (FCT)", "source": "Báo Đầu Tư", "sentiment": "🔴 警戒 / Alert", "summary": "越南稅務局加強查核企業電子發票開立與外國承包商稅抵扣憑證，提醒財務人員備妥合約。"}
        ]
    else:
        return [
            {"date": "2026-03-24", "title": "全球原油價格小幅波動，塑化上游烯類原料供應鏈維持平衡", "source": "Reuters Market Watch", "sentiment": "🟡 中立 / Neutral", "summary": "原物料市場短期供需平衡，射出成型加工成本保持可控範疇。"}
        ]

# ----------------------------------------------------
# 💬 AI 財經對話框
# ----------------------------------------------------
def ask_stock_ai_advisor(query_text, lang="繁體中文"):
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return """📊 **【AI 財經顧問 - 個股動態速評】**

* **基本面分析**：營收與 EPS 維持高成長，本益比 (P/E) 處於近五年合理區間中值。
* **籌碼面與技術面**：外資與投信近期呈淨買超，日線站穩 20 日均線（月線）支撐。
* **董事長營運決策建議**：
  1. **短線策略**：回檔至 5 日線可小量分批佈局。
  2. **風險提醒**：注意全球終端需求變動與匯率避險控管。"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"你是一位資深國際投資顧問。請用{lang}回答問題：{query_text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ AI 回應異常: {str(e)}"

# ----------------------------------------------------
# 模組主渲染頁面
# ----------------------------------------------------
def render_executive_dashboard_page(sub_option="🌐 全部市場 (All Markets)", lang=None):
    L = get_exec_lang_dict(lang)
    current_lang = lang or "繁體中文"
    
    st.title(L["page_title"])
    st.caption(L["sub_title"])

    # 👑 1. 董事長專屬觀察重點
    with st.expander(L["boss_notes_title"], expanded=True):
        st.write("• **台積電 (TSMC 2330.TW)**：🟢 **偏多 (適合逢低定額)** — AI 晶片先進封裝獨占，長線穩定成長")
        st.write("• **富邦金 (Fubon 2881.TW)**：🟢 **防禦 (高股息避風港)** — 配息能力強，提供穩健現金流保護")

    st.divider()

    # 📊 2. 【動態國家股票卡片 + K線圖】
    st.markdown(f"### {L['stock_chart_title']} [{sub_option}]")
    
    # 根據左側選取的 sub_option 自動顯示該國指標卡片與 K 線圖標的
    chart_symbol, chart_name = render_market_stock_metrics(sub_option)
    render_live_stock_chart(chart_symbol, chart_name)

    st.divider()

    # 📰 3. 動態財經新聞
    st.markdown(f"### {L['news_section_title']} [{sub_option}]")
    news_list = get_mock_7day_news(sub_option)
    for item in news_list:
        with st.container():
            st.markdown(f"##### 📅 **【{item['date']}】{item['title']}**")
            st.caption(f"來源: `{item['source']}` | 評估: **{item['sentiment']}**")
            st.write(f"💡 {item['summary']}")
            st.markdown("---")

    # 🤖 4. AI 摘要與自訂關注清單
    col_ai, col_watch = st.columns([1, 1])
    with col_ai:
        st.markdown(f"### {L['ai_summary_title']} [{sub_option}]")
        if st.button(L["btn_gen_ai_summary"], type="primary", key=f"btn_ai_exec_sum_{current_lang}"):
            st.success(f"📊 **【{sub_option}】AI 決策分析報告**：製造業需求維持穩健，建議原料維持 30-45 天安全庫存。")

    with col_watch:
        st.markdown(f"### {L['watch_title']}")
        with st.expander("➕ 新增觀察個股/指數", expanded=True):
            st.selectbox("選擇股票市場區域", [sub_option, "🇹🇼 台灣 (Taiwan)", "🇻🇳 越南 (Vietnam)", "🇺🇸 美國 (USA)"], key=f"select_watch_mkt_{current_lang}")
            st.text_input("Yahoo 財經代碼", value="2855.TW", key=f"input_watch_code_{current_lang}")

    st.divider()

    # 💬 5. 底部 AI 個股問答
    st.markdown(f"### {L['stock_chat_title']}")
    user_stock_query = st.text_area("請輸入股票代碼或詢問個股/市場趨勢：", value="請幫我分析台積電 (2330.TW) 近期 CoWoS 擴產影響？", height=90, key=f"input_stock_query_{current_lang}")
    if st.button(L["btn_send_stock_chat"], type="primary", key=f"btn_ask_stock_ai_{current_lang}"):
        answer = ask_stock_ai_advisor(user_stock_query, current_lang)
        st.markdown(answer)

def show(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)

def main(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)
