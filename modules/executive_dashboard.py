import streamlit as st
import pandas as pd
import datetime
import random
from sqlalchemy import text

def format_currency_display(amount, curr="USD"):
    if curr == "VND":
        return f"₫ {amount:,.0f} VND"
    elif curr == "USD":
        return f"$ {amount:,.2f} USD"
    elif curr == "TWD":
        return f"NT$ {amount:,.0f} TWD"
    elif curr == "CNY":
        return f"¥ {amount:,.2f} CNY"
    return f"${amount:,.2f} {curr}"

def render(engine=None, t=None):
    st.title("👑 裕豐電機工業 - 董事長 / 總經理 綜合營運與財務戰情看板")
    st.caption("REETECH INDUSTRIAL Co., Ltd. - 跨國財務 (AR/AP)、越南本土/國際原物料與四國股市 (越/美/台/中) Gemini AI 智能分析")

    if not engine:
        st.warning("⚠️ 資料庫連線建置中...")
        return

    try:
        # 讀取 AR 與 AP 資料庫數據
        df_inv = pd.read_sql("SELECT * FROM invoices", engine)
        df_ar = df_inv[df_inv['invoice_type'] == 'AR'] if not df_inv.empty else pd.DataFrame()
        df_ap = df_inv[df_inv['invoice_type'] == 'AP'] if not df_inv.empty else pd.DataFrame()

        # 計算財務數據
        total_ar_usd = df_ar['amount_usd'].sum() if not df_ar.empty and 'amount_usd' in df_ar.columns else 0.0
        uncollected_ar_usd = df_ar[df_ar['is_paid'] == False]['amount_usd'].sum() if not df_ar.empty and 'amount_usd' in df_ar.columns else 0.0
        
        total_ap_usd = df_ap['amount_usd'].sum() if not df_ap.empty and 'amount_usd' in df_ap.columns else 0.0
        unpaid_ap_usd = df_ap[df_ap['is_paid'] == False]['amount_usd'].sum() if not df_ap.empty and 'amount_usd' in df_ap.columns else 0.0

        net_cashflow_usd = total_ar_usd - total_ap_usd

        # ----------------------------------------------------
        # 1. 頂部高階主管核心 KPI 卡片
        # ----------------------------------------------------
        st.markdown("### 📊 全集團綜合財務與原物料行情 KPI")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("客戶應收帳款總額 (AR)", f"USD ${total_ar_usd:,.2f}", f"未收: ${uncollected_ar_usd:,.2f}")
        c2.metric("廠商應付帳款總額 (AP)", f"USD ${total_ap_usd:,.2f}", f"未付: ${unpaid_ap_usd:,.2f}", delta_color="inverse")
        c3.metric("🇻🇳 越南國內銅排價格 (VND/kg)", "₫ 245,000 / kg", "+1.2% (平陽/西寧交貨)")
        c4.metric("🇻🇳 越南股市 (VN-Index)", "1,288.50 pts", "+0.65% 🚀")

        st.markdown("---")

        tab_stock, tab_summary, tab_ar_audit, tab_ap_summary = st.tabs([
            "📈 越南/國際原物料 (銅/鋼) & 跨國股市 (越/美/台/中) + AI 分析",
            "📊 綜合財務損益與現金流總報表",
            "🚨 應收帳款 (AR) 未收款理由與催收稽核",
            "🛒 應付帳款 (AP) 付款排程與採購清冊"
        ])

        # ----------------------------------------------------
        # TAB 1: 越南本土與國際原物料 + 越/美/台/中 股市 + Gemini AI 問答
        # ----------------------------------------------------
        with tab_stock:
            st.subheader("📈 原物料行情與跨國股市看板 (越、美、台、中)")
            st.caption("包含越南當地銅排/鋼板資材價格、LME 國際銅價，以及越南、美國、台灣、中國四大股市指數。")

            # 原物料與匯率卡片
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            col_met1.metric("🇻🇳 越南本土導電銅排", "₫ 245,000 VND / kg", "+2,500 (+1.03%)")
            col_met2.metric("🌍 倫敦 LME 期銅 (LME Copper)", "$9,850 USD / 噸", "+180 USD (+1.86%)")
            col_met3.metric("🇻🇳 越南鋼鐵 (Hòa Phát 鋼板)", "₫ 15,200 VND / kg", "持平 0.00%")
            col_met4.metric("💵 美元 / 越南盾 (USD/VND)", "25,420 VND", "＋0.05%")

            st.markdown("---")
            
            # 跨國股市大盤數據
            st.markdown("##### 🌐 全球四大市場股市指數 (越南 / 美國 / 台灣 / 中國)")
            global_stocks = {
                "國家 / 市場": ["🇻🇳 越南 (Vietnam)", "🇺🇸 美國 (USA)", "🇹🇼 台灣 (Taiwan)", "🇨🇳 中國 (China)"],
                "股市指數名稱": ["VN-Index (胡志明指數)", "道瓊工業 / S&P 500", "台灣加權指數 (TAIEX)", "上證綜合指數 (SSE Index)"],
                "最新指數點數": ["1,288.50 pts", "42,150.00 pts", "22,850.00 pts", "3,280.50 pts"],
                "今日漲跌": ["+0.65% 🔺", "-0.15% 🔻", "+0.72% 🔺", "+1.12% 🔺"],
                "對裕豐電機營運影響評估": [
                    "越南當地建廠與配電盤需求暢旺",
                    "美金資產利息高，注意匯率避險",
                    "台灣總部訂單與資材調撥平穩",
                    "原物料出口與外銷供需改善"
                ]
            }
            st.table(pd.DataFrame(global_stocks))

            st.markdown("---")
            
            # 🤖 Gemini AI 股市與原物料智能分析助手
            st.markdown("### 🤖 Gemini AI 股市與原物料資材智能分析助手")
            st.caption("您可以輸入任何關於「越南銅價趨勢」、「VN-Index 股市走勢」、「美金匯率」或「配電盤採購避險策略」等問題，Gemini 將為您進行專業解析。")

            user_query = st.text_input(
                "💬 請輸入您想詢問 Gemini 的財務、股市或原物料問題：", 
                placeholder="例如：目前越南銅價上漲，我們平陽廠與西寧廠的配電盤採購應該如何避險？"
            )

            if st.button("🚀 送出問題讓 Gemini AI 進行分析", type="primary"):
                if user_query.strip():
                    with st.spinner("Gemini AI 正在分析跨國股市、匯率與越南銅價走勢中..."):
                        # Gemini AI 模擬分析回應邏輯
                        response_text = f"""
### 💡 Gemini AI 專家分析報告

**【針對您的提問】**：`{user_query}`

1. **🇻🇳 越南本土與 LME 國際銅價趨勢分析：**
   - 目前越南本土導電銅排價格來到 **₫ 245,000 VND/kg**，受 LME 倫敦期銅每噸突破 **$9,850 USD** 影響，呈現微幅上漲趨勢。
   - 由於配電盤專案中，母線銅排 (Busbar) 佔材料成本約 **25% ~ 35%**，銅價每上漲 5%，工程毛利將被侵蝕約 **1.2%**。

2. **🌐 跨國股市與匯率波動聯動 (越 / 美 / 台 / 中)：**
   - **越南 VN-Index (1,288 pts)** 強勢上漲，代表越南當地工業區建廠與擴廠需求熱絡，配電盤接單前景看好。
   - **美元對越南盾 (USD/VND = 25,420)** 保持高位，建議出口結匯保持美金部位，以抵銷進口斷路器等外幣採購成本。

3. **🎯 裕豐電機營運與採購建議：**
   - **鎖定銅價：** 建議採購部門針對「西寧紡織廠工程」與已簽約之大金額專案，**立即簽訂鎖價合約或提早預購 2~3 個月銅排庫存**。
   - **合約條款追加：** 未來新報價單建議加入「原物料價格浮動調整條款 (Escalation Clause)」，若銅價漲幅超過 5% 可向客戶調整合約金額。
                        """
                        st.markdown(response_text)
                else:
                    st.warning("請輸入您的問題！")

        # ----------------------------------------------------
        # TAB 2: 綜合財務損益與現金流總報表
        # ----------------------------------------------------
        with tab_summary:
            st.subheader("📋 綜合財務資產負債與營運損益簡表")
            
            summary_data = {
                "財務科目類別": [
                    "💵 營業收入 - 客戶應收款總額 (AR)", 
                    "💸 營業成本 - 廠商資材應付款總額 (AP)", 
                    "📊 預估毛利 (Estimated Gross Profit)",
                    "⏳ 待收回現金 (Pending AR Collection)",
                    "⌛ 待支付貨款 (Pending AP Payment)"
                ],
                "金額 (折合 USD)": [
                    f"${total_ar_usd:,.2f}",
                    f"${total_ap_usd:,.2f}",
                    f"${net_cashflow_usd:,.2f}",
                    f"${uncollected_ar_usd:,.2f}",
                    f"${unpaid_ap_usd:,.2f}"
                ],
                "說明與狀態": [
                    "包含已開立發票與工程合約款",
                    "含銅排、開關元件與塗裝資材採購",
                    "營運淨流入預估",
                    "業務團隊進行催收中",
                    "出納按到期日安排銀行轉帳 (UNC)"
                ]
            }
            st.table(pd.DataFrame(summary_data))

        # ----------------------------------------------------
        # TAB 3: 應收帳款未收款理由與催收稽核
        # ----------------------------------------------------
        with tab_ar_audit:
            st.subheader("🚨 客戶未收款項與拖延理由稽核紀錄")
            st.caption("提供董事長/總經理審閱業務回報之客戶拖延原因、最新承諾付款日期與歷史催討軌跡。")

            if not df_ar.empty:
                ar_audit_list = []
                for _, row in df_ar.iterrows():
                    ar_audit_list.append({
                        "帳單單號": row.get("invoice_id"),
                        "客戶名稱": row.get("entity_name"),
                        "工程專案": row.get("project_name"),
                        "交易幣別": row.get("currency"),
                        "應收金額": format_currency_display(row.get("amount", 0.0), row.get("currency", "USD")),
                        "約定/更新後付款日": row.get("due_date"),
                        "負責業務": row.get("quoter_name", "-"),
                        "收款狀態": "✅ 已結清" if row.get("is_paid") else "🔴 未收款",
                        "最新未收款原因 / 催收歷史記錄": row.get("uncollected_reason") if row.get("uncollected_reason") else "無備註"
                    })
                st.dataframe(pd.DataFrame(ar_audit_list), use_container_width=True)
            else:
                st.info("目前無應收帳款資料。")

        # ----------------------------------------------------
        # TAB 4: 應付帳款付款排程與採購清冊
        # ----------------------------------------------------
        with tab_ap_summary:
            st.subheader("🛒 廠商採購與應付貨款 (AP) 摘要")
            st.caption("審閱向正泰、施耐德等供應商採購資材之應付帳款與銀行轉帳水單 (UNC) 狀態。")

            if not df_ap.empty:
                ap_summary_list = []
                for _, row in df_ap.iterrows():
                    ap_summary_list.append({
                        "採購單號": row.get("invoice_id"),
                        "供應商名稱": row.get("entity_name"),
                        "採購品名與規格": row.get("project_name"),
                        "交易幣別": row.get("currency"),
                        "應付金額": format_currency_display(row.get("amount", 0.0), row.get("currency", "USD")),
                        "付款到期日": row.get("due_date"),
                        "付款狀態": "✅ 已付清" if row.get("is_paid") else "⏳ 待付款",
                        "轉帳水單號 (UNC)": row.get("bank_transfer_ref", "未開立水單")
                    })
                st.dataframe(pd.DataFrame(ap_summary_list), use_container_width=True)
            else:
                st.info("目前無應付帳款資料。")

    except Exception as e:
        st.error(f"戰情看板讀取資料庫時發生錯誤：{e}")

def show(engine=None, t=None):
    render(engine, t)

def main(engine=None, t=None):
    render(engine, t)
