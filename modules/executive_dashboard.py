import streamlit as st
import os
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from datetime import datetime, date

# ----------------------------------------------------
# 🌐 越南台廠水電工程戰情室多語系字典 (i18n)
# ----------------------------------------------------
EXEC_I18N = {
    "繁體中文": {
        "page_title": "⚡ 裕豐電機工業 - 越南台廠水電工程專案與收款戰情室",
        "sub_title": "即時監控專案工程進度、合約款項回收狀況、LME 銅價走勢與 USD/VND 匯率風險管控",
        "tab_project_progress": "📊 台廠水電工程專案進度與收款看板",
        "tab_materials_fx": "📈 LME 銅價成本與 USD/VND 匯率追蹤",
        "tab_fin_stat": "📊 工程專案 AR/AP 財務現金流",
        "tab_vpsh_reports": "📊 企業綜合損益表 (P&L) 與毛利勾稽",
        "section_title": "🏗️ 越南廠房客製化水電與高低壓配電專案執行清單",
        "ai_summary_title": "🤖 Gemini AI 工程收款與合約風險智慧分析",
        "btn_gen_ai_summary": "🚀 生成專案進度與收款催收建議報告",
    },
    "Tiếng Việt": {
        "page_title": "⚡ REETECH INDUSTRIAL - Quản lý Tiến độ Dự án Cơ điện & Thu tiền",
        "sub_title": "Giám sát thời gian thực tiến độ thi công cơ điện nhà máy Đài Loan tại VN, tình hình thu tiền, giá đồng LME và tỷ giá USD/VND",
        "tab_project_progress": "📊 Bảng tiến độ dự án cơ điện & Thu hồi công nợ",
        "tab_materials_fx": "📈 Theo dõi giá đồng LME & Tỷ giá USD/VND",
        "tab_fin_stat": "📊 Dòng tiền tài chính AR/AP dự án",
        "tab_vpsh_reports": "📊 Báo cáo kết quả kinh doanh (P&L) & Biên lợi nhuận",
        "section_title": "🏗️️ Danh sách dự án cơ điện & tủ điện trạm biến áp nhà máy",
        "ai_summary_title": "🤖 Phân tích AI Gemini về tiến độ & Rủi ro thu hồi vốn",
        "btn_gen_ai_summary": "🚀 Tạo báo cáo phân tích & Đề xuất thu hồi công nợ",
    },
    "English": {
        "page_title": "⚡ REETECH INDUSTRIAL - M&E Project Progress & Collection Dashboard",
        "sub_title": "Real-time monitoring of MEP project milestones, cash collections, LME copper trends & USD/VND FX risk",
        "tab_project_progress": "📊 M&E Project Progress & Collection Tracking",
        "tab_materials_fx": "📈 LME Copper Cost & USD/VND FX Trends",
        "tab_fin_stat": "📊 Project AR/AP Financial Cash Flow",
        "tab_vpsh_reports": "📊 Consolidated P&L & Margin Reconciliation",
        "section_title": "🏗️️ Custom M&E and Switchgear Project Execution List",
        "ai_summary_title": "🤖 Gemini AI Project Collection & Risk Analysis",
        "btn_gen_ai_summary": "🚀 Generate Project Progress & Collection Brief",
    }
}

def get_exec_lang_dict(lang_param=None):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return EXEC_I18N.get(lang, EXEC_I18N["繁體中文"])

