import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# 🌐 應收帳款 (AR) 多語系字典
AR_I18N = {
    "繁體中文": {
        "title": "📋 管理部 - 客戶應收帳款 (AR) & 專案催收管理",
        "caption": "管控工程專案應付分期期別、自動計算期別金額、紀錄專案進度與催收軌跡。",
        "tab_list": "📑 應收帳款專案清單",
        "tab_add": "➕ 登記新應收帳款專案",
        "tab_update": "📝 更新專案進度與催收說明",
        "tab_quote": "📄 配電盤工程報價單範例",
        "col_id": "編號",
        "col_req_no": "請款編號",
        "col_customer": "客戶名稱",
        "col_project": "工程名稱",
        "col_currency": "交易幣別",
        "col_total": "總帳款",
        "col_installment_type": "分期類型",
        "col_desc": "專案說明",
        "col_progress": "進行進度說明",
        "lbl_installment_choice": "分期方式",
        "opt_no_inst": "不分期",
        "opt_inst_3": "分 3 期",
        "opt_inst_5": "分 5 期",
        "lbl_p1_ratio": "第一期比率 (%)",
        "lbl_p2_ratio": "第二期比率 (%)",
        "lbl_p3_ratio": "第三期比率 (%)",
        "lbl_p4_ratio": "第四期比率 (%)",
        "lbl_p5_ratio": "第五期比率 (%)",
        "lbl_p1_amt": "第一期金額",
        "lbl_p2_amt": "第二期金額",
        "lbl_p3_amt": "第三期金額",
        "lbl_p4_amt": "第四期金額",
        "lbl_p5_amt": "第五期金額",
        "lbl_pay_date": "付款日期",
        "btn_save_new": "💾 儲存並建立專案帳單",
        "btn_save_progress": "💾 儲存進度更新",
        "msg_success_add": "🎉 新應收帳款專案已成功建立！",
        "msg_success_update": "✅ 專案進度已成功更新！"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Quản lý - Phải thu Khách hàng (AR) & Quản lý Tiến độ",
        "caption": "Quản lý đợt thanh toán dự án, tự động tính số tiền theo tỷ lệ, ghi nhận tiến độ công trình.",
        "tab_list": "📑 Danh sách Dự án Phải thu",
        "tab_add": "➕ Thêm Dự án Phải thu Mới",
        "tab_update": "📝 Cập nhật Tiến độ & Ghi chú",
        "tab_quote": "📄 Mẫu Báo giá Công trình Tủ điện",
        "col_id": "STT",
        "col_req_no": "Mã Yêu Cầu",
        "col_customer": "Tên Khách Hàng",
        "col_project": "Tên Công Trình",
        "col_currency": "Tiền Tệ",
        "col_total": "Tổng Thanh Toán",
        "col_installment_type": "Hình Thức Thanh Toán",
        "col_desc": "Mô Tả Dự Án",
        "col_progress": "Cập Nhật Tiến Độ",
        "lbl_installment_choice": "Hình thức chia đợt",
        "opt_no_inst": "Không chia đợt",
        "opt_inst_3": "Chia 3 đợt",
        "opt_inst_5": "Chia 5 đợt",
        "lbl_p1_ratio": "Tỷ lệ Đợt 1 (%)",
        "lbl_p2_ratio": "Tỷ lệ Đợt 2 (%)",
        "lbl_p3_ratio": "Tỷ lệ Đợt 3 (%)",
        "lbl_p4_ratio": "Tỷ lệ Đợt 4 (%)",
        "lbl_p5_ratio": "Tỷ lệ Đợt 5 (%)",
        "lbl_p1_amt": "Số tiền Đợt 1",
        "lbl_p2_amt": "Số tiền Đợt 2",
        "lbl_p3_amt": "Số tiền Đợt 3",
        "lbl_p4_amt": "Số tiền Đợt 4",
        "lbl_p5_amt": "Số tiền Đợt 5",
        "lbl_pay_date": "Ngày thanh toán",
        "btn_save_new": "💾 Lưu & Tạo Dự Án Mới",
        "btn_save_progress": "💾 Lưu Cập Nhật Tiến Độ",
        "msg_success_add": "🎉 Đã tạo thành công dự án khoản phải thu mới!",
        "msg_success_update": "✅ Đã cập nhật tiến độ dự án thành công!"
    },
    "English": {
        "title": "📋 Admin - Accounts Receivable (AR) & Project Tracking",
        "caption": "Manage installment terms, ratio calculations, project descriptions and progress updates.",
        "tab_list": "📑 AR Project Ledger",
        "tab_add": "➕ Add New AR Project",
        "tab_update": "📝 Update Progress & Log",
        "tab_quote": "📄 Switchboard Quotation Sample",
        "col_id": "No.",
        "col_req_no": "Request No.",
        "col_customer": "Customer Name",
        "col_project": "Project Name",
        "col_currency": "Currency",
        "col_total": "Total Amount",
        "col_installment_type": "Payment Plan",
        "col_desc": "Project Description",
        "col_progress": "Progress Log",
        "lbl_installment_choice": "Payment Terms",
        "opt_no_inst": "Full Payment (No Installment)",
        "opt_inst_3": "3 Installments",
        "opt_inst_5": "5 Installments",
        "lbl_p1_ratio": "Phase 1 Ratio (%)",
        "lbl_p2_ratio": "Phase 2 Ratio (%)",
        "lbl_p3_ratio": "Phase 3 Ratio (%)",
        "lbl_p4_ratio": "Phase 4 Ratio (%)",
        "lbl_p5_ratio": "Phase 5 Ratio (%)",
        "lbl_p1_amt": "Phase 1 Amount",
        "lbl_p2_amt": "Phase 2 Amount",
        "lbl_p3_amt": "Phase 3 Amount",
        "lbl_p4_amt": "Phase 4 Amount",
        "lbl_p5_amt": "Phase 5 Amount",
        "lbl_pay_date": "Payment Date",
        "btn_save_new": "💾 Save & Create AR Project",
        "btn_save_progress": "💾 Save Progress Update",
        "msg_success_add": "🎉 New AR project created successfully!",
        "msg_success_update": "✅ Project progress updated successfully!"
    }
}

