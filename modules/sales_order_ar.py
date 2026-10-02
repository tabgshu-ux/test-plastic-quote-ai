import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def format_currency_display(amount, curr):
    if curr == "VND":
        return f"₫ {amount:,.0f} VND"
    elif curr == "USD":
        return f"$ {amount:,.2f} USD"
    elif curr == "TWD":
        return f"NT$ {amount:,.0f} TWD"
    elif curr == "CNY":
        return f"¥ {amount:,.2f} CNY"
    return f"{amount:,.2f} {curr}"

def render_sales_order_ar_page(engine=None, **kwargs):
    st.title("📋 管理部 - 客戶應收帳款 (AR) & 報價單與合約管理")
    st.caption("完整記錄客戶應收帳款、預計與實際到期日期時間、未能收款原因以及工程報價單內容。")

    tab_list, tab_quote, tab_add = st.tabs([
        "📑 客戶應收款項明細表",
        "📄 配電盤工程報價單與合約內容",
        "➕ 登記新應收帳款/合約"
    ])

    with tab_list:
        st.subheader("📋 客戶應收帳款追蹤清單")
        
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    display_data = []
                    for _, row in df_ar.iterrows():
                        display_data.append({
                            "帳單單號": row.get("invoice_id"),
                            "客戶名稱": row.get("entity_name"),
                            "工程專案名稱": row.get("project_name"),
                            "交易幣別": row.get("currency"),
                            "當期應收金額": format_currency_display(row.get("amount", 0.0), row.get("currency", "VND")),
                            "約定收款日期時間": f"{row.get('due_date')} 17:00",
                            "經辦業務": row.get("quoter_name", "-"),
                            "收款狀態": "✅ 已收到錢" if row.get("is_paid") else "⏳ 未收到錢",
                            "未能收款原因說明": row.get("uncollected_reason") if row.get("uncollected_reason") else "尚未到期 / 客戶文件審核中",
                            "合約/報價單檔名": row.get("contract_file_name", "未上傳")
                        })
                    st.dataframe(pd.DataFrame(display_data), use_container_width=True)
                else:
                    st.info("目前尚無應收帳款紀錄。")
            except Exception as e:
                st.error(f"資料讀取失敗：{e}")

    with tab_quote:
        st.subheader("📄 配電盤工程正式報價單與合約細項")
        st.caption("點選下方工程可預覽詳細報價細項與合約條款：")

        sample_quote = """
======================================================================
              裕豐電機工業有限公司 (REETECH INDUSTRIAL)
                   配電盤工程正式報價單
======================================================================
專案名稱：西寧紡織廠 2000A 高壓主配電櫃新建工程
合約編號：HD-2026-TN01
客戶名稱：CÔNG TY TNHH A-Z TÂY NINH

【報價明細規格】
1. 2000A 高壓主配電櫃 (含粉體塗裝外殼 RAL 7035) x 6 台
2. 高純度導電銅排 (Busbar 10x100mm) 壓延與加工組裝
3. 施耐德 Schneider ACB 2000A 空氣斷路器 x 2 套
4. 現場安裝、高壓耐壓測試與送電驗收

----------------------------------------------------------------------
💰 合約報價總金額： ₫ 6,350,000,000 VND
💳 付款期別與條件：
   - 第一期 (30% 訂金)：₫ 1,905,000,000 VND (已結清)
   - 第二期 (60% 進場)：₫ 3,810,000,000 VND (約定到期日: 2026-10-15 17:00)
   - 第三期 (10% 驗收)：₫ 635,000,000 VND
======================================================================
        """
        st.code(sample_quote, language="text")

    with tab_add:
        st.subheader("➕ 登記新客戶應付款項 (AR)")
        with st.form("add_ar_form"):
            col1, col2 = st.columns(2)
            with col1:
                entity_name = st.text_input("客戶公司名稱 *")
                project_name = st.text_input("工程名稱 / 銷售產品品名 *")
                project_period = st.text_input("工程合約編號 / PO單號")
                quoter_name = st.text_input("經辦業務人員")
            with col2:
                currency = st.selectbox("交易幣別", ["VND", "USD", "TWD", "CNY"])
                amount = st.number_input("這次要收的金額 *", min_value=0.0)
                quoted_amount = st.number_input("合約總報價金額", min_value=0.0)
                due_date = st.date_input("約定收款日期", datetime.date.today() + datetime.timedelta(days=15))
                uncollected_reason = st.text_area("未收款原因說明 / 備註")
                uploaded_file = st.file_uploader("📎 上傳合約 / 報價單 PDF", type=["pdf", "jpg", "png"])

            if st.form_submit_button("💾 儲存並寫入資料庫", use_container_width=True):
                if entity_name and project_name:
                    inv_id = f"AR-2026-{datetime.datetime.now().strftime('%m%d%H%M')}"
                    file_name = uploaded_file.name if uploaded_file else "合約報價單.pdf"
                    
                    if engine:
                        with engine.connect() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO invoices (invoice_id, entity_name, project_name, project_period, quoter_name, currency, amount, quoted_amount, due_date, uncollected_reason, contract_file_name, invoice_type, is_paid)
                                    VALUES (:id, :entity, :prj, :period, :quoter, :curr, :amt, :quoted, :due, :reason, :file, 'AR', false)
                                """),
                                {
                                    "id": inv_id, "entity": entity_name, "prj": project_name, "period": project_period,
                                    "quoter": quoter_name, "curr": currency, "amt": amount, "quoted": quoted_amount,
                                    "due": due_date, "reason": uncollected_reason, "file": file_name
                                }
                            )
                            conn.commit()
                    st.success(f"客戶應收帳單 {inv_id} 已成功建立！")
                    st.rerun()

def show(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def main(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)
