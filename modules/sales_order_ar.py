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
    st.title("📋 管理部 - 客戶應收帳款 (AR) & 催收稽核軌跡")
    st.caption("即時記錄每次向客戶催討帳款的理由、更新預計付款時間，並保存修改人與催款稽核歷程。")

    tab_list, tab_edit, tab_quote, tab_add = st.tabs([
        "📑 客戶應收款項明細表",
        "📝 編輯/登記催收歷程與修改理由",
        "📄 配電盤工程報價單與合約內容",
        "➕ 登記新應收帳款/合約"
    ])

    # ----------------------------------------------------
    # TAB 1: 客戶應收款項明細表
    # ----------------------------------------------------
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
                            "約定/更新後到期日": f"{row.get('due_date')}",
                            "經辦/催款人": row.get("quoter_name", "-"),
                            "收款狀態": "✅ 已收到錢" if row.get("is_paid") else "⏳ 未收到錢",
                            "最新未能收款原因說明": row.get("uncollected_reason") if row.get("uncollected_reason") else "尚未到期 / 客戶文件審核中",
                            "合約/報價單檔名": row.get("contract_file_name", "未上傳")
                        })
                    st.dataframe(pd.DataFrame(display_data), use_container_width=True)
                else:
                    st.info("目前尚無應收帳款紀錄。")
            except Exception as e:
                st.error(f"資料讀取失敗：{e}")

    # ----------------------------------------------------
    # TAB 2: 編輯與催收紀錄（包含修改人與討要理由稽核）
    # ----------------------------------------------------
    with tab_edit:
        st.subheader("📝 登記催收歷程與更新付款承諾")
        st.caption("每次向客戶討要帳款後，在此輸入客戶給的最新理由、新承諾付款日期與催款經辦人。")

        if engine:
            try:
                df_ar_edit = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR' AND is_paid = false", engine)
                if not df_ar_edit.empty:
                    ar_options = {f"{row['invoice_id']} - {row['entity_name']} ({format_currency_display(row['amount'], row['currency'])})": row['invoice_id'] for _, row in df_ar_edit.iterrows()}
                    
                    selected_ar_label = st.selectbox("請選擇要更新催收進度的帳單：", list(ar_options.keys()))
                    target_id = ar_options[selected_ar_label]
                    
                    target_row = df_ar_edit[df_ar_edit['invoice_id'] == target_id].iloc[0]

                    st.markdown("---")
                    st.markdown(f"#### 🔍 目前帳單資訊：`{target_id}` - {target_row['entity_name']}")
                    st.write(f"• **工程專案**：{target_row['project_name']}")
                    st.write(f"• **這次要收金額**：`{format_currency_display(target_row['amount'], target_row['currency'])}`")
                    st.write(f"• **原本約定到期日**：`{target_row['due_date']}`")

                    with st.form("form_update_collection_history"):
                        st.markdown("##### ✍️ 填寫這次催款與修改資訊")
                        col_e1, col_e2 = st.columns(2)
                        
                        with col_e1:
                            new_due_date = st.date_input("客戶承諾延後至何時付款（新到期日）", value=datetime.date.today() + datetime.timedelta(days=15))
                            modifier_name = st.text_input("修改/催款記錄人姓名 *", value=st.session_state.get("user_name", "經辦業務"))
                        
                        with col_e2:
                            mark_as_paid = st.checkbox("🎉 客戶已正式匯款（標記為已結清此筆應付款）")
                            delay_reason = st.text_area("客戶給的拖延/未付款理由 *", placeholder="例如: 客戶會計表示第二期工程驗收單尚未簽核完畢，承諾延至 10/25 撥款。")

                        btn_save_history = st.form_submit_button("💾 儲存催收歷程並更新狀態", use_container_width=True)

                        if btn_save_history:
                            if not delay_reason or not modifier_name:
                                st.error("請填寫修改人姓名以及客戶拖延/未付款理由！")
                            else:
                                now_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                old_reason = target_row['uncollected_reason'] if target_row['uncollected_reason'] else "無"
                                
                                # 組合追記 Audit Log 流水帳記錄
                                audit_log_entry = f"【{now_timestamp} 催款員: {modifier_name}】客戶延至 {new_due_date} 付款。理由：{delay_reason}\n"
                                updated_full_reason = f"{audit_log_entry}\n{old_reason}"

                                with engine.connect() as conn:
                                    conn.execute(
                                        text("""
                                            UPDATE invoices 
                                            SET due_date = :due,
                                                uncollected_reason = :reason,
                                                quoter_name = :quoter,
                                                is_paid = :paid
                                            WHERE invoice_id = :id
                                        """),
                                        {
                                            "due": new_due_date,
                                            "reason": updated_full_reason,
                                            "quoter": modifier_name,
                                            "paid": mark_as_paid,
                                            "id": target_id
                                        }
                                    )
                                    conn.commit()
                                st.success(f"帳單 {target_id} 催收歷史已成功紀錄！最新預計付款日更新為 {new_due_date}。")
                                st.rerun()

                    # 顯示該筆帳單歷史催款軌跡歷史紀錄
                    st.markdown("---")
                    st.markdown("#### 📜 該筆帳單歷史催款與討要理由軌跡紀錄 (Audit Trail)")
                    if target_row['uncollected_reason']:
                        st.text_area("歷史紀錄明細 (時間 / 記錄人 / 理由)", value=target_row['uncollected_reason'], height=200, disabled=True)
                    else:
                        st.info("此帳單目前尚無歷史催款記錄。")
                else:
                    st.info("目前所有客戶應收帳款皆已收齊結清！")
            except Exception as e:
                st.error(f"讀取資料失敗：{e}")

    # ----------------------------------------------------
    # TAB 3: 配電盤工程報價單與合約
    # ----------------------------------------------------
    with tab_quote:
        st.subheader("📄 配電盤工程正式報價單與合約細項")
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

    # ----------------------------------------------------
    # TAB 4: 登記新應收帳款
    # ----------------------------------------------------
    with tab_add:
        st.subheader("➕ 登記新客戶應付款項 (AR)")
        with st.form("add_ar_form"):
            col1, col2 = st.columns(2)
            with col1:
                entity_name = st.text_input("客戶公司名稱 *")
                project_name = st.text_input("工程名稱 / 銷售產品品名 *")
                project_period = st.text_input("工程合約編號 / PO單號")
                quoter_name = st.text_input("經辦業務人員", value=st.session_state.get("user_name", ""))
            with col2:
                currency = st.selectbox("交易幣別", ["USD", "VND", "TWD", "CNY"])
                amount = st.number_input("這次要收的金額 *", min_value=0.0)
                quoted_amount = st.number_input("合約總報價金額", min_value=0.0)
                due_date = st.date_input("約定收款日期", datetime.date.today() + datetime.timedelta(days=15))
                uncollected_reason = st.text_area("初始未收款原因 / 備註", value="尚未到期 / 客戶文件審核中")
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
