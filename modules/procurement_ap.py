import streamlit as st
import pandas as pd
import datetime
import imaplib
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 採購與應付帳款模組三語系字典 (i18n)
# ----------------------------------------------------
AP_I18N = {
    "繁體中文": {
        "title": "🛒 管理部 - 採購與應付帳款管理 (AP)",
        "caption": "管理廠商編號、商品條碼關聯、比價歷史紀錄、自動讀取信箱發票與水單 (UNC) 核銷。",
        "tab_list": "💳 廠商應付貨款明細與發票列印",
        "tab_search": "🔍 依商品條碼反查賣家與歷史報價",
        "tab_add": "➕ 登記採購單 (含廠商編號與條碼)",
        "tab_email": "📧 自動讀取信箱電子發票 (AI/Email)",
        "tab_pay": "🏦 銀行轉帳水單 (UNC) 登記",
        "sec_list_title": "🛒 廠商應付貨款與發票檔案庫",
        "col_po_id": "請款/採購單號",
        "col_vendor": "廠商編號與名稱",
        "col_barcode": "商品條碼",
        "col_product": "採購品名與規格",
        "col_currency": "交易幣別",
        "col_amount": "上次/本次報價金額",
        "col_due_date": "付款到期日",
        "col_status": "付款狀態",
        "col_file": "發票附件檔案",
        "status_paid": "✅ 已付清",
        "status_unpaid": "⏳ 待付款",
        "status_nofile": "未歸檔",
        "sec_print_title": "🖨️ 快速檢視與列印紙本發票/附件 (Print / Preview Invoice)",
        "select_inv_label": "選擇要調閱與列印的發票單號：",
        "no_file_warn": "⚠️ 該筆單據尚未上傳發票 PDF 或圖片附件檔。",
        "btn_download": "🖨️ 下載 / 開啟列印發票",
        "sec_search_title": "🔍 商品歷史報價與可供應廠商反查系統",
        "search_caption": "輸入商品的「條碼」或「品名關鍵字」，系統自動撈出曾經販售該商品的所有廠商與上次報價金額。",
        "search_input": "🔎 請輸入商品條碼 (Barcode) 或品名關鍵字：",
        "sec_add_title": "➕ 登記新採購進貨單與廠商發票 (手動)",
        "add_caption": "將商品歸類在特定的廠商編號與商品條碼下，以便建立歷次採購報價檔案庫。",
        "lbl_vendor_code": "廠商編號 *",
        "lbl_vendor_name": "廠商 / 供應商名稱 *",
        "lbl_barcode": "商品條碼 (Barcode / 料號) *",
        "lbl_product_name": "採購品名與規格 *",
        "lbl_currency": "交易幣別",
        "lbl_amount": "本次報價/進貨金額 *",
        "lbl_po_no": "採購單號 (PO) / 廠商發票號碼",
        "lbl_buyer": "採購經辦人",
        "lbl_due": "約定付款到期日",
        "lbl_remark": "備註說明",
        "lbl_upload": "📎 上傳紙本發票照片 / 電子發票 PDF *",
        "btn_save": "💾 儲存採購單並建立歷史報價檔案庫",
        "sec_email_title": "📧 自動同步信箱電子發票與附件歸檔系統",
        "email_info": "連線信箱讀取發票 PDF 並自動辨識金額與廠商編號。",
        "sec_pay_title": "🏦 銀行轉帳水單 (Ủy Nhiệm Chi - UNC) 登記",
        "pay_info": "出納經 Vietcombank / BIDV 轉帳後，輸入水單號碼辦理核銷。"
    },
    "Tiếng Việt": {
        "title": "🛒 Khối Quản lý - Quản lý Mua hàng & Phải trả (AP)",
        "caption": "Quản lý mã nhà cung cấp, mã vạch sản phẩm, lịch sử báo giá, đọc hóa đơn email tự động & xác nhận UNC.",
        "tab_list": "💳 Chi tiết Phải trả & In Hóa đơn",
        "tab_search": "🔍 Tra cứu Nhà cung cấp theo Mã vạch",
        "tab_add": "➕ Thêm Đơn Mua hàng (Có Mã NCC & Mã vạch)",
        "tab_email": "📧 Đọc Hóa đơn Điện tử từ Email (AI)",
        "tab_pay": "🏦 Quản lý Ủy Nhiệm Chi (UNC)",
        "sec_list_title": "🛒 Danh sách Khoản Phải trả & Tệp Hóa đơn VAT",
        "col_po_id": "Mã đơn hàng/PO",
        "col_vendor": "Mã & Tên Nhà cung cấp",
        "col_barcode": "Mã vạch SP",
        "col_product": "Tên & Quy cách Hàng hóa",
        "col_currency": "Tiền tệ",
        "col_amount": "Số tiền báo giá",
        "col_due_date": "Hạn thanh toán",
        "col_status": "Trạng thái",
        "col_file": "Tệp Hóa đơn Kèm theo",
        "status_paid": "✅ Đã thanh toán",
        "status_unpaid": "⏳ Chờ thanh toán",
        "status_nofile": "Chưa đính kèm",
        "sec_print_title": "🖨️ Xem nhanh & In Hóa đơn VAT giấy (Print / Preview)",
        "select_inv_label": "Chọn hóa đơn cần xem và in:",
        "no_file_warn": "⚠️ Đơn hàng này chưa được tải lên tệp PDF hoặc ảnh hóa đơn.",
        "btn_download": "🖨️ Tải về / Mở in Hóa đơn",
        "sec_search_title": "🔍 Tra cứu Lịch sử Báo giá & Nhà cung cấp",
        "search_caption": "Nhập mã vạch hoặc tên sản phẩm, hệ thống sẽ tìm tất cả NCC đã từng bán hàng và giá đợt trước.",
        "search_input": "🔎 Nhập mã vạch (Barcode) hoặc từ khóa tên sản phẩm:",
        "sec_add_title": "➕ Đăng ký Đơn Mua hàng & Hóa đơn NCC mới",
        "add_caption": "Phân loại hàng hóa theo Mã NCC và Mã vạch để lưu lịch sử báo giá mua hàng.",
        "lbl_vendor_code": "Mã Nhà cung cấp *",
        "lbl_vendor_name": "Tên Nhà cung cấp *",
        "lbl_barcode": "Mã vạch Sản phẩm (Barcode) *",
        "lbl_product_name": "Tên & Quy cách Hàng hóa *",
        "lbl_currency": "Loại tiền tệ",
        "lbl_amount": "Số tiền Mua hàng / Báo giá *",
        "lbl_po_no": "Mã PO / Số Hóa đơn NCC",
        "lbl_buyer": "Nhân viên Mua hàng",
        "lbl_due": "Ngày hạn thanh toán",
        "lbl_remark": "Ghi chú thêm",
        "lbl_upload": "📎 Tải lên tệp Hóa đơn VAT (PDF/Ảnh) *",
        "btn_save": "💾 Lưu Đơn Mua hàng & Lưu Lịch sử Báo giá",
        "sec_email_title": "📧 Đồng bộ Hóa đơn Điện tử tự động từ Email",
        "email_info": "Kết nối Email để tự động đọc PDF hóa đơn và nhận diện số tiền.",
        "sec_pay_title": "🏦 Đăng ký Ủy Nhiệm Chi (UNC) Ngân hàng",
        "pay_info": "Sau khi chuyển khoản qua Vietcombank / BIDV, nhập số UNC để xác nhận."
    },
    "English": {
        "title": "🛒 Admin - Accounts Payable & Procurement Management (AP)",
        "caption": "Manage Vendor Codes, Product Barcodes, Price History, Auto-parsing Email Invoices & UNC Bank Receipts.",
        "tab_list": "💳 AP Details & Invoice Print",
        "tab_search": "🔍 Vendor & Price Lookup by Barcode",
        "tab_add": "➕ Add PO (With Vendor Code & Barcode)",
        "tab_email": "📧 Auto Email Invoice Parser (AI)",
        "tab_pay": "🏦 Bank UNC Receipt Management",
        "sec_list_title": "🛒 AP Ledger & VAT Invoice Document Store",
        "col_po_id": "PO / Invoice ID",
        "col_vendor": "Vendor Code & Name",
        "col_barcode": "Barcode",
        "col_product": "Product Specs",
        "col_currency": "Currency",
        "col_amount": "Quoted Amount",
        "col_due_date": "Due Date",
        "col_status": "Payment Status",
        "col_file": "Attached File",
        "status_paid": "✅ Paid",
        "status_unpaid": "⏳ Pending",
        "status_nofile": "No File",
        "sec_print_title": "🖨️ Quick Preview & Print Paper VAT Invoice",
        "select_inv_label": "Select invoice to review & print:",
        "no_file_warn": "⚠️ No PDF/Image invoice file uploaded for this transaction.",
        "btn_download": "🖨️ Download / Open Print Invoice",
        "sec_search_title": "🔍 Product Price History & Vendor Search",
        "search_caption": "Enter barcode or keyword to find all vendors and past quoted prices.",
        "search_input": "🔎 Enter Product Barcode or Keyword:",
        "sec_add_title": "➕ Register New Purchase Order & Invoice",
        "add_caption": "Categorize products under Vendor Code and Barcode to maintain price history.",
        "lbl_vendor_code": "Vendor Code *",
        "lbl_vendor_name": "Vendor Name *",
        "lbl_barcode": "Product Barcode *",
        "lbl_product_name": "Product Name & Specs *",
        "lbl_currency": "Currency",
        "lbl_amount": "Amount *",
        "lbl_po_no": "PO No. / Vendor Invoice No.",
        "lbl_buyer": "Purchaser",
        "lbl_due": "Payment Due Date",
        "lbl_remark": "Remarks",
        "lbl_upload": "📎 Upload Invoice PDF / Photo *",
        "btn_save": "💾 Save PO & Price History",
        "sec_email_title": "📧 Auto Sync Email Invoices",
        "email_info": "Connect email to auto-read PDF invoices and detect amounts.",
        "sec_pay_title": "🏦 Register UNC Bank Transfer",
        "pay_info": "Enter UNC bank transfer reference after paying via Vietcombank/BIDV."
    }
}

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

