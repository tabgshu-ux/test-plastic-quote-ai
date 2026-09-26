import streamlit as st
import pandas as pd
from datetime import datetime, date

# ----------------------------------------------------
# 💱 跨國匯率參照字典 (以 USD 為基準換算)
# ----------------------------------------------------
EXCHANGE_RATES = {
    "VND (越南盾)": {"symbol": "₫", "to_usd": 0.0000393, "rate": 25420.0},
    "TWD (新台幣)": {"symbol": "NT$", "to_usd": 0.0314, "rate": 31.8},
    "RMB (人民幣)": {"symbol": "¥", "to_usd": 0.1398, "rate": 7.15},
    "USD (美金)": {"symbol": "$", "to_usd": 1.0, "rate": 1.0},
    "EUR (歐元)": {"symbol": "€", "to_usd": 1.087, "rate": 0.92}
}

def render_general_affairs_page(sub_option, lang):
    st.title(f"🏢 總務管理系統 — {sub_option}")
    st.caption("管理公司固定資產、總務採購、零用金支應、行政公文與線上多關卡簽核作業（支援多幣別）")

    # 防護 user_info，防止未登入時報錯
    user_info = st.session_state.get("user_info", {"name": "張總務", "role": "總務主管", "dept": "總務部"})

    # ----------------------------------------------------
    # 🗄️ 1. 初始化 Session State 模擬資料庫
    # ----------------------------------------------------
    # (1) 固定資產資料庫 (多幣別)
    if "ga_asset_data" not in st.session_state:
        st.session_state.ga_asset_data = [
            {
                "資產編號": "FA-2026-001",
                "資產名稱": "行政部公務車 Toyota",
                "資產類別": "運輸設備",
                "保管人": "總務部 李專員",
                "放置地點": "台北總部停車場",
                "購買日期": "2023-05-15",
                "預計報廢日期": "2030-05-14",
                "幣別": "TWD",
                "取得價值 (原幣)": 800000.0,
                "取得價值 (USD)": 25157.0,
                "狀態": "🟢 使用中"
            },
            {
                "資產編號": "FA-2026-002",
                "資產名稱": "會議室高畫質投影機",
                "資產類別": "辦公設備",
                "保管人": "資訊部",
                "放置地點": "大會議室",
                "購買日期": "2024-01-10",
                "預計報廢日期": "2027-01-09",
                "幣別": "USD",
                "取得價值 (原幣)": 1200.0,
                "取得價值 (USD)": 1200.0,
                "狀態": "🟢 使用中"
            }
        ]

    # (2) 採購請購單資料庫 (多幣別)
    if "ga_purchase_data" not in st.session_state:
        st.session_state.ga_purchase_data = [
            {"單號": "PO-20260901-01", "物品名稱": "A4 影印紙 (500張/包)", "分類": "辦公用品", "數量": 15, "幣別": "TWD", "預估金額 (原幣)": 2250.0, "預估金額 (USD)": 70.7, "狀態": "🟢 已核准", "申請人": "張小美"},
            {"單號": "PO-20260902-02", "物品名稱": "廠區清潔劑", "分類": "清潔用品", "數量": 40, "幣別": "VND", "預估金額 (原幣)": 2500000.0, "預估金額 (USD)": 98.25, "狀態": "🟢 已核准", "申請人": "李大同"}
        ]

    # (3) 零用金資料庫 (多幣別)
    if "ga_petty_cash_data" not in st.session_state:
        st.session_state.ga_petty_cash_data = [
            {"單號": "PC-20260901-01", "申請日期": "2026-09-01", "申請人": "李大同", "費用類別": "車馬費", "幣別": "VND", "金額 (原幣)": 1150000.0, "金額 (USD)": 45.2, "說明": "拜訪平陽客戶計程車費", "狀態": "🟢 已核銷"},
            {"單號": "PC-20260915-02", "申請日期": "2026-09-15", "申請人": "張小美", "費用類別": "快遞費", "幣別": "USD", "金額 (原幣)": 18.5, "金額 (USD)": 18.5, "說明": "寄送樣品至海外廠區", "狀態": "🟡 簽核中"}
        ]

    # (4) 行政公文與合同資料庫
    if "ga_contract_data" not in st.session_state:
        st.session_state.ga_contract_data = [
            {
                "合同/公文編號": "CTR-2026-001",
                "文件類別": "廠商合約",
                "標題/主題": "廠區保全安防維護合約",
                "簽約對象/單位": "中興保全",
                "簽署日期": "2026-01-01",
                "到期日期": "2026-12-31",
                "負責人": "李總務",
                "狀態": "🟢 有效中"
            }
        ]

    # (5) 簽核中心佇列資料庫 (Workflow Queue)
    if "approval_queue" not in st.session_state:
        st.session_state.approval_queue = [
            {
                "簽核單號": "APV-PC-20260915-02",
                "來源模組": "💵 零用金報銷",
                "申請人": "張小美",
                "申請項目": "寄送樣品至海外廠區 ($18.5 USD / 18.5 USD)",
                "申請日期": "2026-09-15",
                "當前關卡": "關卡 1：部門主管審核",
                "狀態": "🟡 待簽核",
                "簽核歷程": []
            }
        ]

    # ----------------------------------------------------
    # 📌 2. 總務用品採購與庫存管理 (含多幣別輸入)
    # ----------------------------------------------------
    if "總務用品" in sub_option or "Procurement" in sub_option or "Mua sắm" in sub_option:
        st.subheader("📦 總務用品採購與庫存管理")
        
        # 算式連動
        po_usd_total = sum(item.get("預估金額 (USD)", 0.0) for item in st.session_state.ga_purchase_data)
        col1, col2, col3 = st.columns(3)
        col1.metric("本月總務採購總額 (USD)", f"${po_usd_total:,.2f} USD")
        col2.metric("待簽核採購單", f"{sum(1 for i in st.session_state.approval_queue if '📦 總務用品採購' in i['來源模組'] and '待簽核' in i['狀態'])} 筆")
        col3.metric("品項庫存數量", f"{len(st.session_state.ga_purchase_data)} 項")

        st.markdown("#### 📋 採購需求與請購紀錄")
        st.dataframe(pd.DataFrame(st.session_state.ga_purchase_data), use_container_width=True)

        with st.expander("➕ 新建總務採購請購單 (支援當地幣別)", expanded=True):
            with st.form("ga_purchase_form", clear_on_submit=True):
                item_name = st.text_input("物品名稱 / Description", placeholder="例如：廠區清潔劑 / 影印紙")
                category = st.selectbox("物品分類", ["辦公用品", "清潔用品", "行政設備", "五金雜項", "其他"])
                
                col_qty, col_curr, col_price = st.columns([1, 1.5, 2])
                with col_qty:
                    qty = st.number_input("數量 / Quantity", min_value=1, value=10)
                with col_curr:
                    selected_curr = st.selectbox("結算幣別 / Currency", list(EXCHANGE_RATES.keys()), index=0)
                
                curr_info = EXCHANGE_RATES[selected_curr]
                curr_code = selected_curr.split()[0]
                curr_symbol = curr_info["symbol"]
                
                with col_price:
                    default_unit_price = 150000.0 if curr_code == "VND" else 100.0
                    unit_price = st.number_input(f"預估單價 ({curr_code})", min_value=0.0, value=default_unit_price, step=1000.0 if curr_code=="VND" else 1.0)

                dept = st.selectbox("費用歸屬部門", ["財務部", "總務部", "廠務部", "業務部", "生產一課"])
                
                # 動態金額小計
                total_local = qty * unit_price
                total_usd = total_local * curr_info["to_usd"]
                st.info(f"💰 報銷當地原幣小計：**{curr_symbol} {total_local:,.2f} {curr_code}** （折合美金約 **${total_usd:,.2f} USD**）")
                
                submit_po = st.form_submit_button("🚀 送出採購申請並發起簽核", type="primary")

                if submit_po and item_name:
                    po_id = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    new_po = {
                        "單號": po_id,
                        "物品名稱": item_name,
                        "分類": category,
                        "數量": qty,
                        "幣別": curr_code,
                        "預估金額 (原幣)": total_local,
                        "預估金額 (USD)": total_usd,
                        "狀態": "🟡 簽核中",
                        "申請人": user_info["name"]
                    }
                    st.session_state.ga_purchase_data.append(new_po)

                    # 同步推送到簽核佇列
                    st.session_state.approval_queue.append({
                        "簽核單號": f"APV-{po_id}",
                        "來源模組": "📦 總務用品採購",
                        "申請人": user_info["name"],
                        "申請項目": f"{item_name} x {qty} ({curr_symbol}{total_local:,.2f} {curr_code} / ${total_usd:,.2f} USD)",
                        "申請日期": str(date.today()),
                        "當前關卡": "關卡 1：總務主管審核",
                        "狀態": "🟡 待簽核",
                        "簽核歷程": []
                    })
                    st.success(f"✅ 成功送出採購申請！金額：{curr_symbol} {total_local:,.2f} {curr_code}，簽核單號：APV-{po_id}")
                    st.rerun()

    # ----------------------------------------------------
    # 🏢 3. 公司固定資產與設備管理 (含多幣別)
    # ----------------------------------------------------
    elif "固定資產" in sub_option or "Asset" in sub_option or "Tài sản" in sub_option:
        st.subheader("🏢 公司固定資產與辦公設備管理")

        assets = st.session_state.ga_asset_data
        total_assets = len(assets)
        total_val_usd = sum(a.get("取得價值 (USD)", 0.0) for a in assets)

        c1, c2, c3 = st.columns(3)
        c1.metric("列管固定資產總數", f"{total_assets} 件")
        c2.metric("資產原值總計 (USD)", f"${total_val_usd:,.2f} USD")
        c3.metric("保養維修中設備", f"{sum(1 for a in assets if '維修' in a['狀態'])} 件")

        # ➕ 新增固定資產
        with st.expander("➕ 登記新固定資產", expanded=True):
            with st.form("form_add_asset", clear_on_submit=True):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    asset_name = st.text_input("資產名稱", placeholder="例如：行政部公務車 / 辦公電腦")
                    category = st.selectbox("資產類別", ["辦公設備", "運輸設備", "資訊設備", "廠務設備", "其他資產"])
                    keeper = st.text_input("保管人 / 部門", value=user_info["name"])
                
                with col_b:
                    location = st.text_input("放置地點 / 廠區", placeholder="例如：台北總部 4F / 越南平陽廠")
                    purchase_date = st.date_input("購買日期", value=date.today())
                    scrap_date = st.date_input("預計報廢日期", value=date(date.today().year + 5, date.today().month, date.today().day))
                
                with col_c:
                    selected_curr = st.selectbox("購入幣別", list(EXCHANGE_RATES.keys()), index=0)
                    curr_info = EXCHANGE_RATES[selected_curr]
                    curr_code = selected_curr.split()[0]
                    val_local = st.number_input(f"取得價值 ({curr_code})", min_value=0.0, value=500.0, step=100.0)
                    status = st.selectbox("初始狀態", ["🟢 使用中", "🔧 維修中", "🟡 閒置中", "🔴 已報廢"])

                btn_add_asset = st.form_submit_button("📥 儲存資產資料", type="primary")

                if btn_add_asset:
                    if not asset_name:
                        st.error("❌ 請輸入資產名稱！")
                    else:
                        asset_id = f"FA-{purchase_date.strftime('%Y')}-{len(assets) + 1:03d}"
                        val_usd = val_local * curr_info["to_usd"]
                        new_asset = {
                            "資產編號": asset_id,
                            "資產名稱": asset_name,
                            "資產類別": category,
                            "保管人": keeper,
                            "放置地點": location,
                            "購買日期": str(purchase_date),
                            "預計報廢日期": str(scrap_date),
                            "幣別": curr_code,
                            "取得價值 (原幣)": val_local,
                            "取得價值 (USD)": val_usd,
                            "狀態": status
                        }
                        st.session_state.ga_asset_data.append(new_asset)
                        st.success(f"✅ 成功新增資產！資產編號：{asset_id}")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📋 固定資產與設備列管清單")
        if st.session_state.ga_asset_data:
            st.dataframe(pd.DataFrame(st.session_state.ga_asset_data), use_container_width=True)

            with st.expander("🗑️ 刪除或報廢特定固定資產"):
                col_del_1, col_del_2 = st.columns([3, 1])
                with col_del_1:
                    asset_ids = [a["資產編號"] + " - " + a["資產名稱"] for a in st.session_state.ga_asset_data]
                    selected_asset_str = st.selectbox("請選擇欲刪除的資產：", asset_ids, key="sb_del_asset")
                    selected_asset_id = selected_asset_str.split(" - ")[0]
                
                with col_del_2:
                    st.write("")
                    st.write("")
                    if st.button("❌ 刪除此資產", type="secondary", key="btn_del_asset"):
                        st.session_state.ga_asset_data = [
                            a for a in st.session_state.ga_asset_data if a["資產編號"] != selected_asset_id
                        ]
                        st.success(f"已成功刪除資產：{selected_asset_id}")
                        st.rerun()

    # ----------------------------------------------------
    # 💵 4. 零用金與行政費用申請 (含多幣別與自動發起簽核)
    # ----------------------------------------------------
    elif "零用金" in sub_option or "Petty Cash" in sub_option or "Tiền mặt" in sub_option:
        st.subheader("💵 零用金與行政費用報銷")
        st.info("💡 提供總務人員登記日常小額零用金支出，可直接選擇越南盾(VND)、新台幣(TWD)等當地貨幣。")

        # ➕ 新增零用金申請
        with st.expander("➕ 新增零用金/費用報銷申請", expanded=True):
            with st.form("form_add_petty_cash", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    applicant = st.text_input("申請人姓名", value=user_info["name"])
                    exp_type = st.selectbox("費用類別", ["車馬費", "快遞費", "餐費", "雜項辦公採購", "其他"])
                with c2:
                    exp_date = st.date_input("申請日期", value=date.today())
                    selected_curr = st.selectbox("報銷幣別", list(EXCHANGE_RATES.keys()), index=0)
                
                curr_info = EXCHANGE_RATES[selected_curr]
                curr_code = selected_curr.split()[0]
                curr_symbol = curr_info["symbol"]

                with c3:
                    default_amount = 500000.0 if curr_code == "VND" else 50.0
                    amount_local = st.number_input(f"報銷金額 ({curr_code})", min_value=0.1, value=default_amount, step=1000.0 if curr_code=="VND" else 5.0)
                    desc = st.text_input("費用用途/說明", placeholder="請填寫費用事由與發票資訊...")

                amount_usd = amount_local * curr_info["to_usd"]
                st.caption(f"💰 折合美金約：`${amount_usd:,.2f} USD`")

                submit_btn = st.form_submit_button("📤 提交報銷申請並發起簽核", type="primary")

                if submit_btn:
                    new_id = f"PC-{exp_date.strftime('%Y%m%d')}-{len(st.session_state.ga_petty_cash_data) + 1:02d}"
                    new_item = {
                        "單號": new_id,
                        "申請日期": str(exp_date),
                        "申請人": applicant,
                        "費用類別": exp_type,
                        "幣別": curr_code,
                        "金額 (原幣)": amount_local,
                        "金額 (USD)": amount_usd,
                        "說明": desc,
                        "狀態": "🟡 簽核中"
                    }
                    st.session_state.ga_petty_cash_data.append(new_item)

                    # 發起簽核流程
                    st.session_state.approval_queue.append({
                        "簽核單號": f"APV-{new_id}",
                        "來源模組": "💵 零用金報銷",
                        "申請人": applicant,
                        "申請項目": f"{exp_type} - {desc} ({curr_symbol}{amount_local:,.2f} {curr_code} / ${amount_usd:,.2f} USD)",
                        "申請日期": str(exp_date),
                        "當前關卡": "關卡 1：主管審核",
                        "狀態": "🟡 待簽核",
                        "簽核歷程": []
                    })

                    st.success(f"✅ 成功建立申請單！單號：{new_id}，已發起簽核單號：APV-{new_id}")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 📋 歷史零用金報銷紀錄")
        if st.session_state.ga_petty_cash_data:
            st.dataframe(pd.DataFrame(st.session_state.ga_petty_cash_data), use_container_width=True)

            with st.expander("🗑️ 刪除或管理特定單據"):
                col_del_1, col_del_2 = st.columns([3, 1])
                with col_del_1:
                    item_ids = [item["單號"] for item in st.session_state.ga_petty_cash_data]
                    selected_id = st.selectbox("請選擇欲處理的單號：", item_ids, key="sb_del_pc")
                
                with col_del_2:
                    st.write("")
                    st.write("")
                    if st.button("❌ 刪除此單據", type="secondary", key="btn_del_pc"):
                        st.session_state.ga_petty_cash_data = [
                            item for item in st.session_state.ga_petty_cash_data if item["單號"] != selected_id
                        ]
                        st.success(f"已成功刪除單據：{selected_id}")
                        st.rerun()

    # ----------------------------------------------------
    # 📄 5. 行政公文與合同管理
    # ----------------------------------------------------
    elif "公文" in sub_option or "合同" in sub_option or "Contracts" in sub_option:
        st.subheader("📄 行政公文與合同管理")

        contracts = st.session_state.ga_contract_data
        total_cnt = len(contracts)
        expiring_cnt = sum(1 for c in contracts if "即將到期" in c["狀態"])

        c1, c2, c3 = st.columns(3)
        c1.metric("總列管合同/公文數", f"{total_cnt} 件")
        c2.metric("30天內即將到期", f"{expiring_cnt} 件", delta_color="inverse")
        c3.metric("系統告警狀態", "🟢 正常" if expiring_cnt == 0 else "⚠️ 需注意到期日")

        # ➕ 新增合同/公文
        with st.expander("➕ 登記新合同 / 行政公文", expanded=True):
            with st.form("form_add_contract", clear_on_submit=True):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    doc_type = st.selectbox("文件類別", ["廠商合約", "廠房租約", "行政公文", "保密協議 (NDA)", "其他合同"])
                    title = st.text_input("合同/公文名稱", placeholder="例如：越南廠區設備維修合約")
                    owner = st.text_input("內部負責人", value=user_info["name"])
                with col_b:
                    partner = st.text_input("對外簽約單位/發文機關", placeholder="例如：OO科技股份有限公司")
                    sign_date = st.date_input("簽署/發文日期", value=date.today())
                with col_c:
                    end_date = st.date_input("合約到期日", value=date(2027, 12, 31))

                btn_add_doc = st.form_submit_button("📥 儲存並建立文件檔案", type="primary")

                if btn_add_doc:
                    if not title or not partner:
                        st.error("❌ 請填寫合同名稱與簽約單位！")
                    else:
                        prefix = "CTR" if "合約" in doc_type or "租約" in doc_type or "協議" in doc_type else "DOC"
                        doc_id = f"{prefix}-{sign_date.strftime('%Y')}-{len(contracts) + 1:03d}"
                        
                        days_left = (end_date - date.today()).days
                        if days_left < 0:
                            status = "🔴 已過期"
                        elif days_left <= 30:
                            status = "⚠️ 即將到期"
                        else:
                            status = "🟢 有效中"

                        new_doc = {
                            "合同/公文編號": doc_id,
                            "文件類別": doc_type,
                            "標題/主題": title,
                            "簽約對象/單位": partner,
                            "簽署日期": str(sign_date),
                            "到期日期": str(end_date),
                            "負責人": owner,
                            "狀態": status
                        }
                        st.session_state.ga_contract_data.append(new_doc)
                        st.success(f"✅ 成功新增文件！文件編號：{doc_id}")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📋 合同與行政公文列管清單")
        if st.session_state.ga_contract_data:
            st.dataframe(pd.DataFrame(st.session_state.ga_contract_data), use_container_width=True)

            with st.expander("🗑️ 刪除或結案特定合同/公文"):
                col_del_1, col_del_2 = st.columns([3, 1])
                with col_del_1:
                    doc_ids = [c["合同/公文編號"] + " - " + c["標題/主題"] for c in st.session_state.ga_contract_data]
                    selected_doc_str = st.selectbox("請選擇欲刪除的文件：", doc_ids, key="sb_del_doc")
                    selected_doc_id = selected_doc_str.split(" - ")[0]
                
                with col_del_2:
                    st.write("")
                    st.write("")
                    if st.button("❌ 刪除此文件", type="secondary", key="btn_del_doc"):
                        st.session_state.ga_contract_data = [
                            c for c in st.session_state.ga_contract_data if c["合同/公文編號"] != selected_doc_id
                        ]
                        st.success(f"已成功刪除文件：{selected_doc_id}")
                        st.rerun()

    # ----------------------------------------------------
    # 📑 6. 總務與簽核審核中心 (電子簽核 Workflow — 修正點擊無反應問題)
    # ----------------------------------------------------
    else:
        st.subheader("📑 總務與簽核審核中心")
        st.info("💡 跨部門電子簽核關卡、待辦單據審核與簽核歷史歷程。")

        queue = st.session_state.approval_queue

        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric("⌛ 待審核單據總數", f"{sum(1 for i in queue if '待簽核' in i['狀態'])} 筆")
        col_kpi2.metric("🟢 已核准單據", f"{sum(1 for i in queue if '已核准' in i['狀態'])} 筆")
        col_kpi3.metric("🔴 已駁回單據", f"{sum(1 for i in queue if '已駁回' in i['狀態'])} 筆")

        st.markdown("---")
        st.markdown("### 📥 待審核單據列表")

        pending_indices = [i for i, item in enumerate(queue) if "待簽核" in item["狀態"]]

        if pending_indices:
            for idx_pos, q_idx in enumerate(pending_indices):
                item = queue[q_idx]
                with st.expander(f"📄 [{item['簽核單號']}] {item['來源模組']} — {item['申請項目']} (申請人: {item['申請人']})", expanded=(idx_pos==0)):
                    c_a, c_b = st.columns(2)
                    with c_a:
                        st.write(f"**申請日期：** {item['申請日期']}")
                        st.write(f"**來源模組：** {item['來源模組']}")
                        st.write(f"**當前審核關卡：** `{item['當前關卡']}`")
                    with c_b:
                        st.write(f"**申請人：** {item['申請人']}")
                        st.write(f"**申請詳情：** {item['申請項目']}")

                    if item.get("簽核歷程"):
                        st.markdown("**📜 歷史簽核紀錄：**")
                        for log in item["簽核歷程"]:
                            st.caption(f"• {log['時間']} | {log['簽核人']} : {log['動作']} — 意見: {log['意見']}")

                    st.markdown("---")
                    
                    # ✍️ 執行簽核動作 (獨立 form 鍵值防衝突)
                    form_key = f"form_approval_{item['簽核單號']}_{q_idx}"
                    with st.form(form_key):
                        user_role = user_info.get("role", "審核主管")
                        user_name = user_info.get("name", "張總務")
                        
                        st.write(f"**當前簽核執行人：** {user_name} ({user_role})")
                        comment = st.text_input("審核意見 / 備註", placeholder="請輸入同意或駁回之原因...", key=f"comment_{form_key}")
                        
                        btn_c1, btn_c2, _ = st.columns([1, 1, 2])
                        with btn_c1:
                            btn_approve = st.form_submit_button("🟢 同意 (Approve)", type="primary")
                        with btn_c2:
                            btn_reject = st.form_submit_button("🔴 駁回 (Reject)")

                        if btn_approve:
                            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                            # 直接更新 Session State 中的原始字典
                            st.session_state.approval_queue[q_idx]["簽核歷程"].append({
                                "簽核人": f"{user_name} ({user_role})",
                                "動作": "🟢 同意",
                                "時間": now_str,
                                "意見": comment if comment else "同意辦理"
                            })
                            st.session_state.approval_queue[q_idx]["狀態"] = "🟢 已核准"
                            
                            target_apv_id = item["簽核單號"]
                            # 連動更新零用金與採購單狀態
                            for pc in st.session_state.ga_petty_cash_data:
                                if f"APV-{pc['單號']}" == target_apv_id:
                                    pc['狀態'] = "🟢 已核銷"

                            for po in st.session_state.ga_purchase_data:
                                if f"APV-{po['單號']}" == target_apv_id:
                                    po['狀態'] = "🟢 已核准"

                            st.success(f"✅ 單號 {target_apv_id} 已順利核准！")
                            st.rerun()

                        if btn_reject:
                            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.session_state.approval_queue[q_idx]["簽核歷程"].append({
                                "簽核人": f"{user_name} ({user_role})",
                                "動作": "🔴 駁回",
                                "時間": now_str,
                                "意見": comment if comment else "退回重審"
                            })
                            st.session_state.approval_queue[q_idx]["狀態"] = "🔴 已駁回"

                            target_apv_id = item["簽核單號"]
                            for pc in st.session_state.ga_petty_cash_data:
                                if f"APV-{pc['單號']}" == target_apv_id:
                                    pc['狀態'] = "🔴 已駁回"

                            for po in st.session_state.ga_purchase_data:
                                if f"APV-{po['單號']}" == target_apv_id:
                                    po['狀態'] = "🔴 已駁回"

                            st.error(f"❌ 單號 {target_apv_id} 已駁回！")
                            st.rerun()
        else:
            st.success("🎉 目前沒有任何待您審核的單據！")

        st.markdown("---")
        st.markdown("### 📜 全系統歷史簽核總覽")
        if st.session_state.approval_queue:
            st.dataframe(pd.DataFrame(st.session_state.approval_queue), use_container_width=True)
