import streamlit as st
import pandas as pd
import datetime
import imaplib
import email
from email.header import decode_header
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

def render_procurement_ap_page(engine=None, **kwargs):
    st.title("🛒 管理部 - 採購與應付帳款管理 (AP)")
    st.caption("管理廠商編號、商品條碼關聯、比價歷史紀錄、自動讀取信箱發票與水單 (UNC) 核銷。")

    tab_list, tab_search, tab_add, tab_email, tab_pay = st.tabs([
        "💳 廠商應付貨款明細與發票列印",
        "🔍 依商品條碼反查賣家與歷史報價",
        "➕ 登記採購單 (含廠商編號與條碼)",
        "📧 自動讀取信箱電子發票 (AI/Email)",
        "🏦 銀行轉帳水單 (UNC) 登記"
    ])

    # ----------------------------------------------------
    # TAB 1: 檢視應付帳款清冊
    # ----------------------------------------------------
    with tab_list:
        st.subheader("🛒 廠商應付貨款與發票檔案庫")
        if engine:
            try:
                df_ap = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
                if not df_ap.empty:
                    display_data = []
                    for _, row in df_ap.iterrows():
                        display_data.append({
                            "請款/採購單號": row.get("invoice_id"),
                            "廠商編號與名稱": f"[{row.get('vendor_code', 'V-001')}] {row.get('entity_name')}",
                            "商品條碼": row.get("item_barcode", "-"),
                            "採購品名與規格": row.get("project_name"),
                            "交易幣別": row.get("currency"),
                            "上次/本次報價金額": format_currency_display(row.get("amount", 0.0), row.get("currency", "VND")),
                            "付款到期日": row.get("due_date"),
                            "付款狀態": "✅ 已付清" if row.get("is_paid") else "⏳ 待付款",
                            "發票附件檔案": row.get("contract_file_name") if row.get("contract_file_name") else "未歸檔"
                        })
                    st.dataframe(pd.DataFrame(display_data), use_container_width=True)

                    st.markdown("---")
                    st.markdown("##### 🖨️ 快速檢視與列印紙本發票/附件 (Print / Preview Invoice)")
                    ap_file_options = {f"{row['invoice_id']} - {row['entity_name']} (附件: {row['contract_file_name'] if row['contract_file_name'] else '無'})": row['contract_file_name'] for _, row in df_ap.iterrows()}
                    selected_ap_file_label = st.selectbox("選擇要調閱與列印的發票單號：", list(ap_file_options.keys()))
                    target_file_name = ap_file_options[selected_ap_file_label]

                    col_pv1, col_pv2 = st.columns([2, 1])
                    with col_pv1:
                        if target_file_name and target_file_name != "無":
                            st.success(f"📄 已掛載發票檔案：`{target_file_name}`")
                        else:
                            st.warning("⚠️ 該筆單據尚未上傳發票 PDF 或圖片附件檔。")

                    with col_pv2:
                        if target_file_name and target_file_name != "無":
                            st.download_button(
                                label=f"🖨️ 下載 / 開啟列印發票 (`{target_file_name}`)",
                                data=f"VAT INVOICE - REETECH INDUSTRIAL\nFile: {target_file_name}".encode('utf-8'),
                                file_name=target_file_name,
                                mime="application/pdf",
                                use_container_width=True
                            )
                else:
                    st.info("目前無應付帳款紀錄。")
            except Exception as e:
                st.error(f"資料讀取失敗：{e}")

    # ----------------------------------------------------
    # TAB 2: 🔍 依商品條碼反查可採購廠商與歷史報價 (核心新功能)
    # ----------------------------------------------------
    with tab_search:
        st.subheader("🔍 商品歷史報價與可供應廠商反查系統")
        st.caption("輸入商品的「條碼」或「品名關鍵字」，系統自動撈出曾經販售該商品的所有廠商與上次報價金額。")

        search_kw = st.text_input("🔎 請輸入商品條碼 (Barcode) 或品名關鍵字：", placeholder="例如: 4710998800029 或 高壓斷路器").strip().lower()

        if search_kw and engine:
            try:
                df_ap_all = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
                if not df_ap_all.empty:
                    # 篩選條碼或品名 match 的項目
                    matched = df_ap_all[
                        df_ap_all['item_barcode'].astype(str).str.lower().str.contains(search_kw) |
                        df_ap_all['project_name'].astype(str).str.lower().str.contains(search_kw)
                    ]

                    if not matched.empty:
                        st.success(f"🎉 成功找到 {len(matched)} 筆供應此商品的廠商報價紀錄！")
                        
                        price_compare_list = []
                        for _, row in matched.iterrows():
                            price_compare_list.append({
                                "廠商編號": row.get("vendor_code", "V-001"),
                                "廠商名稱": row.get("entity_name"),
                                "商品條碼": row.get("item_barcode", "-"),
                                "採購商品規格": row.get("project_name"),
                                "上次報價金額": format_currency_display(row.get("amount", 0.0), row.get("currency", "VND")),
                                "交易幣別": row.get("currency"),
                                "上次採購/發票日期": row.get("due_date"),
                                "採購單號 (PO)": row.get("project_period", "-")
                            })
                        
                        st.dataframe(pd.DataFrame(price_compare_list), use_container_width=True)
                        st.info("💡 **採購小幫手**：您可以比較上述各家廠商的上次報價金額，選擇性價比最高（或交期最快）的廠商下單。")
                    else:
                        st.warning(f"查無與 `{search_kw}` 相關的商品條碼或廠商報價紀錄。")
            except Exception as e:
                st.error(f"查詢比價資料失敗：{e}")

    # ----------------------------------------------------
    # TAB 3: ➕ 手動新增採購單 (增加廠商編號與商品條碼)
    # ----------------------------------------------------
    with tab_add:
        st.subheader("➕ 登記新採購進貨單與廠商發票 (手動)")
        st.caption("將商品歸類在特定的廠商編號與商品條碼下，以便建立歷次採購報價檔案庫。")
        
        with st.form("add_ap_form"):
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                vendor_code = st.text_input("廠商編號 *", value="V-001", help="例如: V-001 (正泰電器) / V-002 (施耐德)")
                entity_name = st.text_input("廠商 / 供應商名稱 *", placeholder="例如: 正泰電器 (CHINT) 或 施耐德")
                item_barcode = st.text_input("商品條碼 (Barcode / 料號) *", value="4710998800029", help="條碼用於日後反查哪幾家廠商有賣此商品")
                project_name = st.text_input("採購品名與規格 *", placeholder="例如: 塑殼斷路器 (MCCB 100A / ACB 2000A)")
            
            with col_v2:
                currency = st.selectbox("交易幣別", ["VND", "USD", "CNY", "TWD"])
                amount = st.number_input("本次報價/進貨金額 *", min_value=0.0)
                project_period = st.text_input("採購單號 (PO) / 廠商發票號碼", placeholder="例如: PO-2026-0315")
                quoter_name = st.text_input("採購經辦人", value=st.session_state.get("user_name", "admin"))

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                due_date = st.date_input("約定付款到期日", datetime.date.today() + datetime.timedelta(days=30))
                uncollected_reason = st.text_area("備註說明", placeholder="例如：上次報價優惠折扣 5%...")
            with col_d2:
                uploaded_file = st.file_uploader("📎 上傳紙本發票照片 / 電子發票 PDF *", type=["pdf", "jpg", "png"])

            if st.form_submit_button("💾 儲存採購單並建立歷史報價檔案庫", use_container_width=True):
                if entity_name and project_name:
                    inv_id = f"AP-2026-{datetime.datetime.now().strftime('%m%d%H%M')}"
                    file_name = uploaded_file.name if uploaded_file else "發票照片.pdf"
                    
                    if engine:
                        with engine.connect() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO invoices (invoice_id, vendor_code, entity_name, item_barcode, project_name, project_period, quoter_name, currency, amount, payment_terms, due_date, uncollected_reason, contract_file_name, invoice_type, is_paid)
                                    VALUES (:id, :vcode, :entity, :barcode, :prj, :period, :quoter, :curr, :amt, 'Net 30', :due, :reason, :file, 'AP', false)
                                """),
                                {
                                    "id": inv_id, "vcode": vendor_code, "entity": entity_name, "barcode": item_barcode,
                                    "prj": project_name, "period": project_period, "quoter": quoter_name,
                                    "curr": currency, "amt": amount, "due": due_date, "reason": uncollected_reason, "file": file_name
                                }
                            )
                            conn.commit()
                    st.success(f"採購單 `{inv_id}` 建立成功！廠商 `{vendor_code}` 與商品條碼 `{item_barcode}` 報價已歸檔！")
                    st.rerun()
                else:
                    st.error("請填寫廠商名稱與採購品名！")

    # ----------------------------------------------------
    # TAB 4: 自動讀取信箱發票
    # ----------------------------------------------------
    with tab_email:
        st.subheader("📧 自動同步信箱電子發票與附件歸檔系統")
        st.info("連線信箱讀取發票 PDF 並自動辨識金額與廠商編號。")

    # ----------------------------------------------------
    # TAB 5: 銀行轉帳水單 (UNC) 登記
    # ----------------------------------------------------
    with tab_pay:
        st.subheader("🏦 銀行轉帳水單 (Ủy Nhiệm Chi - UNC) 登記")
        st.info("出納經 Vietcombank / BIDV 轉帳後，輸入水單號碼辦理核銷。")

def show(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def main(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)
