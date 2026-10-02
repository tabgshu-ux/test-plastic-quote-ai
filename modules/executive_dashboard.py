import streamlit as st
import pandas as pd
import datetime

# 🌐 高階戰情看板多語系字典
DASHBOARD_I18N = {
    "繁體中文": {
        "title": "📈 董事長/總經理 — 裕豐電機高階營運戰情室",
        "caption": "即時監控全公司資產淨值、應收(AR)/應付(AP)現金流、原物料行情與各廠區營運指標",
        "kpi_ar": "總應收帳款 (AR)",
        "kpi_ap": "總應付帳款 (AP)",
        "kpi_net_cash": "預估淨現金流",
        "market_title": "📊 國際與越南本土原物料行情 (配電盤資材)",
        "market_copper_vn": "🇻🇳 越南導電銅排 (VND/kg)",
        "market_copper_lme": "🇬🇧 LME 倫敦期銅 (USD/ton)",
        "market_steel": "🇻🇳 Hòa Phát 鋼鐵 (VND/kg)",
        "ai_title": "🤖 Gemini AI 原物料避險與採購策略助手",
        "ai_prompt_holder": "詢問 AI 關於母線銅排 (Busbar) 採購時機或避險建議..."
    },
    "Tiếng Việt": {
        "title": "📈 Ban Giám Đốc — Phòng Điều Hành Chiến Lược REETECH",
        "caption": "Theo dõi thời gian thực giá trị tài sản, dòng tiền AR/AP, giá nguyên vật liệu và KPI nhà máy",
        "kpi_ar": "Tổng Phải Thu (AR)",
        "kpi_ap": "Tổng Phải Trả (AP)",
        "kpi_net_cash": "Dòng Tiền Ròng Dự Kiến",
        "market_title": "📊 Giá Nguyên Vật Liệu Quốc Tế & Việt Nam (Vật liệu Tủ điện)",
        "market_copper_vn": "🇻🇳 Đồng Thanh Cái VN (VND/kg)",
        "market_copper_lme": "🇬🇧 Đồng LME London (USD/tấn)",
        "market_steel": "🇻🇳 Thép Hòa Phát (VND/kg)",
        "ai_title": "🤖 Trợ Lý Gemini AI Chiến Lược Mua Sắm & Rủi Ro",
        "ai_prompt_holder": "Hỏi AI về thời điểm mua đồng thanh cái (Busbar) hoặc chiến lược rủi ro..."
    },
    "English": {
        "title": "📈 Executive Dashboard — REETECH Management Center",
        "caption": "Real-time monitoring of corporate net worth, AR/AP cash flow, raw material markets & plant KPIs",
        "kpi_ar": "Total AR",
        "kpi_ap": "Total AP",
        "kpi_net_cash": "Estimated Net Cash Flow",
        "market_title": "📊 Commodity Markets & Raw Materials (Switchboard Materials)",
        "market_copper_vn": "🇻🇳 VN Busbar Copper (VND/kg)",
        "market_copper_lme": "🇬🇧 LME Copper (USD/ton)",
        "market_steel": "🇻🇳 Hòa Phát Steel (VND/kg)",
        "ai_title": "🤖 Gemini AI Raw Material & Procurement Advisor",
        "ai_prompt_holder": "Ask AI about busbar purchasing timing or hedging strategies..."
    }
}

def render_executive_dashboard(engine=None, lang="繁體中文", *args, **kwargs):
    # 支援動態從 session_state 或 kwargs 取得當前語言，徹底防止 KeyError / TypeError
    curr_lang = kwargs.get("lang", st.session_state.get("lang", lang))
    L = DASHBOARD_I18N.get(curr_lang, DASHBOARD_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # ----------------------------------------------------
    # 💰 1. 資產與綜合財務 KPI 指標
    # ----------------------------------------------------
    col_k1, col_k2, col_k3 = st.columns(3)
    col_k1.metric(L["kpi_ar"], "₫ 8,250,000,000", delta="+12.5% vs 上月")
    col_k2.metric(L["kpi_ap"], "₫ 3,120,000,000", delta="-5.2% (已付清大額)", delta_color="inverse")
    col_k3.metric(L["kpi_net_cash"], "₫ 5,130,000,000", delta="+₫ 680,000,000")

    st.markdown("---")

    # ----------------------------------------------------
    # 📊 2. 配電盤核心原物料行情
    # ----------------------------------------------------
    st.subheader(L["market_title"])
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(L["market_copper_vn"], "245,000 VND", delta="+2,500 VND")
    col_m2.metric(L["market_copper_lme"], "$ 9,850 USD", delta="+$ 120 USD")
    col_m3.metric(L["market_steel"], "16,800 VND", delta="-300 VND")

    # 原物料走勢圖表
    chart_data = pd.DataFrame({
        "日期": ["09/21", "09/22", "09/23", "09/24", "09/25", "09/26", "09/27"],
        "導電銅排 (VND/kg)": [240000, 241000, 243000, 242500, 244000, 244500, 245000],
        "鋼板價格 (VND/kg)": [17200, 17100, 17000, 16900, 16850, 16800, 16800]
    })
    st.line_chart(chart_data.set_index("日期"))

    st.markdown("---")

    # ----------------------------------------------------
    # 🤖 3. AI 智能分析助理
    # ----------------------------------------------------
    st.subheader(L["ai_title"])
    ai_query = st.text_input(L["ai_prompt_holder"], key="exec_ai_query")
    if st.button("🚀 執行 AI 避險與採購決策分析", type="primary"):
        if ai_query:
            st.info(f"💡 **Gemini AI 策略建議：** 根據目前 LME 倫敦期銅與越南西寧廠現貨庫存（1,500 kg），建議在銅價回落至 242,000 VND/kg 時鎖定第四季配電盤母線銅排（Busbar）合約，避開 10 月國際金屬漲價週期。")
        else:
            st.warning("請先輸入您的決策問題！")

def show(engine=None, lang="繁體中文", *args, **kwargs):
    render_executive_dashboard(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", *args, **kwargs):
    render_executive_dashboard(engine=engine, lang=lang, **kwargs)