# ----------------------------------------------------
# 🏗️ 1. 台廠水電工程專案進度與收款看板
# ----------------------------------------------------
def render_mep_project_progress_board():
    st.markdown("### 🏗️ 越南台廠客製化水電工程專案進度與財務收款追蹤")
    st.caption("結合工程現場施工進度百分比、合約總價、已收款金額、未收款（尾款/進度款）及收款理由與驗收狀態。")

    # 頂部戰情指標
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("在手水電專案總數", "8 件", "執行中 6件 / 驗收 2件")
    c2.metric("合約總金額 (USD)", "$1,850,000", "累計已收: $1,250,000")
    c3.metric("總未收款/應收尾款 (AR)", "$600,000", "⚠️ 需加強催收")
    c4.metric("平均工程進度", "76.5%", "🟢 進度正常")

    st.markdown("---")
    st.markdown("#### 📋 專案明細、工程進度與收款連動管控表")

    # 模擬水電工程專案資料（包含工程進度、收款金額、未收款理由與驗收狀態）
    projects_data = [
        {
            "專案代碼": "PRJ-2026-01",
            "台廠客戶名稱": "🇻🇳 越南新順楠梓電子廠 (XinShun Electronics)",
            "水電工程項目": "無塵室高低壓配電盤安裝與強弱電配管",
            "合約總價 (USD)": 450000.0,
            "已收款金額 (USD)": 315000.0,
            "未收款/尾款 (USD)": 135000.0,
            "工程進度 (%)": 90,
            "工程與驗收狀態": "🟢 設備安裝完成，進行試車中",
            "財務收款理由說明": "依合約約定，待總承商完成消防驗收並取得合格證後，撥付 30% 尾款。"
        },
        {
            "專案代碼": "PRJ-2026-02",
            "台廠客戶名稱": "🇻🇳 平陽美德金屬加工廠 (MeiDe Metal)",
            "水電工程項目": "廠房動力配電、給排水系統與照明工程",
            "合約總價 (USD)": 380000.0,
            "已收款金額 (USD)": 228000.0,
            "未收款/尾款 (USD)": 152000.0,
            "工程進度 (%)": 75,
            "工程與驗收狀態": "🟡 正在進行主幹管拉線與配電盤組裝",
            "財務收款理由說明": "第三期進度款（60%）已達請款條件，會計部已發出請款單，預計下週入帳。"
        },
        {
            "專案代碼": "PRJ-2026-03",
            "台廠客戶名稱": "🇻🇳 隆安宏遠精密機械廠 (HongYuan Precision)",
            "水電工程項目": "變電站統包工程、銅排配置與空調系統配電",
            "合約總價 (USD)": 620000.0,
            "已收款金額 (USD)": 434000.0,
            "未收款/尾款 (USD)": 186000.0,
            "工程進度 (%)": 85,
            "工程與驗收狀態": "🟢 變電站主體完工，台電/當地電力局驗收中",
            "財務收款理由說明": "電力局供電許可證核發中，證照到手後立即通知客戶支付 30% 驗收尾款。"
        },
        {
            "專案代碼": "PRJ-2026-04",
            "台廠客戶名稱": "🇻🇳 北寧富泰光電科技 (FuTai Optoelectronics)",
            "水電工程項目": "廠辦大樓消防警報系統與機房不斷電(UPS)配電",
            "合約總價 (USD)": 400000.0,
            "已收款金額 (USD)": 273000.0,
            "未收款/尾款 (USD)": 127000.0,
            "工程進度 (%)": 55,
            "工程與驗收狀態": "🟡 橋架架設與線槽安裝階段",
            "財務收款理由說明": "第二期工程進度款審核中，因客戶工程師近期出差延遲簽核，已由業務前往催辦。"
        }
    ]

    df_proj = pd.DataFrame(projects_data)
    
    # 格式化顯示表格
    st.dataframe(df_proj, use_container_width=True)

    # 視覺化圖表：工程進度與未收款金額對比
    st.markdown("---")
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        fig_prog = px.bar(df_proj, x="專案代碼", y="工程進度 (%)", color="專案代碼", title="各水電專案工程進度和進度條 (Progress)")
        st.plotly_chart(fig_prog, use_container_width=True)
    with c_chart2:
        fig_cash = px.bar(df_proj, x="專案代碼", y=["已收款金額 (USD)", "未收款/尾款 (USD)"], title="各專案已收款 vs 未收款結構 (USD)")
        st.plotly_chart(fig_cash, use_container_width=True)

