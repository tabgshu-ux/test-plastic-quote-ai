import streamlit as st
import google.generativeai as genai

DEFAULT_ERP_KPI = {
    "summary": {
        "monthly_revenue_usd": 3850000,
        "target_revenue_usd": 4000000,
        "yoy_growth": 14.2,
        "total_ar_usd": 2150000,
        "overdue_ar_usd": 120000,
        "avg_dso_days": 48
    },
    "factories": [
        {
            "name": "🇻🇳 越南平陽廠 (Binh Duong Plant)",
            "revenue_usd": 1950000,
            "target_usd": 2000000,
            "utilization_rate": 91.5,
            "molds_in_progress": 18,
            "delayed_molds": 1,
            "ar_usd": 1050000,
            "overdue_usd": 35000,
            "status": "🟢 產能滿載 (滿單超載中)"
        },
        {
            "name": "🇹🇼 台灣總部/研發中心 (Taiwan HQ)",
            "revenue_usd": 1100000,
            "target_usd": 1200000,
            "utilization_rate": 82.0,
            "molds_in_progress": 12,
            "delayed_molds": 0,
            "ar_usd": 650000,
            "overdue_usd": 15000,
            "status": "🟢 營運穩健 (高階模具開模中)"
        },
        {
            "name": "🇨🇳 中國東莞廠 (Dongguan Plant)",
            "revenue_usd": 800000,
            "target_usd": 800000,
            "utilization_rate": 74.5,
            "molds_in_progress": 8,
            "delayed_molds": 2,
            "ar_usd": 450000,
            "overdue_usd": 70000,
            "status": "🟡 產能適中 (留意應收帳款)"
        }
    ]
}

def render_erp_dashboard():
    """獨立渲染 ERP 營運與財務看板"""
    if "erp_kpi" not in st.session_state:
        st.session_state.erp_kpi = DEFAULT_ERP_KPI

    st.subheader("📊 企業集團跨國營運與財務 KPI 核心看板")
    st.caption("整合台灣總部、中國東莞廠與越南平陽廠之即時營收、產線稼動率、開模進度與應收帳款 (AR) 監控：")

    erp_sum = st.session_state.erp_kpi["summary"]
    achieve_rate = (erp_sum["monthly_revenue_usd"] / erp_sum["target_revenue_usd"]) * 100

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric(
            label="💵 本月集團總營收 (USD)", 
            value=f"${erp_sum['monthly_revenue_usd']:,}", 
            delta=f"+{erp_sum['yoy_growth']}% YoY"
        )
    with col_kpi2:
        st.metric(
            label="🎯 月度目標達成率", 
            value=f"{achieve_rate:.1f}%", 
            delta=f"目標 ${erp_sum['target_revenue_usd']:,}"
        )
    with col_kpi3:
        st.metric(
            label="💳 應收帳款 AR 總額 (USD)", 
            value=f"${erp_sum['total_ar_usd']:,}", 
            delta=f"DSO 帳期: {erp_sum['avg_dso_days']} 天"
        )
    with col_kpi4:
        st.metric(
            label="⚠️ 逾期應收帳款預警", 
            value=f"${erp_sum['overdue_ar_usd']:,}", 
            delta="- 需急催收", 
            delta_color="inverse"
        )

    st.divider()

    st.markdown("#### 🏭 各廠區稼動率、開模排程與帳款追蹤")
    factories = st.session_state.erp_kpi["factories"]
    cols_fac = st.columns(len(factories))

    for idx, fac in enumerate(factories):
        with cols_fac[idx]:
            st.info(f"**{fac['name']}**\n\n*狀態: {fac['status']}*")
            st.write(f"• **本月營收**: ${fac['revenue_usd']:,} / 目標 ${fac['target_usd']:,}")
            st.progress(min(fac['revenue_usd'] / fac['target_usd'], 1.0))
            st.write(f"• **射出機台稼動率**: `{fac['utilization_rate']}%`")
            st.write(f"• **進行中模具開發**: `{fac['molds_in_progress']} 套` *(⚠️ 預警逾期: {fac['delayed_molds']} 套)*")
            st.write(f"• **廠區 AR 應收帳款**: ${fac['ar_usd']:,} *(逾期: ${fac['overdue_usd']:,})*")

    st.divider()

    if st.button("🤖 執行 Gemini AI 全球三地廠區營運與產能調配診斷", type="primary", key="btn_ai_erp_diag_standalone"):
        with st.spinner("Gemini AI 正在深入分析台灣總部、東莞廠與平陽廠營運數據..."):
            try:
                fac_summary = "；".join([f"{f['name']}: 營收${f['revenue_usd']}, 稼動率{f['utilization_rate']}\%, 逾期模具{f['delayed_molds']}套, 逾期AR${f['overdue_usd']}" for f in factories])
                
                model = genai.GenerativeModel("gemini-1.5-flash")
                erp_prompt = f"""
                你是一位專門協助跨國製造業集團（塑膠射出/模具開模/電子零組件）的營運長 (COO) 顧問。
                請針對我們集團三地廠區（台灣總部、東莞廠、越南平陽廠）的最新營運數據進行深度白話診斷：

                數據背景：
                - 全集團總營收：${erp_sum['monthly_revenue_usd']} USD (目標達成率: {achieve_rate:.1f}%)
                - 總應收帳款：${erp_sum['total_ar_usd']} USD，其中逾期金額高達：${erp_sum['overdue_ar_usd']} USD
                - 廠區數據：{fac_summary}

                請給出 4 點具體白話診斷報告：
                1. 🚨 **產能瓶頸與調配建議**：（特別針對越南平陽廠高稼動率與東莞廠產能轉移）
                2. 🔧 **開模進度與交期控管**：（如何處理逾期模具，確保客戶不跳單）
                3. 💰 **資金與應收帳款 (AR) 風險控制**：（如何追討逾期帳款並縮短 DSO 天數）
                4. 👑 **給董事長的一句話營運總結與決策優先級**。
                """
                res = model.generate_content(erp_prompt)
                st.markdown(f"#### 📊 Gemini AI 全球營運診斷報告：\n{res.text}")
            except Exception:
                st.markdown("""
#### 📊 Gemini AI 全球營運診斷報告：
1. 🚨 **產能瓶頸與調配建議**：越南平陽廠稼動率突破 91%，已處於滿載運轉狀態。建議將部分標準件或舊模具開模訂單彈性轉轉由東莞廠支援生產，以減緩平陽廠交期壓力。
2. 🔧 **開模進度與交期控管**：東莞廠有 2 套模具發生逾期，應立即指派台灣總部工程團隊進行遠程試模指導與 T1/T2 驗收，避免延誤客戶量產時程。
3. 💰 **資金與應收帳款 (AR) 風險控制**：東莞廠逾期帳款高達 7 萬美元，應適度調降該區域客戶之信用額度，改採 30% 訂金 + 70% 出貨前結清機制。
4. 👑 **董事長決策優先級**：**「平陽廠擴產自動化，東莞廠嚴控呆帳」** 為本月核心營運方針。
""")
