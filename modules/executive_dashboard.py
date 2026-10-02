import streamlit as st
import pandas as pd

# 🌐 戰情看板三語系字典
EXEC_I18N = {
    "繁體中文": {
        "title": "📈 董事長/總經理 — 戰情看板",
        "caption": "即時監控全公司資產淨值、應收(AR)/應付(AP)現金流、原物料行情",
        "kpi_ar": "總應收帳款 (AR)",
        "kpi_ap": "總應付帳款 (AP)",
        "kpi_net": "預估淨現金流",
        "market_title": "📊 國際與越南本土原物料行情",
        "copper_vn": "🇻🇳 越南導電銅排 (VND/kg)",
        "copper_lme": "🇬🇧 LME 倫敦期銅 (USD/ton)",
        "steel_vn": "🇻🇳 Hòa Phát 鋼鐵 (VND/kg)"
    },
    "Tiếng Việt": {
        "title": "📈 Ban Giám Đốc — Báo Cáo Chiến Lược",
        "caption": "Theo dõi thời gian thực giá trị tài sản, dòng tiền AR/AP, giá nguyên vật liệu",
        "kpi_ar": "Tổng Phải Thu (AR)",
        "kpi_ap": "Tổng Phải Trả (AP)",
        "kpi_net": "Dòng Tiền Ròng Dự Kiến",
        "market_title": "📊 Giá Nguyên Vật Liệu Quốc Tế & Việt Nam",
        "copper_vn": "🇻🇳 Đồng Thanh Cái VN (VND/kg)",
        "copper_lme": "🇬🇧 Đồng LME London (USD/tấn)",
        "steel_vn": "🇻🇳 Thép Hòa Phát (VND/kg)"
    },
    "English": {
        "title": "📈 Executive Dashboard — Chairman & GM",
        "caption": "Real-time monitoring of corporate net worth, AR/AP cash flow, raw material markets",
        "kpi_ar": "Total AR",
        "kpi_ap": "Total AP",
        "kpi_net": "Estimated Net Cash Flow",
        "market_title": "📊 Raw Material & Commodity Markets",
        "copper_vn": "🇻🇳 VN Busbar Copper (VND/kg)",
        "copper_lme": "🇬🇧 LME Copper (USD/ton)",
        "steel_vn": "🇻🇳 Hòa Phát Steel (VND/kg)"
    }
}

def render(engine=None, t=None, lang="繁體中文", *args, **kwargs):
    """確保 render 函式名稱與傳參皆完美相容 app.py 的呼叫，防止 AttributeError"""
    curr_lang = kwargs.get("lang", lang)
    if curr_lang not in EXEC_I18N:
        curr_lang = "繁體中文"
    L = EXEC_I18N[curr_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    col1, col2, col3 = st.columns(3)
    col1.metric(L["kpi_ar"], "₫ 8,250,000,000", "+12.5%")
    col2.metric(L["kpi_ap"], "₫ 3,120,000,000", "-5.2%", delta_color="inverse")
    col3.metric(L["kpi_net"], "₫ 5,130,000,000", "+₫ 680,000,000")

    st.markdown("---")
    st.subheader(L["market_title"])
    m1, m2, m3 = st.columns(3)
    m1.metric(L["copper_vn"], "245,000 VND", "+2,500 VND")
    m2.metric(L["copper_lme"], "$ 9,850 USD", "+$ 120 USD")
    m3.metric(L["steel_vn"], "16,800 VND", "-300 VND")

def show(engine=None, t=None, lang="繁體中文", *args, **kwargs):
    render(engine, t, lang, *args, **kwargs)

def main(engine=None, t=None, lang="繁體中文", *args, **kwargs):
    render(engine, t, lang, *args, **kwargs)