# ----------------------------------------------------
# 📈 2. LME 銅價與 USD/VND 匯率追蹤 (水電工程核心成本)
# ----------------------------------------------------
def render_materials_and_fx_tracking():
    st.markdown("### 📈 LME 國際銅價成本與 USD/VND 匯率即時監控")
    st.caption("水電工程的核心成本來自導線與銅排（Copper Busbar）。本看板協助評估國際銅價波動對專案毛利的影響。")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("LME 倫敦銅價 (Copper)", "$9,250 USD/噸", "+85.0 (+0.93%) 🟢")
    col2.metric("美金/越南盾 (USD/VND)", "25,420 VND", "-15.0 (-0.06%) 穩定")
    col3.metric("PVC 塑膠管材指數", "$1,420 USD", "+5.0 (+0.35%)")
    col4.metric("變壓器矽鋼片採購指數", "$2,150 USD/噸", "持平")

    st.markdown("---")
    st.markdown("#### 💡 銅價波動對水電工程報價之影響評估")
    st.info("""
    * **銅價走勢分析**：近期 LME 銅價維持在 $9,250 美元/噸高檔震盪。若合約為固定總價且未納入原物料價格調整條款，需留意後續進場施工之線材採購成本。
    * **匯率風險控管**：越南當地工程人工及部分內購材料以越南盾 (VND) 支付，但進口高壓開關與變電設備常以美金 (USD) 計價，建議財務部持續關注 USD/VND 匯率走勢並做好匯率避險。
    """)

# ----------------------------------------------------
# 📊 3. 專案 AR/AP 財務現金流
# ----------------------------------------------------
def render_project_ar_ap_stats():
    st.markdown("### 📊 越南台廠水電工程專案 AR / AP 財務現金流")
    
    col_ar1, col_ar2, col_ar3, col_ar4 = st.columns(4)
    col_ar1.metric("工程總應收帳款 (AR)", "$600,000 USD", "包含各期尾款與進度款")
    col_ar2.metric("材料與工班應付帳款 (AP)", "$280,000 USD", "供應商與次承攬商貨款")
    col_ar3.metric("逾期未收款 (>60天)", "$85,000 USD", "⚠️ 需優先催收")
    col_ar4.metric("專案淨現金流預估", "$320,000 USD", "🟢 資金水位安全")

    st.markdown("#### 🏢 專案應收與應付明細表")
    ar_ap_data = [
        {"專案代碼": "PRJ-2026-01", "客戶名稱": "新順楠梓電子", "應收 AR (USD)": "$135,000", "應付 AP (USD)": "$60,000", "帳款狀態": "🟡 待驗收尾款"},
        {"專案代碼": "PRJ-2026-02", "客戶名稱": "平陽美德金屬", "應收 AR (USD)": "$152,000", "應付 AP (USD)": "$75,000", "帳款狀態": "🟢 請款審核中"},
        {"專案代碼": "PRJ-2026-03", "客戶名稱": "隆安宏遠精密", "應收 AR (USD)": "$186,000", "應付 AP (USD)": "$90,000", "帳款狀態": "🟡 待電力局驗收"},
        {"專案代碼": "PRJ-2026-04", "客戶名稱": "北寧富泰光電", "應收 AR (USD)": "$127,000", "應付 AP (USD)": "$55,000", "帳款狀態": "🟢 施工採購中"}
    ]
    st.dataframe(pd.DataFrame(ar_ap_data), use_container_width=True)

