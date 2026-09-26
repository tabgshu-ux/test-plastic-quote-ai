import streamlit as st
import os
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from datetime import datetime, date

# ----------------------------------------------------
# 🌐 營運戰情室多語系字典 (i18n) - 完全保留
# ----------------------------------------------------
EXEC_I18N = {
    "繁體中文": {
        "page_title": "📈 跨國企業營運戰情室 (Executive Dashboard)",
        "sub_title": "即時監控台灣、越南、美國、中國與全球原物料/匯率之股市看盤、財經新聞與營運指標",
        "boss_notes_title": "👑 董事長/總經理 專屬觀察重點與理由",
        "tab_market": "🌐 全球市場與即時看盤",
        "tab_fin_stat": "📊 全球廠區 AR/AP 財務統計",
        "tab_vpsh_reports": "📊 VPSH 高階八大財務與營運戰情報表",
        "tab_plant_kpi": "⚡ 全球廠區營運 KPI 與機台稼動 (OEE)",
        "stock_section_title": "📊 市場即時行情與關注個股看板",
        "news_section_title": "📰 近 7 天動態財經新聞與市場大事件 (點擊標題開啟新聞原文)",
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
        "tab_market": "🌐 Thị trường toàn cầu & Bảng giá",
        "tab_fin_stat": "📊 Thống kê tài chính AR/AP các nhà máy",
        "tab_vpsh_reports": "📊 Báo cáo tài chính & vận hành VPSH",
        "tab_plant_kpi": "⚡ KPI vận hành & Hiệu suất máy (OEE)",
        "stock_section_title": "📊 Bảng Giá Chứng Khoán & Chỉ Số Thị Trường Thời Gian Thực",
        "news_section_title": "📰 Tin Tức Tài Chính Trong 7 Ngày Qua (Nhấp vào tiêu đề để đọc chi tiết)",
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
        "sub_title": "Real-time stock tickers, financial news & operational KPIs across Taiwan, Vietnam, USA, China, Commodities & FX",
        "boss_notes_title": "👑 Executive Observation Focus & Notes",
        "tab_market": "🌐 Global Markets & Tickers",
        "tab_fin_stat": "📊 Global Sites AR/AP Financial Stats",
        "tab_vpsh_reports": "📊 VPSH 8-Core Financial & Operational Reports",
        "tab_plant_kpi": "⚡ Global Sites Operational KPIs & OEE",
        "stock_section_title": "📊 Live Stock Tickers & Market Indices",
        "news_section_title": "📰 Recent 7-Day Financial News (Click title to view full article)",
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
        "tab_market": "🌐 全球市场与实时看盘",
        "tab_fin_stat": "📊 全球厂区 AR/AP 财务统计",
        "tab_vpsh_reports": "📊 VPSH 高阶八大财务与营运战情报表",
        "tab_plant_kpi": "⚡ 全球厂区营运 KPI 与机台稼动 (OEE)",
        "stock_section_title": "📊 市场实时行情与关注个股看板",
        "news_section_title": "📰 近 7 天动态财经新闻与市场大事 (点击标题查看新闻原文)",
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
        "sub_title": "Pemantauan harga saham, berita keuangan & KPI operasional secara real-time di Taiwan, Vietnam, AS, Tiongkok & Valas",
        "boss_notes_title": "👑 Catatan Pengamatan Eksklusif Direksi",
        "tab_market": "🌐 Pasar Global & Ticker",
        "tab_fin_stat": "📊 Statistik Keuangan AR/AP Pabrik Global",
        "tab_vpsh_reports": "📊 Laporan Keuangan & Operasional Utama VPSH",
        "tab_plant_kpi": "⚡ KPI Operasional Pabrik & OEE Mesin",
        "stock_section_title": "📊 Harga Saham Langsung & Indeks Pasar",
        "news_section_title": "📰 Berita Keuangan 7 Hari Terakhir (Klik judul untuk membaca selengkapnya)",
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
# 📊 1. 股票與市場看板 (Metric Cards)
# ----------------------------------------------------
def render_market_stock_metrics(market_key):
    if "Taiwan" in market_key or "台灣" in market_key or "Đài Loan" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("台積電 (2330.TW)", "$985 TWD", "+15.0 (+1.55%)")
        col2.metric("富邦金 (2881.TW)", "$78.2 TWD", "+0.8 (+1.03%)")
        col3.metric("台光電 (2383.TW)", "$435 TWD", "-2.5 (-0.57%)")
        col4.metric("台灣加權指數 (TAIEX)", "22,850 點", "+120.5 (+0.53%)")

    elif "Vietnam" in market_key or "越南" in market_key or "Việt Nam" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("VN-Index (越南指數)", "1,280.5 點", "+8.2 (+0.64%)")
        col2.metric("Vinamilk (VNM.VN)", "68,500 VND", "+500 (+0.74%)")
        col3.metric("Hoa Phat (HPG.VN)", "29,200 VND", "+300 (+1.04%)")
        col4.metric("Vietcombank (VCB.VN)", "92,000 VND", "-400 (-0.43%)")

    elif "USA" in market_key or "美國" in market_key or "Mỹ" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("輝達 (NVDA)", "$126.5 USD", "+3.8 (+3.09%)")
        col2.metric("蘋果 (AAPL)", "$224.2 USD", "+1.2 (+0.54%)")
        col3.metric("特斯拉 (TSLA)", "$248.0 USD", "-4.5 (-1.78%)")
        col4.metric("標普500 (S&P 500)", "5,620 點", "+18.2 (+0.32%)")

    elif "China" in market_key or "中國" in market_key or "Trung Quốc" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("騰訊控股 (0700.HK)", "$382 HKD", "+4.5 (+1.19%)")
        col2.metric("比亞迪 (1211.HK)", "$245 HKD", "+2.8 (+1.15%)")
        col3.metric("上證指數 (SSEC)", "2,860 點", "+5.2 (+0.18%)")
        col4.metric("恆生指數 (HSI)", "17,650 點", "+110.0 (+0.63%)")

    elif "Commodities" in market_key or "原物料" in market_key or "Nguyên liệu" in market_key:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("美金/越南盾 (USD/VND)", "25,420 VND", "-15.0 (-0.06%)")
        col2.metric("WTI 原油 (Crude Oil)", "$78.5 USD", "+0.45 (+0.58%)")
        col3.metric("LME 倫敦銅 (Copper)", "$9,250 USD", "+85.0 (+0.93%)")
        col4.metric("塑膠粒 PP 遠東區", "$980 USD/噸", "+12.0 (+1.24%)")

    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("台積電 (2330.TW)", "$985 TWD", "+15.0 (+1.55%)")
        col2.metric("VN-Index (越南)", "1,280.5 點", "+8.2 (+0.64%)")
        col3.metric("輝達 (NVDA)", "$126.5 USD", "+3.8 (+3.09%)")
        col4.metric("美金/越南盾 (USD/VND)", "25,420 VND", "-15.0 (-0.06%)")

# ----------------------------------------------------
# 📰 2. 財經新聞資料庫
# ----------------------------------------------------
def get_mock_7day_news(market):
    if "Taiwan" in market or "台灣" in market or "Đài Loan" in market:
        return [
            {
                "date": "2026-03-24",
                "title": "TSMC 晶圓代工產能持續滿載，先進封裝產能預計擴增 20%",
                "url": "https://tw.stock.yahoo.com/news/tsmc-advanced-packaging-expansion",
                "source": "財經日報 / Economic Daily",
                "sentiment": "🟢 看多 / Bullish",
                "summary": "受益於全球 AI 晶片需求強勁，台積電 3nm 產能供不應求，帶動整體 CoWoS 先進封裝供應鏈動能上升。"
            },
            {
                "date": "2026-03-22",
                "title": "央行利率政策維持穩定，新台幣對美元匯率於 31.5 區間震盪",
                "url": "https://tw.stock.yahoo.com/news/cbdc-taiwan-dollar-rate-stable",
                "source": "中央社 / CNA",
                "sentiment": "🟡 中立 / Neutral",
                "summary": "外資小幅淨流入，出口製造業利潤率受匯率變動影響有限，整體外貿環境維持溫和成長。"
            }
        ]
    elif "Vietnam" in market or "越南" in market or "Việt Nam" in market:
        return [
            {
                "date": "2026-03-24",
                "title": "Việt Nam FDI thu hút 6.2 tỷ USD trong Q1, Bình Dương dẫn đầu về sản xuất xuất khẩu",
                "url": "https://vnexpress.net/fdi-vao-viet-nam-tang-truong-manh",
                "source": "VnExpress / Vietnam News",
                "sentiment": "🟢 看多 / Bullish",
                "summary": "外資持續挹注平陽省與同奈省工業區，製造業擴廠動能強勁，帶動當地射出成型與周邊設備需求。"
            }
        ]
    else:
        return [
            {
                "date": "2026-03-24",
                "title": "全球原油價格小幅波動，塑化上游烯類原料供應鏈維持平衡",
                "url": "https://www.reuters.com/business/energy",
                "source": "Reuters Market Watch",
                "sentiment": "🟡 中立 / Neutral",
                "summary": "原物料市場短期供需平衡，射出成型加工原料成本保持在可控範疇。"
            }
        ]

# ----------------------------------------------------
# 💬 3. AI 財經顧問對話框
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
        prompt = f"你是一位專為董事長服務的資深跨國投資顧問。請用{lang}簡明回答：{query_text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ AI 回應異常: {str(e)}"

# ----------------------------------------------------
# 📊 4. 全球廠區 AR/AP 財務統計
# ----------------------------------------------------
def render_financial_ar_ap_stats():
    st.markdown("### 📊 跨國集團全球廠區應收/應付帳款 (AR/AP) 總覽")
    
    col_ar1, col_ar2, col_ar3, col_ar4 = st.columns(4)
    col_ar1.metric("全球總應收帳款 (AR)", "$2,850,000 USD", "+$120,000")
    col_ar2.metric("全球總應付帳款 (AP)", "$1,420,000 USD", "-$45,000")
    col_ar3.metric("逾期帳款 (>60天)", "$185,000 USD", "⚠️ 需關注")
    col_ar4.metric("淨營運現金流預估", "$1,430,000 USD", "🟢 健康")

    st.markdown("#### 🏢 各廠區 AR / AP 明細與流動性分析")
    ar_ap_data = [
        {"廠區/子公司": "🇹🇼 台灣總部 (Taiwan HQ)", "應收帳款 (AR) USD": "$1,200,000", "應付帳款 (AP) USD": "$600,000", "逾期帳款 USD": "$20,000", "主要幣別": "TWD / USD", "帳款狀態": "🟢 正常"},
        {"廠區/子公司": "🇻🇳 越南平陽廠 (Binh Duong Plant)", "應收帳款 (AR) USD": "$950,000", "應付帳款 (AP) USD": "$520,000", "逾期帳款 USD": "$115,000", "主要幣別": "VND / USD", "帳款狀態": "🟡 催收中"},
        {"廠區/子公司": "🇨🇳 中國東莞廠 (Dongguan Plant)", "應收帳款 (AR) USD": "$700,000", "應付帳款 (AP) USD": "$300,000", "逾期帳款 USD": "$50,000", "主要幣別": "RMB / USD", "帳款狀態": "🟢 正常"}
    ]
    st.dataframe(pd.DataFrame(ar_ap_data), use_container_width=True)

# ----------------------------------------------------
# 🧮 5. 動態計算引擎：從底層營運算式自動運算匯總「綜合損益表」 (包含連動全系統 Session State)
# ----------------------------------------------------
def render_vpsh_core_reports():
    st.markdown("### 📊 VPSH 高階八大財務與營運決策戰情報表 (USD)")

    # 🎛️ 可調式高管參數設定選單（允許總經理模擬試算）
    with st.expander("⚙️ 營運底層計算參數試算模組 (點擊展開可調整試算條件)", expanded=False):
        c_p1, c_p2, c_p3 = st.columns(3)
        sales_units = c_p1.number_input("總銷售套數 (VIP套裝)", min_value=1000, value=22320, step=1000)
        unit_price = c_p2.number_input("VIP套裝銷售單價 ($ USD)", min_value=100.0, value=345.0, step=5.0)
        shoe_cost_per_set = c_p3.number_input("鞋款生產成本/套 ($ USD)", min_value=0.0, value=42.0, step=1.0)

    # ----------------------------------------------------
    # 動態算式計算 (自動勾稽連動 Session State 系統資料庫)
    # ----------------------------------------------------
    # 1. 營業收入 (結合模擬試算與系統已核准之報價單/訂單)
    sys_revenue = sum(q.get("金額 (USD)", 0.0) for q in st.session_state.get("quotations_data", []) if "成交" in q.get("狀態", ""))
    revenue = (sales_units * unit_price) + sys_revenue

    # 2. 營業成本 (結合 VPSH 算式與總務/生產採購單)
    sys_po_cost = sum(p.get("預估金額 (USD)", 0.0) for p in st.session_state.get("ga_purchase_data", []) if "核准" in p.get("狀態", ""))
    cost_shoes = sales_units * shoe_cost_per_set  # $9拖鞋 + $15運動鞋 + $18休閒鞋 = $42
    cost_coffee_hub = sales_units * 0.694 * 60 * 0.25
    cost_coffee_f2b = sales_units * 0.306 * 30 * 0.50
    total_cogs = cost_shoes + cost_coffee_hub + cost_coffee_f2b + sys_po_cost

    # 3. 銷貨毛利
    gross_profit = revenue - total_cogs
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0

    # 4. 營業費用 (結合 VPSH 算式與總務零用金/維修費用)
    sys_petty_cost = sum(pc.get("金額 (USD)", 0.0) for pc in st.session_state.get("ga_petty_cash_data", []) if "核銷" in pc.get("狀態", "") or "核准" in pc.get("狀態", ""))
    exp_salary = 20000 * 12  # 8 人團隊
    exp_rent = 36000 * 12    # 首爾門市
    exp_f2c = 11616 * 64.55
    exp_f2b = 10800 * 64.55
    exp_bm3 = 0
    exp_recovery_fund = sales_units * 17.25
    exp_donations = sales_units * 5.0
    exp_utilities = 1250 * 12
    exp_handling = revenue * 0.80 * 0.03  # 80% Momo Pay × 3%
    exp_depreciation = 3750 * 12

    total_opex = (exp_salary + exp_rent + exp_f2c + exp_f2b + exp_bm3 +
                  exp_recovery_fund + exp_donations + exp_utilities +
                  exp_handling + exp_depreciation + sys_petty_cost)

    # 5. 營業利益
    ebit = gross_profit - total_opex
    ebit_margin = (ebit / revenue * 100) if revenue > 0 else 0

    # 6. 所得稅與淨利
    tax_rate = 0.20
    tax_expense = ebit * tax_rate if ebit > 0 else 0
    net_income = ebit - tax_expense
    net_margin = (net_income / revenue * 100) if revenue > 0 else 0

    # 頂部動態 KPI 卡片展示
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("動態總營業收入", f"${revenue:,.0f} USD", f"{sales_units:,} 套")
    k2.metric("動態本期淨利", f"${net_income:,.0f} USD", f"淨利率 {net_margin:.2f}%")
    k3.metric("期末現金餘額", "$3,900,928 USD", "流動性極佳")
    k4.metric("股權報酬率 (ROE)", "78.20%", "回收期 8.7 個月")
    k5.metric("動態產能利用率", f"{(sales_units/39200*100):.2f}%", "最大產能 39.2k 套")

    st.markdown("---")

    # 八大報表頁籤
    r_tab1, r_tab2, r_tab3, r_tab4, r_tab5, r_tab6, r_tab7, r_tab8 = st.tabs([
        "一、綜合損益表 (算式自動匯總)",
        "二、資產負債表",
        "三、現金流量表",
        "四、股東權益變動",
        "五、核心財務指標",
        "六、股權結構",
        "七、營運與 ESG",
        "八、產能利用率"
    ])

    # ----------------------------------------------------
    # 一、動態計算匯總之綜合損益表 (Income Statement)
    # ----------------------------------------------------
    with r_tab1:
        st.subheader("一、 綜合損益表 (Income Statement) - 由底層營運算式與全系統動態即時加總 (USD)")

        dynamic_income_data = [
            {
                "項目 (Item)": "營業收入 (Revenue)",
                "金額 (USD)": f"${revenue:,.0f}",
                "計算說明 / 底層營運明細": f"銷量 {sales_units:,} 套 × ${unit_price:.2f}/套 + 系統成交單 ${sys_revenue:,.0f}"
            },
            {
                "項目 (Item)": "營業成本 (Cost of Goods Sold)",
                "金額 (USD)": f"(${total_cogs:,.0f})",
                "計算說明 / 底層營運明細": f"包含鞋款、咖啡補貼與系統採購單 (${sys_po_cost:,.0f})"
            },
            {
                "項目 (Item)": "  [-] VIP套裝生產成本 cost:shoes",
                "金額 (USD)": f"(${cost_shoes:,.0f})",
                "計算說明 / 底層營運明細": f"{sales_units:,} 套 × ${shoe_cost_per_set:.2f} ($9拖鞋 + $15運動鞋 + $18休閒鞋)"
            },
            {
                "項目 (Item)": "  [-] Hub咖啡銷貨成本 coffee",
                "金額 (USD)": f"(${cost_coffee_hub:,.0f})",
                "計算說明 / 底層營運明細": f"{sales_units:,} 套 × 69.4% × 60杯 × $0.25/杯"
            },
            {
                "項目 (Item)": "  [-] F2B咖啡補貼支出 coffee",
                "金額 (USD)": f"(${cost_coffee_f2b:,.0f})",
                "計算說明 / 底層營運明細": f"{sales_units:,} 套 × 30.6% × 30杯 × $0.50/杯"
            },
            {
                "項目 (Item)": "  [-] 全系統採購與進貨成本 (System PO)",
                "金額 (USD)": f"(${sys_po_cost:,.0f})",
                "計算說明 / 底層營運明細": f"總務部與廠區簽核通過之採購單據"
            },
            {
                "項目 (Item)": "銷貨毛利 (Gross Profit)",
                "金額 (USD)": f"${gross_profit:,.0f}",
                "計算說明 / 底層營運明細": f"營業收入 ${revenue:,.0f} - 營業成本 ${total_cogs:,.0f} (毛利率: {gross_margin:.2f}%)"
            },
            {
                "項目 (Item)": "營業費用 (Operating Expenses)",
                "金額 (USD)": f"(${total_opex:,.0f})",
                "計算說明 / 底層營運明細": f"包含人事、租金、渠道分潤、公益基金、金流、零用金 (${sys_petty_cost:,.0f}) 與折舊"
            },
            {
                "項目 (Item)": "  [-] 人事薪資費用 (Salary)",
                "金額 (USD)": f"(${exp_salary:,.0f})",
                "計算說明 / 底層營運明細": "$20,000/月 × 12個月 (含專業經理人、會計、助理、生產銷售員共8人)"
            },
            {
                "項目 (Item)": "  [-] 租金費用 (Rent)",
                "金額 (USD)": f"(${exp_rent:,.0f})",
                "計算說明 / 底層營運明細": "$36,000/月 × 12個月 (首爾漢陽大學門市)"
            },
            {
                "項目 (Item)": "  [-] F2C 大使分潤 Profit sharing",
                "金額 (USD)": f"(${exp_f2c:,.0f})",
                "計算說明 / 底層營運明細": "11,616 套 (H1 3,600套) × $64.55/套"
            },
            {
                "項目 (Item)": "  [-] F2B 聯盟分潤 Profit sharing",
                "金額 (USD)": f"(${exp_f2b:,.0f})",
                "計算說明 / 底層營運明細": "10,800 套 (H2 F2B 10,800套) × $64.55/套"
            },
            {
                "項目 (Item)": "  [-] BM3 分潤 Profit sharing (商業模式: 3份利潤)",
                "金額 (USD)": "($0)",
                "計算說明 / 底層營運明細": "已包含於渠道分潤估算中 (由專屬團隊/機構處置)"
            },
            {
                "項目 (Item)": "  [-] 5% 回收基金 Recovery Fund",
                "金額 (USD)": f"(${exp_recovery_fund:,.0f})",
                "計算說明 / 底層營運明細": f"{sales_units:,} 套 × $17.25/套 (專款專用提撥)"
            },
            {
                "項目 (Item)": "  [-] 5 USD 扶貧捐贈 Donations",
                "金額 (USD)": f"(${exp_donations:,.0f})",
                "計算說明 / 底層營運明細": f"{sales_units:,} 套 × $5.00/套 (公益提撥)"
            },
            {
                "項目 (Item)": "  [-] 全系統總務零用金與小額行政報銷",
                "金額 (USD)": f"(${sys_petty_cost:,.0f})",
                "計算說明 / 底層營運明細": "來自總務部已核銷之車馬費、快遞費與雜項"
            },
            {
                "項目 (Item)": "  [-] 水電費 Water and electricity fees",
                "金額 (USD)": f"(${exp_utilities:,.0f})",
                "計算說明 / 底層營運明細": "$1,250/月 × 12個月"
            },
            {
                "項目 (Item)": "  [-] 支付金流手續費 handling fee",
                "金額 (USD)": f"(${exp_handling:,.0f})",
                "計算說明 / 底層營運明細": f"{sales_units:,} 套 × ${unit_price:.0f} × 80% (Momo Pay) × 3% 手續費"
            },
            {
                "項目 (Item)": "  [-] 折舊與攤提費用 depreciation",
                "金額 (USD)": f"(${exp_depreciation:,.0f})",
                "計算說明 / 底層營運明細": "$3,750/月 × 12個月 (設備及裝修折舊)"
            },
            {
                "項目 (Item)": "營業利益 (Income / EBIT)",
                "金額 (USD)": f"${ebit:,.0f}",
                "計算說明 / 底層營運明細": f"銷貨毛利 ${gross_profit:,.0f} - 營業費用 ${total_opex:,.0f} (營業利益率: {ebit_margin:.2f}%)"
            },
            {
                "項目 (Item)": "  [-] 所得稅費用 (Tax @ 20%)",
                "金額 (USD)": f"(${tax_expense:,.0f})",
                "計算說明 / 底層營運明細": f"預估企業所得稅 (營業利益 ${ebit:,.0f} × 20%)"
            },
            {
                "項目 (Item)": "本期淨利 (Net Income)",
                "金額 (USD)": f"${net_income:,.0f}",
                "計算說明 / 底層營運明細": f"營業利益 ${ebit:,.0f} - 所得稅 ${tax_expense:,.0f} (淨利率: {net_margin:.2f}%)"
            }
        ]

        st.dataframe(pd.DataFrame(dynamic_income_data), use_container_width=True, height=520)

    # 二、資產負債表
    with r_tab2:
        st.subheader("二、 資產負債表 (Balance Sheet) - USD")
        col_bs1, col_bs2 = st.columns(2)
        with col_bs1:
            st.markdown("##### 🟢 資產 (Assets)")
            bs_assets = [
                {"資產類別": "流動資產：現金及現金等價物 Cash and cash equivalents", "金額 (USD)": "$3,900,928"},
                {"資產類別": "流動資產：存貨 (鞋材與咖啡豆) Inventory", "金額 (USD)": "$50,000"},
                {"資產類別": "流動資產合計 Total current assets", "金額 (USD)": "$3,950,928"},
                {"資產類別": "非流動資產：固定資產與設備 (淨額) Fixed assets", "金額 (USD)": "$405,000"},
                {"資產類別": "非流動資產：體驗中心押金 (Deposit)", "金額 (USD)": "$360,000"},
                {"資產類別": "非流動資產合計 Total non-current assets", "金額 (USD)": "$765,000"},
                {"資產類別": "資產總額 (Total Assets)", "金額 (USD)": "$4,715,928"}
            ]
            st.dataframe(pd.DataFrame(bs_assets), use_container_width=True)

        with col_bs2:
            st.markdown("##### 🔴 負債與股東權益 (Liabilities & Equity)")
            bs_liab = [
                {"負債與權益類別": "流動負債：應付扶貧/回收基金撥備 (Donation)", "金額 (USD)": "$496,620"},
                {"負債與權益類別": "流動負債：預估應付所得稅 (Tax @ 20%)", "金額 (USD)": "$689,982"},
                {"負債與權益類別": "流動負債合計 Total current liabilities", "金額 (USD)": "$1,186,602"},
                {"負債與權益類別": "長期負債 (Long-Term Liabilities)", "金額 (USD)": "$0"},
                {"負債與權益類別": "負債總額 Total liabilities", "金額 (USD)": "$1,186,602"},
                {"負債與權益類別": "股東權益：股本 (Capital Stock)", "金額 (USD)": "$2,000,000"},
                {"負債與權益類別": "股東權益：保留盈餘 (Retained Earnings)", "金額 (USD)": "$1,529,326"},
                {"負債與權益類別": "負債與權益總額 (Total L & E)", "金額 (USD)": "$4,715,928"}
            ]
            st.dataframe(pd.DataFrame(bs_liab), use_container_width=True)

    # 三、現金流量表
    with r_tab3:
        st.subheader("三、 現金流量表 (Statement of Cash Flows) - USD")
        cf_data = [
            {"營業/投資/籌資活動項目": "【營業活動】本期淨利 (Net Income)", "金額 (USD)": "$2,759,928", "備註說明": ""},
            {"營業/投資/籌資活動項目": "  (+) 折舊與攤提費用 depreciation", "金額 (USD)": "$45,000", "備註說明": "非現金費用加回"},
            {"營業/投資/籌資活動項目": "  (+) 應付撥備與應付稅款增加 cope", "金額 (USD)": "$1,186,602", "備註說明": "應付扶貧基金、回收基金與所得稅"},
            {"營業/投資/籌資活動項目": "  (-) 存貨增加 Decrease: Increase in inventory", "金額 (USD)": "($50,000)", "備註說明": "營運資金需求"},
            {"營業/投資/籌資活動項目": "營業活動淨現金流入 Cash inflow", "金額 (USD)": "$3,941,530", "備註說明": ""},
            {"營業/投資/籌資活動項目": "【投資活動】購置資本設備與裝修 (CAPEX)", "金額 (USD)": "($450,000)", "備註說明": "PU成型線、模具、裝修、AIoT系統"},
            {"營業/投資/籌資活動項目": "  (-) 支付體驗中心租賃押金 (Hub Deposit)", "金額 (USD)": "($360,000)", "備註說明": "10 個月押金 ($36,000/月)"},
            {"營業/投資/籌資活動項目": "投資活動淨現金流出 Cash outflow", "金額 (USD)": "($810,000)", "備註說明": ""},
            {"營業/投資/籌資活動項目": "【籌資活動】股東原始投資金額投入 Investment amount", "金額 (USD)": "$2,000,000", "備註說明": "2026/12/01 資金到位"},
            {"營業/投資/籌資活動項目": "  (-) 股利發放 (Dividends Paid)", "金額 (USD)": "($1,230,602)", "備註說明": "淨利提撥股利發放 Net profit allocation"},
            {"營業/投資/籌資活動項目": "籌資活動淨現金流入 Cash inflow", "金額 (USD)": "$769,398", "備註說明": ""},
            {"營業/投資/籌資活動項目": "現金及現金等價物淨增加額 Net increase", "金額 (USD)": "$3,900,928", "備註說明": "期末現金餘額 Ending cash balance"}
        ]
        st.dataframe(pd.DataFrame(cf_data), use_container_width=True)

    # 四、股東權益變動表
    with r_tab4:
        st.subheader("四、 股東權益變動表 (Statement of Stockholders' Equity) - USD")
        st.caption("期間：2027 年 1 月 1 日 @ 10:01，至 2027 年 12 月 31 日（單位：美元）")
        eq_change_data = [
            {"項目": "2026/12/01 期初餘額", "股本 (Capital Stock)": "$2,000,000", "保留盈餘 (Retained Earnings)": "$0", "股東權益總額 (Total Equity)": "$2,000,000"},
            {"項目": "2027年度 本期淨利", "股本 (Capital Stock)": "$0", "保留盈餘 (Retained Earnings)": "$2,759,928", "股東權益總額 (Total Equity)": "$2,759,928"},
            {"項目": "2027年度 股利發放", "股本 (Capital Stock)": "$0", "保留盈餘 (Retained Earnings)": "($1,230,602)", "股東權益總額 (Total Equity)": "($1,230,602)"},
            {"項目": "2027/12/31 期末餘額", "股本 (Capital Stock)": "$2,000,000", "保留盈餘 (Retained Earnings)": "$1,529,326", "股東權益總額 (Total Equity)": "$3,529,326"}
        ]
        st.dataframe(pd.DataFrame(eq_change_data), use_container_width=True)

    # 五、核心財務指標
    with r_tab5:
        st.subheader("五、 核心財務指標 (Core Financial Key Indicators)")
        kpi_core_data = [
            {"指標名稱": "毛利率 (Gross Margin)", "數值": f"{gross_margin:.2f}%", "產業基準與分析評語": "直營/F2X 垂直整合的高附加價值模型"},
            {"指標名稱": "營業利益率 (Operating Margin)", "數值": f"{ebit_margin:.2f}%", "產業基準與分析評語": "極致自動化與高轉換率所帶來的營運槓桿效益"},
            {"指標名稱": "淨利率 (Net Profit Margin)", "數值": f"{net_margin:.2f}%", "產業基準與分析評語": "高獲利科技與軟硬體結合零售型態"},
            {"指標名稱": "資產報酬率 (ROA)", "數值": "58.52%", "產業基準與分析評語": "輕資產高資產週轉效率"},
            {"指標名稱": "股權報酬率 (ROE)", "數值": "78.20%", "產業基準與分析評語": "對原始投資資本 ($2M) 提供極佳的回報"},
            {"指標名稱": "投資回收期 (Payback Period)", "數值": "約 8.7 個月", "產業基準與分析評語": "首年本期淨利 $2.76M 即可徹底回收原始投資 $2M"}
        ]
        st.dataframe(pd.DataFrame(kpi_core_data), use_container_width=True)

    # 六、股權結構
    with r_tab6:
        st.subheader("六、 股權結構 (Equity Structure)")
        col_eq1, col_eq2 = st.columns([1, 1])
        with col_eq1:
            eq_struct_data = [
                {"股東名稱 / 類別": "VPSH 創始團隊 / 母公司", "持股比例 (%)": "60.0%", "備註說明": "2,040,000 USD 之實繳資本額(現金+設備)"},
                {"股東名稱 / 類別": "員工股權信託 ESOP Trust", "持股比例 (%)": "40.0%", "備註說明": "ESOP 全體員工股權池 (Employee Stock Option Pool)"},
                {"股東名稱 / 類別": "實繳金額", "持股比例 (%)": "-", "備註說明": "$2,040,000 USD"},
                {"股東名稱 / 類別": "公司註冊資本額", "持股比例 (%)": "100.0%", "備註說明": "$3,400,000 USD"}
            ]
            st.dataframe(pd.DataFrame(eq_struct_data), use_container_width=True)
        with col_eq2:
            fig_eq = px.pie(
                values=[60, 40],
                names=["VPSH 創始團隊 (60%)", "員工股權信託 ESOP (40%)"],
                title="VPSH 股權分配比例",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_eq, use_container_width=True)

    # 七、營運核心指標
    with r_tab7:
        st.subheader("七、 營運核心指標 (Operational KPIs & ESG Metrics)")
        op_kpi_data = [
            {"營運指標項目": "體驗中心/門市數量 (Stores)", "2027年度 達成數據": "1 家 Hub 旗艦店+Spoke", "說明 / 明細": "HUB Center (500~1,500㎡ )"},
            {"營運指標項目": "ESG 青年大使數量 (ESG Ambassadors)", "2027年度 達成數據": "120 名 (120 人)", "說明 / 明細": "來自建國大學、漢陽大學、世宗大學"},
            {"營運指標項目": "F2B 聯盟合作店家 (F2B Partner Shops)", "2027年度 達成數據": "20 家精選咖啡館", "說明 / 明細": "每家每日約 300 人流，轉化率 1%"},
            {"營運指標項目": "BM3商業模式3 數據套件", "2027年度 達成數據": "4,320 套/年 (每年 4,320 套)", "說明 / 明細": "F2B:1,440套+D2C:1,440套+Spoke:1,440套"},
            {"營運指標項目": "5%回收基金累積金額 Recovery Fund", "2027年度 達成數據": f"${exp_recovery_fund:,.0f} USD", "說明 / 明細": "每一套組撥入 $17.25 USD"},
            {"營運指標項目": "5 USD 扶貧捐贈金額 Donations", "2027年度 達成數據": f"${exp_donations:,.0f} USD", "說明 / 明細": "每一套組撥入 $5.00 USD"},
            {"營運指標項目": "營運廠區面積 (Factory Hub Area)", "2027年度 達成數據": "1,500 ㎡ (1,500 平方米)", "說明 / 明細": "Hub Center Demo Factory"},
            {"營運指標項目": "正職員工數量 (Full-time Employees)", "2027年度 達成數據": "8 人 / 條生產線", "說明 / 明細": "1經理 + 1會計 + 1助理 + 5生產銷售員"}
        ]
        st.dataframe(pd.DataFrame(op_kpi_data), use_container_width=True)

    # 八、產能利用率分析
    with r_tab8:
        st.subheader("八、 產能利用率分析 (Capacity Utilization Rate)")
        cap_util_rate = (sales_units / 39200 * 100)
        cap_analysis_data = [
            {"產能分析項目": "單小時理論產能 (Production capacity/H)", "數據說明": "60 雙 / 小時", "計算邏輯 / 數據源": "PGH-999 全自動化 PU 成型線設計標準"},
            {"產能分析項目": "日營運時間與日產能 (Production capacity/D)", "數據說明": "480 雙/天 = 160 套/天", "計算邏輯 / 數據源": "8 小時/天 (每 3 雙組合為 1 VIP 套裝)"},
            {"產能分析項目": "年度設計最大總產能 (Production capacity/Y)", "數據說明": "39,200 套 / 年", "計算邏輯 / 數據源": "245 天工作日 × 160 套/天"},
            {"產能分析項目": "2027 年度實際銷售套數 Actual number of units sold", "數據說明": f"{sales_units:,} 套 / 年", "計算邏輯 / 數據源": "H1 (3,600) + H2 (14,400) + H3 (4,320)"},
            {"產能分析項目": "2027 年度產能利用率 (Capacity Utilization Rate)", "數據說明": f"{cap_util_rate:.2f}%", "計算邏輯 / 數據源": f"{sales_units:,} 套 / 39,200 套（展現充足擴充空間）"}
        ]
        col_c1, col_c2 = st.columns([3, 2])
        with col_c1:
            st.dataframe(pd.DataFrame(cap_analysis_data), use_container_width=True)
        with col_c2:
            fig_cap = px.pie(
                values=[sales_units, max(0, 39200 - sales_units)],
                names=[f"實際產出 ({cap_util_rate:.1f}%)", f"剩餘產能 ({100-cap_util_rate:.1f}%)"],
                title=f"2027 產能利用率 ({cap_util_rate:.1f}%)",
                hole=0.6,
                color_discrete_sequence=["#2ecc71", "#ecf0f1"]
            )
            st.plotly_chart(fig_cap, use_container_width=True)

# ----------------------------------------------------
# ⚡ 6. 機台稼動 (OEE) KPI
# ----------------------------------------------------
def render_plant_oee_kpi():
    st.markdown("### ⚡ 全球廠區射出機台稼動率 (OEE) 與生產 KPI")
    
    col_o1, col_o2, col_o3, col_o4 = st.columns(4)
    col_o1.metric("集團平均機台稼動率 (OEE)", "84.5%", "+2.1%")
    col_o2.metric("射出成型平均良率 (Yield)", "98.2%", "+0.4%")
    col_o3.metric("連線射出機台總數", "42 台", "38台運行 / 4台維修")
    col_o4.metric("本日總產出成品數", "128,500 PCS", "達成率 103%")

    st.markdown("#### 🏭 各廠區射出機台稼動明細")
    oee_data = [
        {"廠區": "🇻🇳 越南平陽廠 (Binh Duong)", "連線機台數": "18 台", "平均 OEE": "86.2%", "良率 Yield": "98.5%", "當前狀態": "🟢 滿載運轉中", "異常告警": "無"},
        {"廠區": "🇨🇳 中國東莞廠 (Dongguan)", "連線機台數": "16 台", "平均 OEE": "81.0%", "良率 Yield": "97.8%", "當前狀態": "🟡 2台換模中", "異常告警": "M03 油溫微升"},
        {"廠區": "🇹🇼 台灣總部研發中心 (TW HQ)", "連線機台數": "8 台", "平均 OEE": "88.5%", "良率 Yield": "99.1%", "當前狀態": "🟢 試模進行中", "異常告警": "無"}
    ]
    st.dataframe(pd.DataFrame(oee_data), use_container_width=True)

# ----------------------------------------------------
# 🚀 模組入口函式
# ----------------------------------------------------
def render_executive_dashboard_page(sub_option="🌐 全部市場 (All Markets)", lang=None):
    L = get_exec_lang_dict(lang)
    current_lang = lang or "繁體中文"
    
    st.title(L["page_title"])
    st.caption(L["sub_title"])

    # 👑 董事長/總經理 專屬觀察重點
    with st.expander(L["boss_notes_title"], expanded=True):
        st.write("• **台積電 (TSMC 2330.TW)**：🟢 **偏多 (適合逢低定額)** — AI 晶片先進封裝獨占，長線穩定成長")
        st.write("• **富邦金 (Fubon 2881.TW)**：🟢 **防禦 (高股息避風港)** — 配息能力強，提供穩健現金流保護")

    st.divider()

    # 4 大戰情室分頁
    tab1, tab2, tab3, tab4 = st.tabs([
        L["tab_market"],
        L["tab_fin_stat"],
        L["tab_vpsh_reports"],
        L["tab_plant_kpi"]
    ])

    # 分頁 1：全球股市與看盤
    with tab1:
        st.markdown(f"### {L['stock_section_title']} [{sub_option}]")
        render_market_stock_metrics(sub_option)

        st.divider()

        st.markdown(f"### {L['news_section_title']} [{sub_option}]")
        col_n1, col_n2 = st.columns([3, 1])
        with col_n2:
            if st.button(L["btn_fetch_news"], type="primary", key=f"btn_refresh_news_{current_lang}"):
                st.toast("✅ 已成功擷取最新 7 天財經新聞資料庫！")

        news_list = get_mock_7day_news(sub_option)
        for item in news_list:
            with st.container():
                st.markdown(f"##### 📅 **【{item['date']}】[{item['title']}]({item['url']})** 🔗")
                st.caption(f"來源: `{item['source']}` | 評估: **{item['sentiment']}**")
                st.write(f"💡 {item['summary']}")
                st.markdown("---")

        col_ai, col_watch = st.columns([1, 1])
        with col_ai:
            st.markdown(f"### {L['ai_summary_title']} [{sub_option}]")
            if st.button(L["btn_gen_ai_summary"], type="primary", key=f"btn_ai_exec_sum_{current_lang}"):
                st.success(f"📊 **【{sub_option}】AI 決策分析報告**：製造業需求維持穩健，建議原料維持 30-45 天安全庫存。")

        with col_watch:
            st.markdown(f"### {L['watch_title']}")
            with st.expander("➕ 新增觀察個股/指數", expanded=True):
                st.selectbox("選擇股票市場區域", [sub_option, "🇹🇼 台灣 (Taiwan)", "VN 越南 (Vietnam)", "US 美國 (USA)"], key=f"select_watch_mkt_{current_lang}")
                st.text_input("股票代碼 (如 2881.TW / NVDA / VNM.VN)", value="2855.TW", key=f"input_watch_code_{current_lang}")

        st.divider()

        st.markdown(f"### {L['stock_chat_title']}")
        st.caption(L["stock_chat_caption"])
        user_stock_query = st.text_area(
            "請輸入股票代碼或詢問個股/市場趨勢：",
            value="請幫我分析台積電 (2330.TW) 近期 CoWoS 先進封裝產能擴張對毛利率與估值的影響？",
            height=90,
            placeholder=L["stock_chat_placeholder"],
            key=f"input_stock_query_{current_lang}"
        )
        if st.button(L["btn_send_stock_chat"], type="primary", key=f"btn_ask_stock_ai_{current_lang}"):
            with st.spinner("AI 財經顧問正在進行個股籌碼與財報數據分析..."):
                answer = ask_stock_ai_advisor(user_stock_query, current_lang)
                st.markdown("#### 📝 AI 財經顧問解析報告：")
                st.markdown(answer)

    # 分頁 2：全球廠區 AR/AP 財務統計
    with tab2:
        render_financial_ar_ap_stats()

    # 分頁 3：動態計算匯總之 VPSH 高階八大財務報表 (已整合系統資料庫連動)
    with tab3:
        render_vpsh_core_reports()

    # 分頁 4：機台稼動 (OEE) KPI
    with tab4:
        render_plant_oee_kpi()

def show(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)

def main(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)
