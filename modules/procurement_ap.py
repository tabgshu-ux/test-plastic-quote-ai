import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ----------------------------------------------------
# 🌐 企業級採購與應付帳款多語系字典 (i18n)
# ----------------------------------------------------
AP_I18N = {
    "繁體中文": {
        "page_title": "🛒 企業級採購與應付帳款系統 (Procurement & AP ERP)",
        "sub_title": "整合供應商管理、PR/PO 電子簽核、進貨驗收、三方媒合 (3-Way Matching) 與帳齡分析",
        "tab_vendor": "🏢 1. 供應商管理",
        "tab_po": "📝 2. 請購/採購/簽核",
        "tab_rcv": "📦 3. 進貨驗收",
        "tab_ap": "💳 4. 應付帳款與三方媒合",
        "tab_report": "📊 5. 付款排程與帳齡分析"
    },
    "Tiếng Việt": {
        "page_title": "🛒 Hệ Thống Mua Hàng & Khoản Phải Trả (Procurement & AP ERP)",
        "sub_title": "Tích hợp Quản lý nhà cung cấp, Duyệt PR/PO, Nghiệm thu, Đối soát 3 bên (3-Way Matching) & Tuổi nợ",
        "tab_vendor": "🏢 1. QL Nhà cung cấp",
        "tab_po": "📝 2. Yêu cầu & Đơn mua hàng",
        "tab_rcv": "📦 3. Nhập kho & Kiểm hàng",
        "tab_ap": "💳 4. Phải trả & Đối soát 3 bên",
        "tab_report": "📊 5. Lịch thanh toán & Tuổi nợ"
    },
    "English": {
        "page_title": "🛒 Enterprise Procurement & AP ERP System",
        "sub_title": "Integrated Vendor Management, PR/PO Workflow, Receiving Inspection, 3-Way Matching & Aging Analytics",
        "tab_vendor": "🏢 1. Vendor Management",
        "tab_po": "📝 2. PR/PO & Workflow",
        "tab_rcv": "📦 3. Receiving & Inspection",
        "tab_ap": "💳 4. AP & 3-Way Matching",
        "tab_report": "📊 5. Payment & Aging Analytics"
    }
}

def get_ap_lang_dict(lang_param=None):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return AP_I18N.get(lang, AP_I18N["繁體中文"])

