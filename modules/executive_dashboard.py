import streamlit as st
import pandas as pd
import datetime
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
    st.caption("REETECH INDUSTRIAL Co., Ltd. - 跨國財務 (AR/AP)、未收款理由稽核與工程利潤即時綜合報表")

    if not engine:
        st.warning("⚠️ 資料庫連線建置中...")
        return

    try:
        # 讀取 AR 與 AP 全料庫數據
        df_inv = pd.read_sql("SELECT * FROM invoices", engine)
        df_ar = df_inv[df_inv['invoice_type'] == 'AR'] if not df_inv.empty else pd.DataFrame()
        df_ap = df_inv[df_inv['invoice_type'] == 'AP'] if not df_inv.empty else pd.DataFrame()

        # 計算綜合數據
        total_ar_usd = df_ar['amount_usd'].sum() if not df_ar.empty and 'amount_usd' in df_ar.columns else 0.0
        uncollected_ar_usd = df_ar[df_ar['is_paid'] == False]['amount_usd'].sum() if not df_ar.empty and 'amount_usd' in df_ar.columns else 0.0
        
        total_ap_usd = df_ap['amount_usd'].sum() if not df_ap.empty and 'amount_usd' in df_ap.columns else 0.0
        unpaid_ap_usd = df_ap[df_ap['is_paid'] == False]['amount_usd'].sum() if not df_ap.empty and 'amount_usd' in df_ap.columns else 0.0

        net_cashflow_usd = total_ar_usd - total_ap_usd

        # ----------------------------------------------------
        # 1. 高階主管核心 KPI 卡片 (Executive Metrics)
        # ----------------------------------------------------
        st.markdown("### 📊 全集團綜合財務 KPI 總覽")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("客戶應收帳款總額 (AR)", f"USD ${total_ar_usd:,.2f}", f"未收: ${uncollected_ar_usd:,.2f}", delta_color="normal")
        c2.metric("廠商應付帳款總額 (AP)", f"USD ${total_ap_usd:,.2f}", f"未付: ${unpaid_ap_usd:,.2f}", delta_color="inverse")
        c3.metric("淨營運現金流預估 (Net Cash)", f"USD ${net_cashflow_usd:,.2f}", "結餘良好" if net_cashflow_usd >= 0 else "留意資金流")
        c4.metric("營運中的配電盤工程數", f"{len(df_ar)} 筆項目")

        st.markdown("---")

        tab_summary, tab_ar_audit, tab_ap_summary = st.tabs([
            "📈 綜合財務損益與現金流總報表",
            "🚨 應收帳款 (AR) 未收款理由與催收稽核",
            "🛒 應付帳款 (AP) 付款排程與採購清冊"
        ])

        # ----------------------------------------------------
        # TAB 1: 綜合財務損益與現金流總報表
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
        # TAB 2: 應收帳款未收款理由與催收稽核 (老闆重點關注區)
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
        # TAB 3: 應付帳款付款排程與採購清冊
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