def format_currency_display(amount, curr):
    if curr in ["VND", "越南盾"]:
        return f"₫ {amount:,.0f} VND"
    elif curr in ["USD", "美金"]:
        return f"$ {amount:,.2f} USD"
    elif curr in ["TWD", "台幣"]:
        return f"NT$ {amount:,.0f} TWD"
    elif curr in ["CNY", "人民幣"]:
        return f"¥ {amount:,.2f} CNY"
    return f"{amount:,.2f} {curr}"

def render(*args, **kwargs):
    # 支援多元變數位置（包含 args 與 kwargs 中的 engine, t, lang, curr_lang）
    engine = args[0] if len(args) > 0 else kwargs.get("engine", None)
    
    # 強制擷取語言設定
    curr_lang = kwargs.get("lang", kwargs.get("curr_lang", st.session_state.get("lang", "繁體中文")))
    if curr_lang not in AR_I18N:
        curr_lang = "繁體中文"
    L = AR_I18N[curr_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # 全域範例 Session 資料保護（防資料庫斷線備用）
    if "ar_projects_store" not in st.session_state:
        st.session_state.ar_projects_store = [
            {
                "id": 1,
                "req_no": "INV-2026-001",
                "customer": "越南樟榜工業區 A 廠",
                "project": "2000A 高壓主配電櫃新建工程",
                "currency": "USD",
                "total_amount": 150000.0,
                "inst_type": L["opt_inst_3"],
                "p1_amt": 45000.0, "p1_date": "2026-09-01",
                "p2_amt": 90000.0, "p2_date": "2026-10-15",
                "p3_amt": 15000.0, "p3_date": "2026-11-30",
                "p4_amt": 0.0, "p4_date": "-",
                "p5_amt": 0.0, "p5_date": "-",
                "description": "含粉體塗裝外殼與 Busbar 壓延組裝",
                "progress_log": "第一期訂金已收齊，第二期進場款催討中。"
            }
        ]

    tab_list, tab_add, tab_update, tab_quote = st.tabs([
        L["tab_list"], L["tab_add"], L["tab_update"], L["tab_quote"]
    ])

    # ----------------------------------------------------
    # TAB 1: 專案應收帳款明細表 (全新格式)
    # ----------------------------------------------------
    with tab_list:
        st.subheader(L["tab_list"])
        
        display_rows = []
        for p in st.session_state.ar_projects_store:
            row_dict = {
                L["col_id"]: p["id"],
                L["col_req_no"]: p["req_no"],
                L["col_customer"]: p["customer"],
                L["col_project"]: p["project"],
                L["col_currency"]: p["currency"],
                L["col_total"]: format_currency_display(p["total_amount"], p["currency"]),
                L["col_installment_type"]: p["inst_type"],
                f"{L['lbl_p1_amt']} & {L['lbl_pay_date']}": f"{format_currency_display(p['p1_amt'], p['currency'])} ({p['p1_date']})",
                f"{L['lbl_p2_amt']} & {L['lbl_pay_date']}": f"{format_currency_display(p['p2_amt'], p['currency'])} ({p['p2_date']})" if p['p2_amt'] > 0 else "-",
                f"{L['lbl_p3_amt']} & {L['lbl_pay_date']}": f"{format_currency_display(p['p3_amt'], p['currency'])} ({p['p3_date']})" if p['p3_amt'] > 0 else "-",
            }
            
            if L["opt_inst_5"] in p["inst_type"]:
                row_dict[f"{L['lbl_p4_amt']} & {L['lbl_pay_date']}"] = f"{format_currency_display(p['p4_amt'], p['currency'])} ({p['p4_date']})" if p['p4_amt'] > 0 else "-"
                row_dict[f"{L['lbl_p5_amt']} & {L['lbl_pay_date']}"] = f"{format_currency_display(p['p5_amt'], p['currency'])} ({p['p5_date']})" if p['p5_amt'] > 0 else "-"

            row_dict[L["col_desc"]] = p["description"]
            row_dict[L["col_progress"]] = p["progress_log"]
            display_rows.append(row_dict)

        st.dataframe(pd.DataFrame(display_rows), use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: 登記新專案 (動態比率計算 & 3/5 期欄位展開)
    # ----------------------------------------------------
    with tab_add:
        st.subheader(L["tab_add"])
        
        with st.form("form_add_ar_project"):
            c1, c2, c3 = st.columns(3)
            with c1:
                req_no = st.text_input(f"{L['col_req_no']} *", value=f"INV-2026-{len(st.session_state.ar_projects_store)+1:03d}")
                customer = st.text_input(f"{L['col_customer']} *", placeholder="例如: CÔNG TY TNHH A-Z")
            with c2:
                project = st.text_input(f"{L['col_project']} *", placeholder="例如: 西寧廠配電盤工程")
                currency = st.selectbox(f"{L['col_currency']} *", ["VND", "USD", "TWD", "CNY"])
            with c3:
                total_amount = st.number_input(f"{L['col_total']} *", min_value=0.0, value=100000.0)
                inst_choice = st.selectbox(L["lbl_installment_choice"], [L["opt_no_inst"], L["opt_inst_3"], L["opt_inst_5"]])

            st.markdown("---")
            
            # 分期比率與計算
            p1_amt, p1_date = total_amount, str(datetime.date.today())
            p2_amt, p2_date = 0.0, "-"
            p3_amt, p3_date = 0.0, "-"
            p4_amt, p4_date = 0.0, "-"
            p5_amt, p5_date = 0.0, "-"

            if inst_choice == L["opt_inst_3"]:
                st.markdown(f"##### 📑 {L['opt_inst_3']}")
                rc1, rc2, rc3 = st.columns(3)
                with rc1:
                    r1 = st.number_input(L["lbl_p1_ratio"], value=30.0)
                    d1 = st.date_input(f"1. {L['lbl_pay_date']}", value=datetime.date.today())
                with rc2:
                    r2 = st.number_input(L["lbl_p2_ratio"], value=60.0)
                    d2 = st.date_input(f"2. {L['lbl_pay_date']}", value=datetime.date.today() + datetime.timedelta(days=30))
                with rc3:
                    r3 = st.number_input(L["lbl_p3_ratio"], value=10.0)
                    d3 = st.date_input(f"3. {L['lbl_pay_date']}", value=datetime.date.today() + datetime.timedelta(days=60))

                p1_amt = total_amount * (r1 / 100.0)
                p2_amt = total_amount * (r2 / 100.0)
                p3_amt = total_amount * (r3 / 100.0)
                p1_date, p2_date, p3_date = str(d1), str(d2), str(d3)
                st.info(f"💡 第一期: `{format_currency_display(p1_amt, currency)}` | 第二期: `{format_currency_display(p2_amt, currency)}` | 第三期: `{format_currency_display(p3_amt, currency)}`")

            elif inst_choice == L["opt_inst_5"]:
                st.markdown(f"##### 📑 {L['opt_inst_5']}")
                rc1, rc2, rc3, rc4, rc5 = st.columns(5)
                with rc1:
                    r1 = st.number_input(L["lbl_p1_ratio"], value=20.0)
                    d1 = st.date_input(f"1. {L['lbl_pay_date']}", value=datetime.date.today())
                with rc2:
                    r2 = st.number_input(L["lbl_p2_ratio"], value=20.0)
                    d2 = st.date_input(f"2. {L['lbl_pay_date']}", value=datetime.date.today() + datetime.timedelta(days=30))
                with rc3:
                    r3 = st.number_input(L["lbl_p3_ratio"], value=20.0)
                    d3 = st.date_input(f"3. {L['lbl_pay_date']}", value=datetime.date.today() + datetime.timedelta(days=60))
                with rc4:
                    r4 = st.number_input(L["lbl_p4_ratio"], value=20.0)
                    d4 = st.date_input(f"4. {L['lbl_pay_date']}", value=datetime.date.today() + datetime.timedelta(days=90))
                with rc5:
                    r5 = st.number_input(L["lbl_p5_ratio"], value=20.0)
                    d5 = st.date_input(f"5. {L['lbl_pay_date']}", value=datetime.date.today() + datetime.timedelta(days=120))

                p1_amt = total_amount * (r1 / 100.0)
                p2_amt = total_amount * (r2 / 100.0)
                p3_amt = total_amount * (r3 / 100.0)
                p4_amt = total_amount * (r4 / 100.0)
                p5_amt = total_amount * (r5 / 100.0)
                p1_date, p2_date, p3_date, p4_date, p5_date = str(d1), str(d2), str(d3), str(d4), str(d5)

            st.markdown("---")
            desc = st.text_area(L["col_desc"], placeholder="填寫工程設備細項...")
            progress = st.text_area(L["col_progress"], placeholder="填寫目前進行進度...")

            if st.form_submit_button(L["btn_save_new"], use_container_width=True):
                new_id = len(st.session_state.ar_projects_store) + 1
                st.session_state.ar_projects_store.append({
                    "id": new_id, "req_no": req_no, "customer": customer, "project": project,
                    "currency": currency, "total_amount": total_amount, "inst_type": inst_choice,
                    "p1_amt": p1_amt, "p1_date": p1_date,
                    "p2_amt": p2_amt, "p2_date": p2_date,
                    "p3_amt": p3_amt, "p3_date": p3_date,
                    "p4_amt": p4_amt, "p4_date": p4_date,
                    "p5_amt": p5_amt, "p5_date": p5_date,
                    "description": desc, "progress_log": progress
                })
                st.success(L["msg_success_add"])
                st.rerun()

    # ----------------------------------------------------
    # TAB 3: 修改與更新進行進度說明
    # ----------------------------------------------------
    with tab_update:
        st.subheader(L["tab_update"])
        
        if st.session_state.ar_projects_store:
            proj_options = {f"[{p['req_no']}] {p['customer']} - {p['project']}": idx for idx, p in enumerate(st.session_state.ar_projects_store)}
            sel_label = st.selectbox(L["col_project"], list(proj_options.keys()))
            target_idx = proj_options[sel_label]
            target_p = st.session_state.ar_projects_store[target_idx]

            with st.form("form_update_progress"):
                st.write(f"• **{L['col_customer']}**: {target_p['customer']}")
                st.write(f"• **{L['col_total']}**: `{format_currency_display(target_p['total_amount'], target_p['currency'])}`")
                
                new_desc = st.text_area(L["col_desc"], value=target_p["description"])
                new_progress = st.text_area(L["col_progress"], value=target_p["progress_log"])

                if st.form_submit_button(L["btn_save_progress"], use_container_width=True):
                    st.session_state.ar_projects_store[target_idx]["description"] = new_desc
                    st.session_state.ar_projects_store[target_idx]["progress_log"] = new_progress
                    st.success(L["msg_success_update"])
                    st.rerun()

    # TAB 4: 報價單參照
    with tab_quote:
        st.subheader(L["tab_quote"])
        st.code("""REETECH INDUSTRIAL - Quotation & Contract Reference""", language="text")

# 保持萬用傳參介面相容
def render_sales_order_ar_page(*args, **kwargs):
    render(*args, **kwargs)

def show(*args, **kwargs):
    render(*args, **kwargs)

def main(*args, **kwargs):
    render(*args, **kwargs)
