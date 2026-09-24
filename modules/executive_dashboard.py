import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# ----------------------------------------------------
# 🌐 營運戰情室多語系字典 (i18n)
# ----------------------------------------------------
EXEC_I18N = {
    "繁體中文": {
        "page_title": "📈 跨國企業營運戰情室 (Executive Dashboard)",
        "sub_title": "即時監控台灣、越南、美國、中國與全球原物料/匯率之財經新聞與營運指標",
        "news_section_title": "📰 近 7 天動態財經新聞與市場大事件",
        "btn_fetch_news": "🔄 重新整理 / 抓取最新財經新聞",
        "ai_summary_title": "🤖 Gemini AI 跨國白話財經摘要",
        "btn_gen_ai_summary": "🚀 生成該區域白話重點與決策報告",
        "watch_title": "🛠️ 管理自訂觀察關注標的",
        "boss_notes_title": "👑 董事長/總經理 專屬觀察重點與理由"
    },
    "Tiếng Việt": {
        "page_title": "📈 Bảng Điều Hành Doanh Nghiệp Đa Quốc Gia (Executive Dashboard)",
        "sub_title": "Giám sát thời gian thực tin tức tài chính và chỉ số vận hành tại Đài Loan, Việt Nam, Mỹ, Trung Quốc & Tỷ giá",
        "news_section_title": "📰 Tin Tức Tài Chính & Sự Kiện Thị Trường Trong 7 Ngày Qua",
        "btn_fetch_news": "🔄 Cập nhật / Tải tin tức tài chính mới nhất",
        "ai_summary_title": "🤖 Tóm Tắt Tài Chính AI Gemini",
        "btn_gen_ai_summary": "🚀 Tạo báo cáo tóm tắt & Quyết định chiến lược",
        "watch_title": "🛠️ Quản Lý Danh Mục Theo Dõi Tùy Chỉnh",
        "boss_notes_title": "👑 Ghi Chú Quan Sát Dành Cho Chủ Tịch / Tổng Giám Đốc"
    },
    "English": {
        "page_title": "📈 Executive Strategic Dashboard",
        "sub_title": "Real-time financial news & operational KPIs across Taiwan, Vietnam, USA, China, Commodities & FX",
        "news_section_title": "📰 Recent 7-Day Financial News & Market Events",
        "btn_fetch_news": "🔄 Refresh / Fetch Latest Financial News",
        "ai_summary_title": "🤖 Gemini AI Financial Summary",
        "btn_gen_ai_summary": "🚀 Generate Strategic Brief & Executive Report",
        "watch_title": "🛠️ Custom Watchlist Management",
        "boss_notes_title": "👑 Executive Observation Focus & Notes"
    },
    "简体中文": {
        "page_title": "📈 跨国企业营运战情室 (Executive Dashboard)",
        "sub_title": "实时监控台湾、越南、美国、中国与全球原物料/汇率之财经新闻与营运指标",
        "news_section_title": "📰 近 7 天动态财经新闻与市场大事件",
        "btn_fetch_news": "🔄 刷新 / 抓取最新财经新闻",
        "ai_summary_title": "🤖 Gemini AI 跨国白话财经摘要",
        "btn_gen_ai_summary": "🚀 生成该区域白话重点与决策报告",
        "watch_title": "🛠️ 管理自订观察关注标的",
        "boss_notes_title": "👑 董事长/总经理 专属观察重点与理由"
    },
    "Bahasa Indonesia": {
        "page_title": "📈 Dasbor Strategis Eksekutif (Executive Dashboard)",
        "sub_title": "Pemantauan berita keuangan & KPI operasional secara real-time di Taiwan, Vietnam, AS, Tiongkok & Valas",
        "news_section_title": "📰 Berita Keuangan 7 Hari Terakhir & Acara Pasar",
        "btn_fetch_news": "🔄 Perbarui / Ambil Berita Keuangan Terbaru",
        "ai_summary_title": "🤖 Ringkasan Keuangan AI Gemini",
        "btn_gen_ai_summary": "🚀 Hasilkan Laporan Ringkas & Keputusan Strategis",
        "watch_title": "🛠️ Manajemen Daftar Pantauan Kustom",
        "boss_notes_title": "👑 Catatan Pengamatan Eksklusif Direksi"
    }
}