def render_procurement_ap_page(engine=None, lang="繁體中文", **kwargs):
    # 自動載入對應語系字典（預設繁體中文）
    L = AP_I18N.get(lang, AP_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_search, tab_add, tab_email, tab_pay = st.tabs([
        L["tab_list"],
        L["tab_search"],
        L["tab_add"],
        L["tab_email"],
        L["tab_pay"]
    ])

    # ----------------------------------------------------
    # TAB 1: 檢視應付帳款清冊
    # ----------------------------------------------------
    with tab_list:
        st.subheader(L["sec_list_title"])
        if engine:
            try:
                df_ap = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
                if not df_ap.empty:
                    display_data = []
                    for _, row in df_ap.iterrows():
                        display_data.append({
                            L["col_po_id"]: row.get("invoice_id"),
                            L["col_vendor"]: f"[{row.get('vendor_code', 'V-001')}] {row.get('entity_name')}",
                            L["col_barcode"]: row.get("item_barcode", "-"),
                            L["col_product"]: row.get("project_name"),
                            L["col_currency"]: row.get("currency"),
                            L["col_amount"]: format_currency_display(row.get("amount", 0.0), row.get("currency", "VND")),
                            L["col_due_date"]: row.get("due_date"),
                            L["col_status"]: L["status_paid"] if row.get("is_paid") else L["status_unpaid"],
                            L["col_file"]: row.get("contract_file_name") if row.get("contract_file_name") else L["status_nofile"]
                        })
                    st.dataframe(pd.DataFrame(display_data), use_container_width=True)

                    st.markdown("---")
                    st.markdown(f"##### {L['sec_print_title']}")
                    ap_file_options = {f"{row['invoice_id']} - {row['entity_name']}": row['contract_file_name'] for _, row in df_ap.iterrows()}
                    selected_ap_file_label = st.selectbox(L["select_inv_label"], list(ap_file_options.keys()))
                    target_file_name = ap_file_options[selected_ap_file_label]

                    col_pv1, col_pv2 = st.columns([2, 1])
                    with col_pv1:
                        if target_file_name and target_file_name != "無":
                            st.success(f"📄 {target_file_name}")
                        else:
                            st.warning(L["no_file_warn"])

                    with col_pv2:
                        if target_file_name and target_file_name != "無":
                            st.download_button(
                                label=f"{L['btn_download']} (`{target_file_name}`)",
                                data=f"VAT INVOICE - REETECH INDUSTRIAL\nFile: {target_file_name}".encode('utf-8'),
                                file_name=target_file_name,
                                mime="application/pdf",
                                use_container_width=True
                            )
                else:
                    st.info("No records / Không có dữ liệu.")
            except Exception as e:
                st.error(f"Error: {e}")

    # ----------------------------------------------------
    # TAB 2: 🔍 反查賣家與歷史報價
    # ----------------------------------------------------
    with tab_search:
        st.subheader(L["sec_search_title"])
        st.caption(L["search_caption"])

        search_kw = st.text_input(L["search_input"], placeholder="4710998800029").strip().lower()

        if search_kw and engine:
            try:
                df_ap_all = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
                if not df_ap_all.empty:
                    matched = df_ap_all[
                        df_ap_all['item_barcode'].astype(str).str.lower().str.contains(search_kw) |
                        df_ap_all['project_name'].astype(str).str.lower().str.contains(search_kw)
                    ]

                    if not matched.empty:
                        price_compare_list = []
                        for _, row in matched.iterrows():
                            price_compare_list.append({
                                L["lbl_vendor_code"]: row.get("vendor_code", "V-001"),
                                L["lbl_vendor_name"]: row.get("entity_name"),
                                L["lbl_barcode"]: row.get("item_barcode", "-"),
                                L["lbl_product_name"]: row.get("project_name"),
                                L["lbl_amount"]: format_currency_display(row.get("amount", 0.0), row.get("currency", "VND")),
                                L["lbl_currency"]: row.get("currency"),
                                L["lbl_due"]: row.get("due_date")
                            })
                        st.dataframe(pd.DataFrame(price_compare_list), use_container_width=True)
            except Exception as e:
                st.error(f"Search Error: {e}")

    # ----------------------------------------------------
    # TAB 3: ➕ 手動新增採購單
    # ----------------------------------------------------
    with tab_add:
        st.subheader(L["sec_add_title"])
        st.caption(L["add_caption"])
        
        with st.form("add_ap_form_i18n"):
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                vendor_code = st.text_input(L["lbl_vendor_code"], value="V-001")
                entity_name = st.text_input(L["lbl_vendor_name"], placeholder="Schneider Electric")
                item_barcode = st.text_input(L["lbl_barcode"], value="4710998800029")
                project_name = st.text_input(L["lbl_product_name"], placeholder="ACB 2000A")
            
            with col_v2:
                currency = st.selectbox(L["lbl_currency"], ["VND", "USD", "CNY", "TWD"])
                amount = st.number_input(L["lbl_amount"], min_value=0.0)
                project_period = st.text_input(L["lbl_po_no"], placeholder="PO-2026-0315")
                quoter_name = st.text_input(L["lbl_buyer"], value=st.session_state.get("user_name", "admin"))

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                due_date = st.date_input(L["lbl_due"], datetime.date.today() + datetime.timedelta(days=30))
                uncollected_reason = st.text_area(L["lbl_remark"])
            with col_d2:
                uploaded_file = st.file_uploader(L["lbl_upload"], type=["pdf", "jpg", "png"])

            if st.form_submit_button(L["btn_save"], use_container_width=True):
                if entity_name and project_name:
                    inv_id = f"AP-2026-{datetime.datetime.now().strftime('%m%d%H%M')}"
                    file_name = uploaded_file.name if uploaded_file else "HoaDon.pdf"
                    
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
                    st.success(f"Success / Thành công: `{inv_id}`!")
                    st.rerun()

    # ----------------------------------------------------
    # TAB 4: 自動讀取信箱發票
    # ----------------------------------------------------
    with tab_email:
        st.subheader(L["sec_email_title"])
        st.info(L["email_info"])

    # ----------------------------------------------------
    # TAB 5: 銀行轉帳水單 (UNC) 登記
    # ----------------------------------------------------
    with tab_pay:
        st.subheader(L["sec_pay_title"])
        st.info(L["pay_info"])

# 模組入口相容性封裝
def show(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)