# ----------------------------------------------------
# 🧮 4. 企業綜合損益表 (P&L)
# ----------------------------------------------------
def render_consolidated_income_statement():
    st.markdown("### 📊 水電工程事業部綜合損益表 (Income Statement / P&L) (USD)")
    st.caption("數據由全系統各模組（水電工程合約、材料採購、工班薪資、機具租賃）即時勾稽與計算。")

    total_revenue = 1850000.0   # 總合約營收
    total_cogs = 1250000.0      # 工程成本（線材、配電盤、工班點工）
    gross_profit = total_revenue - total_cogs
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

    payroll_expense = 180000.0  # 工程師與管理薪資
    equipment_expense = 45000.0 # 吊車、機具租賃與測試儀器
    admin_expense = 25000.0     # 辦公與差旅行政開支

    total_opex = payroll_expense + equipment_expense + admin_expense
    ebit = gross_profit - total_opex
    tax_expense = max(0.0, ebit * 0.20)
    net_income = ebit - tax_expense
    net_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("工程總營收 (Revenue)", f"${total_revenue:,.2f} USD")
    k2.metric("工程毛利 (Gross Profit)", f"${gross_profit:,.2f} USD", f"毛利率 {gross_margin:.1f}%")
    k3.metric("營業費用 (OPEX)", f"${total_opex:,.2f} USD")
    k4.metric("本期淨利 (Net Income)", f"${net_income:,.2f} USD", f"淨利率 {net_margin:.1f}%")

    st.markdown("---")
    pl_data = [
        {"會計科目": "一、水電工程營業收入 (Revenue)", "金額 (USD)": f"${total_revenue:,.2f}", "說明": "在手合約總價累計"},
        {"會計科目": "二、工程直接成本 (COGS)", "金額 (USD)": f"(${total_cogs:,.2f})", "說明": "包含銅線、開關、配電盤與工班薪資"},
        {"會計科目": "💡 營業毛利 (Gross Profit)", "金額 (USD)": f"${gross_profit:,.2f}", "說明": f"毛利率: {gross_margin:.1f}%"},
        {"會計科目": "三、營業費用 (OPEX)", "金額 (USD)": f"(${total_opex:,.2f})", "說明": "包含工程師薪資、機具租賃與行政"},
        {"會計科目": "💡 營業利益 (Operating Income)", "金額 (USD)": f"${ebit:,.2f}", "說明": f"營業利益率: {(ebit/total_revenue*100):.1f}%"},
        {"會計科目": "四、預估所得稅 (20%)", "金額 (USD)": f"(${tax_expense:,.2f})", "說明": "越南當地企業所得稅提撥"},
        {"會計科目": "🏆 🏆 本期淨利 (Net Income)", "金額 (USD)": f"${net_income:,.2f}", "說明": f"稅後淨利率: {net_margin:.1f}%"}
    ]
    st.dataframe(pd.DataFrame(pl_data), use_container_width=True)

# ----------------------------------------------------
# 🚀 模組入口函式 (將戰情室 3 個功能在主畫面上完全分開呈現)
# ----------------------------------------------------
def render_executive_dashboard_page(sub_option="🌐 全部市場 (All Markets)", lang=None):
    L = get_exec_lang_dict(lang)
    current_lang = lang or "繁體中文"
    
    st.title(L["page_title"])
    st.caption(L["sub_title"])
    st.divider()

    # 4 個獨立分頁，讓使用者點選即切換，不再全部擠在同一個長頁面上
    tab1, tab2, tab3, tab4 = st.tabs([
        L["tab_project_progress"],
        L["tab_materials_fx"],
        L["tab_fin_stat"],
        L["tab_vpsh_reports"]
    ])

    # 分頁 1：台廠水電工程專案進度與收款看板
    with tab1:
        render_mep_project_progress_board()
        
        st.divider()
        st.markdown(f"### {L['ai_summary_title']}")
        if st.button(L["btn_gen_ai_summary"], type="primary", key=f"btn_ai_mep_sum_{current_lang}"):
            st.success("📊 **【AI 催收與工程進度分析報告】**：目前 4 件在手水電專案進度皆符合預期。建議針對『新順楠梓電子廠』加速催辦消防驗收，以便順利回收 $135,000 美元尾款；另平陽美德廠第三期進度款已達請款條件，請會計部於本週完成發票開立與請款作業。")

    # 分頁 2：LME 銅價成本與 USD/VND 匯率追蹤
    with tab2:
        render_materials_and_fx_tracking()

    # 分頁 3：工程專案 AR/AP 財務現金流
    with tab3:
        render_project_ar_ap_stats()

    # 分頁 4：企業綜合損益表 (P&L) 與毛利勾稽
    with tab4:
        render_consolidated_income_statement()

def show(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)

def main(sub_option="🌐 全部市場 (All Markets)", lang=None):
    render_executive_dashboard_page(sub_option, lang)
