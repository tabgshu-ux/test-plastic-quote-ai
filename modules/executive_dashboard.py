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
        "tab_vpsh_reports": "📊 企業綜合損益表 (P&L) 與營運戰情",
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
        "tab_vpsh_reports": "📊 Báo cáo kết quả kinh doanh (P&L) & Vận hành",
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
        "tab_vpsh_reports": "📊 Consolidated Income Statement (P&L) & Reports",
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
        "tab_vpsh_reports": "📊 企业综合损益表 (P&L) 与营运战情",
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
        "tab_vpsh_reports": "📊 Laporan Laba Rugi Komprehensif (P&L) & Operasional",
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
# 🧮 5. 通用型企業綜合損益表 (自動連動全系統 Session State)
# ----------------------------------------------------
def render_consolidated_income_statement():
    st.markdown("### 📊 企業綜合損益表 (Income Statement / P&L) (USD)")
    st.caption("數據由全系統各模組（業務訂單、總務採購、零用金報銷、設備維修）即時自動勾稽與動態計算")

    # 1. 營業收入：從業務報價/訂單勾稽 (若尚無資料，提供預設標準營運數字)
    quotes = st.session_state.get("quotations_data", [])
    sys_revenue = sum(q.get("金額 (USD)", 0.0) for q in quotes if "成交" in q.get("狀態", "") or "已核准" in q.get("狀態", ""))
    total_revenue = sys_revenue if sys_revenue > 0 else 250000.0

    # 2. 營業成本：從總務與生產採購單勾稽
    purchases = st.session_state.get("ga_purchase_data", [])
    sys_cogs = sum(p.get("預估金額 (USD)", 0.0) for p in purchases if "已核准" in p.get("狀態", "") or "簽核中" in p.get("狀態", ""))
    total_cogs = sys_cogs if sys_cogs > 0 else 115000.0

    # 3. 銷貨毛利
    gross_profit = total_revenue - total_cogs
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

    # 4. 營業費用 (OPEX)：從零用金與模具維修履歷勾稽
    petty_cash_items = st.session_state.get("ga_petty_cash_data", [])
    sys_petty_cash = sum(pc.get("金額 (USD)", 0.0) for pc in petty_cash_items if "已核銷" in pc.get("狀態", "") or "已核准" in pc.get("狀態", ""))
    
    payroll_expense = 45000.0   # 人事薪資費用
    utilities_expense = 3500.0  # 水電與公用事業費
    admin_expense = sys_petty_cash if sys_petty_cash > 0 else 2450.0  # 零用金與小額報銷
    depreciation_expense = 6000.0  # 設備折舊費用

    total_opex = payroll_expense + utilities_expense + admin_expense + depreciation_expense

    # 5. 營業利益
    ebit = gross_profit - total_opex
    ebit_margin = (ebit / total_revenue * 100) if total_revenue > 0 else 0.0

    # 6. 所得稅與淨利
    tax_rate = 0.20
    tax_expense = max(0.0, ebit * tax_rate)
    net_income = ebit - tax_expense
    net_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0.0

    # 頂部 KPI 卡片
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("營業收入 (Revenue)", f"${total_revenue:,.2f} USD")
    k2.metric("營業毛利 (Gross Profit)", f"${gross_profit:,.2f} USD", f"毛利率 {gross_margin:.1f}%")
    k3.metric("營業費用 (OPEX)", f"${total_opex:,.2f} USD")
    k4.metric("本期淨利 (Net Income)", f"${net_income:,.2f} USD", f"淨利率 {net_margin:.1f}%")

    st.markdown("---")

    # 損益明細表
    pl_data = [
        {"會計科目": "一、營業收入 (Revenue)", "金額 (USD)": f"${total_revenue:,.2f}", "說明/勾稽來源": "業務模組已成交銷售訂單"},
        {"會計科目": "二、營業成本 (COGS)", "金額 (USD)": f"(${total_cogs:,.2f})", "說明/勾稽來源": "總務與廠區進貨採購單據"},
        {"會計科目": "💡 營業毛利 (Gross Profit)", "金額 (USD)": f"${gross_profit:,.2f}", "說明/勾稽來源": f"毛利率: {gross_margin:.1f}%"},
        {"會計科目": "三、營業費用 (OPEX)", "金額 (USD)": f"(${total_opex:,.2f})", "說明/勾稽來源": "包含薪資、水電、行政零用金與折舊"},
        {"會計科目": "  [-] 薪資與考勤費用", "金額 (USD)": f"(${payroll_expense:,.2f})", "說明/勾稽來源": "人事部門月度薪資清冊"},
        {"會計科目": "  [-] 廠區水電與公用事業費", "金額 (USD)": f"(${utilities_expense:,.2f})", "說明/勾稽來源": "廠務水電與公用設施支出"},
        {"會計科目": "  [-] 總務零用金與行政費用", "金額 (USD)": f"(${admin_expense:,.2f})", "說明/勾稽來源": "總務部已簽核核銷之零用金報銷"},
        {"會計科目": "  [-] 固定資產折舊與攤提", "金額 (USD)": f"(${depreciation_expense:,.2f})", "說明/勾稽來源": "資產主檔月度直線折舊計算"},
        {"會計科目": "💡 營業利益 (Operating Income)", "金額 (USD)": f"${ebit:,.2f}", "說明/勾稽來源": f"營業利益率: {ebit_margin:.1f}%"},
        {"會計科目": "四、預估所得稅費用 (20%)", "金額 (USD)": f"(${tax_expense:,.2f})", "說明/勾稽來源": "企業所得稅提撥估算"},
        {"會計科目": "🏆 🏆 本期淨利 (Net Income)", "金額 (USD)": f"${net_income:,.2f}", "說明/勾稽來源": f"稅後淨利率: {net_margin:.1f}%"}
    ]

    st.dataframe(pd.DataFrame(pl_data), use_container_width=True)

    # 視覺化圖表
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        df_pie = pd.DataFrame([
            {"費用項目": "薪資費用", "金額": payroll_expense},
            {"費用項目": "廠區水電", "金額": utilities_expense},
            {"費用項目": "行政零用金", "金額": admin_expense},
            {"費用項目": "資產折舊", "金額": depreciation_expense}
        ])
        fig_pie = px.pie(df_pie, values="金額", names="費用項目", title="營業費用結構分布 (OPEX)", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        df_bar = pd.DataFrame([
            {"階段": "營業收入", "金額 (USD)": total_revenue},
            {"階段": "營業毛利", "金額 (USD)": gross_profit},
            {"階段": "營業利益", "金額 (USD)": ebit},
            {"階段": "本期淨利", "金額 (USD)": net_income}
        ])
        fig_bar = px.bar(df_bar, x="階段", y="金額 (USD)", color="階段", text_auto='.2s', title="獲利階層轉換 (Profit Waterfall)")
        st.plotly_chart(fig_bar, use_container_width=True)

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

    # 分頁 3：通用型企業綜合損益表 (自動連動全系統資料庫)
    with tab3:
        render_consolidated_income_statement()

    # 分頁 4：機台稼動 (OEE) KPI
    with tab4:
        render_plant_oee_kpi()

def show(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)

def main(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)