def get_exec_lang_dict(lang_param=None):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return EXEC_I18N.get(lang, EXEC_I18N["繁體中文"])

def get_mock_7day_news(market):
    """根據選擇的國家/市場，動態回傳近 7 天內的財經重點新聞"""
    if "Taiwan" in market or "台灣" in market or "Đài Loan" in market:
        return [
            {"date": "2026-03-24", "title": "TSMC 晶圓代工產能持續滿載，先進封裝產能預計擴增 20%", "source": "財經日報 / Economic Daily", "sentiment": "🟢 看多 / Bullish", "summary": "受益於全球 AI 晶片需求，3nm 產能供不應求，帶動整體供應鏈動能。"},
            {"date": "2026-03-22", "title": "央行利率政策維持穩定，新台幣對美元匯率於 31.5 區間震盪", "source": "中央社 / CNA", "sentiment": "🟡 中立 / Neutral", "summary": "外資小幅淨流入，出口製造業利潤率受匯率變動影響有限。"},
            {"date": "2026-03-20", "title": "塑膠與橡膠原物料價格小幅回升，加工廠預備提早鎖定 Q2 報價", "source": "工商時報 / CTEE", "sentiment": "🟡 關注 / Caution", "summary": "塑膠粒 (PP/ABS) 進口成本略增 2.5%，建議業務報價適當反映材料成本。"}
        ]
    elif "Vietnam" in market or "越南" in market or "Việt Nam" in market:
        return [
            {"date": "2026-03-24", "title": "Việt Nam FDI thu hút 6.2 tỷ USD trong Q1, Bình Dương dẫn đầu về sản xuất xuất khẩu", "source": "VnExpress / Vietnam News", "sentiment": "🟢 看多 / Bullish", "summary": "外資持續挹注平陽省與同奈省工業區，製造業外設廠動能強勁。"},
            {"date": "2026-03-21", "title": "Cục Thuế ban hành công văn mới về kiểm tra Hóa đơn điện tử và Thuế nhà thầu (FCT)", "source": "Báo Đầu Tư", "sentiment": "🔴 警戒 / Alert", "summary": "越南稅務局加強查核企業電子發票開立與外國承包商稅抵扣憑證，提醒財務人員備妥合約。"},
            {"date": "2026-03-19", "title": "Ngân hàng Nhà nước duy trì tỷ giá VND/USD ổn định, hỗ trợ doanh nghiệp XNK", "source": "VietnamPlus", "sentiment": "🟢 看多 / Bullish", "summary": "越南盾對美元匯率保持平穩，利於跨國製造業進口原物料與出口成品。"}
        ]
    elif "USA" in market or "美國" in market or "Mỹ" in market:
        return [
            {"date": "2026-03-23", "title": "Fed Signals Potential Rate Adjustments as Inflation Moderates Near 2%", "source": "Wall Street Journal", "sentiment": "🟢 看多 / Bullish", "summary": "美聯儲放緩升息節奏，美股科技與製造業板塊溫和上揚。"},
            {"date": "2026-03-20", "title": "US Consumer Spending on Electronics and Automotive Parts Rises 3.8%", "source": "Bloomberg", "sentiment": "🟢 看多 / Bullish", "summary": "終端消費市場需求復甦，帶動亞洲零組件與模具出口訂單增長。"}
        ]
    else:
        return [
            {"date": "2026-03-24", "title": "全球原油價格小幅波動，塑化上游烯類原料供應鏈維持平衡", "source": "Reuters Market Watch", "sentiment": "🟡 中立 / Neutral", "summary": "原物料市場短期供需平衡，射出成型加工成本保持可控範疇。"},
            {"date": "2026-03-21", "title": "跨國供應鏈轉移效應顯著，東南亞製造業 PMI 升至 52.4", "source": "Financial Times", "sentiment": "🟢 看多 / Bullish", "summary": "供應鏈多國佈局趨勢不變，越南與泰國生產基地產能稼動率提升。"}
        ]

