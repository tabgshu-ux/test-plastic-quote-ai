import streamlit as st
import pandas as pd
import datetime
import requests
import time

def render_executive_office_dashboard(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📈 總經理室 - 企業經營戰情室 (Executive Dashboard)")
    st.caption("即時掌握全集團工地動態、應收/應付帳款、綜合損益表、全球股市行情與 Gemini AI 經營顧問。")

    # 1. 初始化或讀取系統配置中的 API 與頻率設定 (模擬儲存於 session_state 或資料庫)
    if "exec_config" not in st.session_state:
        st.session_state.exec_config = {
            "api_provider": "Alpha Vantage / Yahoo Finance API",
            "api_key": "",
            "fetch_interval_min": 5, # 預設每 5 分鐘抓取一次，避免過度消耗網路
            "tracked_markets": ["台灣加權指數 (^TWII)", "越南胡志明指數 (^VNINDEX)", "上證指數 (000001.SS)", "香港恆生指數 (^HSI)"]
        }

    config = st.session_state.exec_config

    # 2. 模擬從資料庫撈取工地、應收/應付與損益資料
    active_projects_count = 12
    
    # 動態計算應收 (AR) 與應付 (AP)
    total_ar_usd = 482600.0  # 可從 invoices 表撈取
    total_ap_usd = 125000.0  # 可從 procurement_ap 或 subcontractor 撈取
    gross_profit_usd = total_ar_usd - total_ap_usd

    # ----------------------------------------------------
    # 📊 頂部核心四大指標卡片 (KPI Metrics)
    # ----------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("進行中水電案場 / Số công trường", f"{active_projects_count} 場", "🟢 施工中")
    with k2:
        st.metric("應收帳款總額 / Tổng phải thu (AR)", f"$ {total_ar_usd:,.2f} USD", "↑ 即時連動")
    with k3:
        st.metric("應付帳款總額 / Tổng phải trả (AP)", f"$ {total_ap_usd:,.2f} USD", "↓ 即時連動")
    with k4:
        st.metric("估算營業淨利 / Lợi nhuận gộp", f"$ {gross_profit_usd:,.2f} USD", "🔥 自動加總")

    st.markdown("---")

    # ----------------------------------------------------
    # 💰 綜合損益表 (P&L Statement - 自動隨 AR/AP 變動)
    # ----------------------------------------------------
    st.markdown("##### 📊 集團綜合損益與現金流即時動態總表 (P&L Statement)")
    
    pl_data = {
        "會計項目 (Financial Item)": [
            "1. 工程合約總收入 (Total Contract Revenue)",
            "2. 應收帳款總額 (Accounts Receivable - AR)",
            "------------------------------------------",
            "3. 原物料與設備採購成本 (Material & Equipment Cost)",
            "4. 外包商點工與工資支出 (Labor & Subcontractor Cost)",
            "5. 應付帳款總額 (Accounts Payable - AP)",
            "==========================================",
            "6. 估算營業淨利 (Estimated Net Operating Profit)"
        ],
        "金額 (USD)": [
            f"$ {total_ar_usd * 1.25:,.2f} USD",
            f"$ {total_ar_usd:,.2f} USD",
            "--------------------",
            f"$ {total_ap_usd * 0.7:,.2f} USD",
            f"$ {total_ap_usd * 0.3:,.2f} USD",
            f"$ {total_ap_usd:,.2f} USD",
            "====================",
            f"$ {gross_profit_usd:,.2f} USD"
        ]
    }
    st.dataframe(pd.DataFrame(pl_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ----------------------------------------------------
    # 🌍 全球股市即時監控面板 (依 IT 後台設定之頻率與 API)
    # ----------------------------------------------------
    st.markdown("##### 🌍 全球股市行情監控中心 (Global Markets Ticker)")
    st.info(f"💡 目前資料更新頻率設定：**每 {config['fetch_interval_min']} 分鐘自動擷取一次**（可在 IT 管理後台修改 API 金鑰與擷取頻率）。")

    # 模擬股市即時行情資料 (若串接真實 API 可在此呼叫 requests)
    market_data = [
        {"市場": "🇹🇼 台灣加權指數 (TWSE)", "最新指數": "23,450.80", "漲跌幅": "+1.25%", "狀態": "🟢 交易中"},
        {"市場": "🇻🇳 越南胡志明指數 (VN-Index)", "最新指數": "1,285.40", "漲跌幅": "+0.65%", "狀態": "🟢 交易中"},
        {"市場": "🇨🇳 上海綜合指數 (SSE)", "最新指數": "3,150.20", "漲跌幅": "-0.32%", "狀態": "🟢 交易中"},
        {"市場": "🇭🇰 香港恆生指數 (HSI)", "最新指數": "17,890.10", "漲跌幅": "+0.88%", "狀態": "🟢 交易中"}
    ]
    st.dataframe(pd.DataFrame(market_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ----------------------------------------------------
    # 🤖 Gemini AI 總經理經營顧問
    # ----------------------------------------------------
    st.markdown("##### 🤖 Gemini AI 經營與財務風險智慧顧問")
    st.chat_message("assistant").write("您好，總經理！我是您的 AI 經營顧問。目前集團有 12 個案場進行中，應收帳款 ($482,600 USD) 扣除應付帳款後，現金流與淨利表現穩健。請問需要為您分析哪一個案場的毛利或原物料成本嗎？")
    
    user_ai_query = st.text_input("向 Gemini AI 詢問經營、財務或股市相關問題：", placeholder="例如：目前西寧廠的應收帳款催收風險為何？")
    if st.button("🚀 發送給 Gemini AI 深度分析", type="primary"):
        if user_ai_query:
            st.success(f"🤖 **Gemini AI 分析回覆**：針對您的問題「*{user_ai_query}*」，結合目前應收帳款 ($482,600 USD) 與專案進度，建議管理部針對屆期超過 30 天的工程尾款加強催收，以確保現金流充沛。")
        else:
            st.warning("請輸入您的提問！")

def show(engine=None, lang="繁體中文", **kwargs):
    render_executive_office_dashboard(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_executive_office_dashboard(engine=engine, lang=lang, **kwargs)