def render_procurement_ap_page(sub_option=None, lang=None):
    L = get_ap_lang_dict(lang)
    current_lang = lang or "繁體中文"

    st.title(L["page_title"])
    st.caption(L["sub_title"])

    # ----------------------------------------------------
    # 🗄️ 初始化企業級資料庫 (Session State)
    # ----------------------------------------------------
    if "vendor_db" not in st.session_state:
        st.session_state.vendor_db = [
            {"code": "V-001", "name": "奇美實業 (CHIMEI)", "tax_id": "68521008", "currency": "USD", "bank": "兆豐銀行 (017) 123456789", "contact": "張業務副理", "phone": "+886-6-266-3000", "iso": "ISO 9001 / ISO 14001", "score": 92.5},
            {"code": "V-002", "name": "住友化學 (Sumitomo)", "tax_id": "89542011", "currency": "USD", "bank": "三井住友銀行 987654321", "contact": "林經理", "phone": "+886-2-2500-1234", "iso": "ISO 9001", "score": 88.0}
        ]

    if "po_db" not in st.session_state:
        st.session_state.po_db = [
            {"pr_id": "PR-2026-001", "po_id": "PO-2026-001", "dept": "生產二課", "budget_status": "🟢 預算內", "item": "PP 塑膠顆粒 (50 噸)", "qty": 50, "price": 900.0, "total": 45000.0, "vendor": "奇美實業 (CHIMEI)", "approval": "✅ 總經理已核準", "status": "已發送 PO"}
        ]

    if "rcv_db" not in st.session_state:
        st.session_state.rcv_db = [
            {"rcv_id": "RCV-2026-001", "po_id": "PO-2026-001", "item": "PP 塑膠顆粒", "order_qty": 50, "rcv_qty": 50, "batch_no": "LOT-20260320-A", "qc_result": "🟢 合格入庫", "on_time_rate": "100%"}
        ]

    if "ap_db" not in st.session_state:
        st.session_state.ap_db = [
            {
                "ap_id": "AP-2026-001",
                "vendor": "奇美實業 (CHIMEI)",
                "item": "PP 塑膠顆粒",
                "po_amount": 45000.0,
                "rcv_amount": 45000.0,
                "inv_amount": 45000.0,
                "match_status": "🟢 三方完全吻合 (Matched)",
                "prepaid": 15000.0,
                "remaining": 30000.0,
                "due_date": "2026-04-30",
                "p1": "2026-03-01 ($15,000)",
                "p2": "未付款",
                "p3": "未付款",
                "voucher": "借：原料庫存 $45,000 / 貸：應付帳款 $45,000"
            }
        ]

    if "audit_log" not in st.session_state:
        st.session_state.audit_log = [
            {"time": "2026-03-24 09:30", "user": "Alex Chen (Procurement)", "action": "建立請購單 PR-2026-001 且預算檢核通過"},
            {"time": "2026-03-24 10:15", "user": "GM System", "action": "電子簽核核准 PR-2026-001 並自動轉為 PO-2026-001"}
        ]

    # 5 大功能子系統頁籤
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        L["tab_vendor"],
        L["tab_po"],
        L["tab_rcv"],
        L["tab_ap"],
        L["tab_report"]
    ])

    # ----------------------------------------------------
    # 🏢 1. 供應商管理模組 (Vendor Management)
    # ----------------------------------------------------
    with tab1:
        st.markdown("### 🏢 供應商基本資料、合規審核與評鑑管理")
        col_v1, col_v2 = st.columns([2, 1])
        
        with col_v1:
            st.markdown("#### 📋 合作供應商清冊")
            st.dataframe(pd.DataFrame(st.session_state.vendor_db), use_container_width=True)

        with col_v2:
            st.markdown("#### ➕ 新增/審核供應商准入")
            with st.form("form_add_vendor"):
                v_name = st.text_input("供應商名稱：", value="臺灣塑膠 (FPC)")
                v_tax = st.text_input("統一編號 / 稅號：", value="11400201")
                v_curr = st.selectbox("交易幣別：", ["USD", "TWD", "VND", "RMB"])
                v_bank = st.text_input("匯款銀行與帳號：", value="華南銀行 (008) 987654321")
                v_iso = st.multiselect("合規認證 (ISO/QS)：", ["ISO 9001", "ISO 14001", "IATF 16949"], default=["ISO 9001"])
                v_contact = st.text_input("聯絡人：", value="王課長")
                v_phone = st.text_input("電話：", value="+886-2-8770-1688")
                
                if st.form_submit_button("🚀 儲存並通過合規審核"):
                    st.session_state.vendor_db.append({
                        "code": f"V-00{len(st.session_state.vendor_db)+1}",
                        "name": v_name, "tax_id": v_tax, "currency": v_curr,
                        "bank": v_bank, "contact": v_contact, "phone": v_phone,
                        "iso": "/".join(v_iso), "score": 90.0
                    })
                    st.session_state.audit_log.append({"time": str(date.today()), "user": "Admin", "action": f"新增合格供應商 {v_name}"})
                    st.success("✅ 供應商准入審核成功！")
                    st.rerun()

    # ----------------------------------------------------
    # 📝 2. 採購管理模組 (PR / PO / 電子簽核)
    # ----------------------------------------------------
    with tab2:
        st.markdown("### 📝 請購申請 (PR) ➔ 自動預算檢核 ➔ 電子簽核 ➔ 轉 PO")
        
        col_po1, col_po2 = st.columns([1, 1])
        with col_po1:
            st.markdown("#### 1️⃣ 填寫請購單 (PR)")
            req_dept = st.selectbox("需求部門：", ["生產一課 (射出)", "生產二課 (模具)", "研發部 (R&D)", "廠務部"])
            pr_item = st.text_input("請購品項名稱：", value="ABS 工程塑膠顆粒 (20 噸)")
            pr_qty = st.number_input("請購數量：", min_value=1, value=20)
            pr_price = st.number_input("預估單價 (USD)：", min_value=1.0, value=1200.0)
            pr_total = pr_qty * pr_price
            
            # 自動檢核部門預算
            dept_budget_limit = 50000.0
            if pr_total > dept_budget_limit:
                budget_chk = "🔴 超出部門預算上限 ($50,000)"
                st.error(f"⚠️ 預估金額 ${pr_total:,.2f} USD，{budget_chk}")
            else:
                budget_chk = "🟢 預算額度內"
                st.success(f"✅ 預估金額 ${pr_total:,.2f} USD，{budget_chk}")

            vendor_sel = st.selectbox("指定供應商：", [v["name"] for v in st.session_state.vendor_db])

        with col_po2:
            st.markdown("#### 2️⃣ 電子簽核流程 (Workflow)")
            if pr_total < 10000:
                wf_route = "部門主管簽核 ➔ 自動發單"
            elif pr_total < 50000:
                wf_route = "部門主管 ➔ 財務經理 ➔ 發單"
            else:
                wf_route = "部門主管 ➔ 財務經理 ➔ 總經理 (GM) 親簽 ➔ 發單"
            
            st.info(f"🛣️ **簽核路由**：{wf_route}")

            if st.button("🚀 提交 PR 請購並發送電子簽核", type="primary"):
                pr_code = f"PR-2026-00{len(st.session_state.po_db)+1}"
                po_code = f"PO-2026-00{len(st.session_state.po_db)+1}"
                
                st.session_state.po_db.append({
                    "pr_id": pr_code, "po_id": po_code, "dept": req_dept,
                    "budget_status": budget_chk, "item": pr_item, "qty": pr_qty,
                    "price": pr_price, "total": pr_total, "vendor": vendor_sel,
                    "approval": "✅ 總經理已核准", "status": "已一鍵轉 PO 並 Email 通知廠商"
                })
                st.session_state.audit_log.append({"time": str(date.today()), "user": "PR System", "action": f"建立 {pr_code} 並轉為 {po_code}"})
                st.success(f"🎉 請購單已自動轉為正式採購單 {po_code}，並同步 PDF 給 {vendor_sel}！")
                st.rerun()

        st.markdown("#### 📋 採購單 (PO) 追蹤表")
        st.dataframe(pd.DataFrame(st.session_state.po_db), use_container_width=True)

    # ----------------------------------------------------
    # 📦 3. 進貨驗收模組 (Receiving & Inspection)
    # ----------------------------------------------------
    with tab3:
        st.markdown("### 📦 倉管收料、批號追蹤與線上驗退流程")
        
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            po_to_rcv = st.selectbox("選擇進貨採購單 (PO)：", [p["po_id"] + " — " + p["item"] for p in st.session_state.po_db])
            rcv_qty_input = st.number_input("本次實收數量：", min_value=1, value=20)
            batch_input = st.text_input("進貨製造批號 (Batch/Lot No.)：", value="LOT-20260324-B2")
            qc_status = st.selectbox("品管 (QC) 檢驗結果：", ["🟢 合格特採入庫", "🔴 瑕疵退貨 (RTV)", "🟡 暫存待判"])

        with col_r2:
            st.markdown("#### 📊 供應商達交率與不良率統計")
            st.metric("奇美實業 準時交貨率 (On-Time)", "98.5%", "+1.2%")
            st.metric("進貨檢驗不良率 (Defect Rate)", "0.3%", "-0.1%")

            if st.button("💾 登記收料並產生驗收單 (Receiving Sheet)", type="primary"):
                rcv_code = f"RCV-2026-00{len(st.session_state.rcv_db)+1}"
                st.session_state.rcv_db.append({
                    "rcv_id": rcv_code, "po_id": po_to_rcv.split(" — ")[0],
                    "item": po_to_rcv.split(" — ")[1], "order_qty": 20,
                    "rcv_qty": rcv_qty_input, "batch_no": batch_input,
                    "qc_result": qc_status, "on_time_rate": "100%"
                })
                st.success(f"✅ 已成功建立驗收單 {rcv_code}！")
                st.rerun()

        st.dataframe(pd.DataFrame(st.session_state.rcv_db), use_container_width=True)

    # ----------------------------------------------------
    # 💳 4. 應付帳款與三方媒合 (AP & 3-Way Matching)
    # ----------------------------------------------------
    with tab4:
        st.markdown("### 💳 三方媒合機制 (3-Way Matching) 與會計過帳傳票")
        st.info("💡 **三方媒合核心規則**：系統自動比對 **採購單 (PO) 金額 = 驗收單 (Receiving) 數量 = 廠商發票 (Invoice) 金額**。若完全吻合方可立帳與出金；若有差異將自動鎖定！")

        col_ap1, col_ap2 = st.columns([1, 1])
        with col_ap1:
            st.markdown("#### 1️⃣ 自動三方比對檢核")
            inv_no = st.text_input("輸入廠商發票號碼 (E-Invoice XML/OCR)：", value="INV-20260324-088")
            inv_val = st.number_input("發票開立總金額 (USD)：", min_value=1.0, value=24000.0)
            
            # 模擬 3-Way Matching 檢核邏輯
            po_val = 24000.0
            rcv_val = 24000.0
            
            if abs(inv_val - po_val) < 0.01 and abs(inv_val - rcv_val) < 0.01:
                match_res = "🟢 三方完全吻合 (Matched)"
                st.success(f"✅ 比對結果：PO (${po_val:,.0f}) = 驗收 (${rcv_val:,.0f}) = 發票 (${inv_val:,.0f})。准予立帳！")
            else:
                match_res = "🔴 差異鎖定 (Price/Qty Mismatch)"
                st.error("❌ 金額不符！系統已發送異常警示給採購與財務主管，禁止付款！")

        with col_ap2:
            st.markdown("#### 2️⃣ 自動生成會計分錄 (Voucher)")
            st.code(f"""
            [傳票自動過帳]
            借：原料庫存 (Inventory)      ${inv_val:,.2f} USD
            貸：應付帳款 (Accounts Payable)  ${inv_val:,.2f} USD
            """, language="text")

            if st.button("🚀 執行 3-Way 比對並建立 AP 應付帳款", type="primary"):
                ap_code = f"AP-2026-00{len(st.session_state.ap_db)+1}"
                st.session_state.ap_db.append({
                    "ap_id": ap_code, "vendor": "奇美實業 (CHIMEI)",
                    "item": "ABS 工程塑膠", "po_amount": po_val,
                    "rcv_amount": rcv_val, "inv_amount": inv_val,
                    "match_status": match_res, "prepaid": 7200.0,
                    "remaining": inv_val - 7200.0, "due_date": "2026-05-31",
                    "p1": f"{date.today()} ($7,200)", "p2": "未付款", "p3": "未付款",
                    "voucher": f"借：原料庫存 ${inv_val:,.0f} / 貸：應付帳款 ${inv_val:,.0f}"
                })
                st.success(f"🎉 應付帳單 {ap_code} 立帳成功！")
                st.rerun()

        st.markdown("#### 💳 應付帳款與分 3 期沖銷清冊")
        st.dataframe(pd.DataFrame(st.session_state.ap_db), use_container_width=True)

    # ----------------------------------------------------
    # 📊 5. 付款排程與帳齡分析 (Payment & Analytics)
    # ----------------------------------------------------
    with tab5:
        st.markdown("### 📊 應付帳款帳齡分析表 (Aging Report) 與稽核軌跡")
        
        col_ag1, col_ag2, col_ag3, col_ag4 = st.columns(4)
        col_ag1.metric("未到期帳款 (Current)", "$30,000 USD", "🟢 正常")
        col_ag2.metric("逾期 1-30 天", "$16,800 USD", "🟡 提醒付款")
        col_ag3.metric("逾期 31-60 天", "$0 USD", "🟢 健康")
        col_ag4.metric("逾期 >60 天", "$0 USD", "🟢 無滯欠")

        st.divider()

        st.markdown("#### 🔒 系統操作稽核軌跡 (Audit Trail Log - 資安與內控合規)")
        st.dataframe(pd.DataFrame(st.session_state.audit_log), use_container_width=True)

def show(sub_option=None, lang=None):
    render_procurement_ap_page(sub_option, lang)

def main(sub_option=None, lang=None):
    render_procurement_ap_page(sub_option, lang)