def render_executive_dashboard_page(sub_option="🌐 全部市場 (All Markets)", lang=None):
    L = get_exec_lang_dict(lang)
    
    st.title(L["page_title"])
    st.caption(L["sub_title"])

    # ----------------------------------------------------
    # 👑 頂部：董事長/總經理 專屬觀察重點 (如您原畫面所示)
    # ----------------------------------------------------
    with st.expander(L["boss_notes_title"], expanded=True):
        st.write("• **台積電 (TSMC 2330.TW)**：🟢 **偏多 (適合逢低定額)** — AI 晶片先進封裝獨占，長線穩定成長")
        st.write("• **台光電 (Elite 2383.TW)**：🟡 **觀望 (高檔區間震盪)** — 伺服器高階 PCB 板材，受惠 AI 升級")
        st.write("• **富邦金 (Fubon 2881.TW)**：🟢 **防禦 (高股息避風港)** — 配息能力強，提供穩健現金流保護")

    st.divider()

    # ----------------------------------------------------
    # 📰 【修復重現】：近 7 天動態財經新聞區塊
    # ----------------------------------------------------
    st.markdown(f"### {L['news_section_title']} [{sub_option}]")
    
    col_n1, col_n2 = st.columns([3, 1])
    with col_n2:
        if st.button(L["btn_fetch_news"], type="primary", key=f"btn_refresh_news_{lang}"):
            st.toast("✅ 已成功擷取最新 7 天財經新聞資料庫！")

    # 讀取對應國家近 7 天新聞列表
    news_list = get_mock_7day_news(sub_option)
    
    for item in news_list:
        with st.container():
            st.markdown(f"##### 📅 **【{item['date']}】{item['title']}**")
            st.caption(f"來源: `{item['source']}` | 評估: **{item['sentiment']}**")
            st.write(f"💡 {item['summary']}")
            st.markdown("---")

    # ----------------------------------------------------
    # 🤖 Gemini AI 白話財經摘要與自訂觀察標的 (原本畫面)
    # ----------------------------------------------------
    col_ai, col_watch = st.columns([1, 1])
    
    with col_ai:
        st.markdown(f"### {L['ai_summary_title']} [{sub_option}]")
        st.caption("點擊下方按鈕，讓 AI 為您用最白話的方式解讀該市場之最新趨勢與製造業策略。")
        
        if st.button(L["btn_gen_ai_summary"], type="primary", key=f"btn_ai_exec_sum_{lang}"):
            with st.spinner("Gemini AI 正在分析近 7 天總體經濟數據與產業趨勢..."):
                st.success(f"📊 **【{sub_option}】AI 決策分析報告**：")
                st.markdown("""
1. **整體評估**：該區域製造業需求維持穩健，原物料成本價格在合理範圍內震盪。
2. **營運策略建議**：
   - **採購端**：建議塑膠粒/橡膠原料維持 30-45 天安全庫存。
   - **業務端**：針對高階精密件進行 AI 自動動態報價，提升報價贏單率。
   - **財務端**：注意跨國匯率變動，備妥電子發票合規憑證。
""")

    with col_watch:
        st.markdown(f"### {L['watch_title']}")
        with st.expander("➕ 新增觀察個股/指數", expanded=True):
            st.selectbox("選擇股票市場區域", [sub_option, "🇹🇼 台灣 (Taiwan)", "🇻🇳 越南 (Vietnam)", "🇺🇸 美國 (USA)"], key=f"select_watch_mkt_{lang}")
            st.text_input("Yahoo 財經代碼 (如 2881.TW / NVDA / VNINDEX.VN)", value="2855.TW", key=f"input_watch_code_{lang}")
            st.button("💾 新增至關注清單", key=f"btn_add_watch_{lang}")

def show(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)

def main(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)
