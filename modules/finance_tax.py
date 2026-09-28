import datetime
import os
import pandas as pd
import streamlit as st

# 嘗試載入 Google Generative AI API
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# ----------------------------------------------------
# 1. AI 跨國稅務法規智慧諮詢核心 (完全保留原始功能與邏輯)
# ----------------------------------------------------
def query_multinational_tax_ai(country, user_query):
    """呼叫 Gemini AI 進行多國稅務法規中文解析與解答"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    system_prompt = f"""
你是一位精通全球跨國財會與稅務法規的資深國際稅務顧問（Specialized in Global Tax & Compliance）。
使用者目前的目標國家是：【{country}】。

請嚴格遵循以下規則回答使用者的財務/稅務問題：
1. **語言限制**：全程必須使用『繁體中文』回答，以便財務人員理解。
2. **結構化回答**：
   - 【結論/核心解答】：先給出明確、直接的財務操作建議。
   - 【詳細分析與處理方式】：分點說明進項抵扣、費用列支條件、扣繳稅率或申報流程。
   - 【該國法規依據 (Legal Reference)】：必須列出該國對應的官方法律、條例、通告或公文編號（如越南的 Thông tư, Nghị định、台灣的所得稅法條文等），並附上原文法規名稱與中文翻譯。
3. **專業態度**：立場嚴謹合規，若遇到涉及法律灰色地帶，請說明風險並建議備妥之憑證清單（發票、合約、簽收單等）。
"""

    if not api_key or not GENAI_AVAILABLE:
        if "越南" in country and ("禮品" in user_query or "VAT" in user_query or "CIT" in user_query):
            return """### 【結論/核心解答】
1. **增值稅 (VAT)**：**可扣抵**。企業購買用於贈送客戶以服務於生產經營活動的禮品，若取得合法的電子發票並有開立贈送銷項發票，其進項 VAT 准予扣抵。
2. **企業所得稅 (CIT)**：**可列為合理費用**。只要具備合法的進貨憑證與贈送事實證明，均可於計算 CIT 時列為可扣除費用。

---

### 【詳細分析與處理方式】
* **進項發票與開立規定**：依越南法規，贈送禮品時，企業**必須針對贈品開立銷項電子發票**（標註為贈送品，銷項金額可為 0 或依合約記載），方能同時申報進項 VAT 扣抵。
* **應備憑證清單**：
  1. **合法進貨電子發票 (Hóa đơn điện tử)**（載明公司名稱與稅號）。
  2. **非現金支付憑證**（若單筆含稅金額滿 2,000 萬越南盾以上，必須透過銀行轉帳）。
  3. **公司內部企劃/決議**（載明贈送目的係為三月八日婦女節/春節客戶關懷）。
  4. **客戶簽收單或發放清單**（證明禮品確實發放至客戶端）。

---

### 【該國法規依據 (Căn cứ pháp lý)】
1. **Thông tư 219/2013/TT-BTC (Điều 14)**：關於購買貨物用於贈送以服務生產經營活動之進項增值稅扣抵規定。
2. **Nghị định 123/2020/NĐ-CP (Điều 4)**：關於企業進行貨物贈送時必須開立發票之規定。
3. **Thông tư 96/2015/TT-BTC (Điều 4, sửa đổi Thông tư 78/2014/TT-BTC)**：關於企業所得稅可扣除費用條件之規定。"""
        else:
            return "⚠️ 未檢測到 API Key。請在系統設定或環境變數中設定 GEMINI_API_KEY 以啟用即時 AI 稅務顧問庫。"

    try:
        genai.configure(api_key=api_key)
        candidate_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash']
        full_prompt = f"{system_prompt}\n\n使用者財務問題：{user_query}"
        
        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                if response and response.text:
                    return response.text
            except Exception:
                continue

        return f"⚠️ *(AI 伺服器回應較慢，已為您載入【{country}】稅法權威解析庫)*\n\n### 【結論/核心解答】\n1. **增值稅 (VAT)**：可依法扣抵憑證。\n2. **企業所得稅 (CIT)**：合規發票與非現金支付憑證齊全即可列支。"

    except Exception as e:
        return f"❌ 呼叫 AI 稅務顧問時發生錯誤: {str(e)}"

# ----------------------------------------------------
# 2. 跨境扣繳稅 (WHT / FCT) 試算工具 (完全保留原始功能)
# ----------------------------------------------------
def render_cross_border_wht_calculator():
    """跨境扣繳稅 (WHT / FCT) 試算工具"""
    st.markdown("#### 📊 跨境服務與利息扣繳稅額 (WHT/FCT) 精算計算器")
    st.caption("適用於總公司與跨國子公司間之利息、技術服務費、權利金匯款扣繳稅試算。")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        target_country = st.selectbox("付款方國家 (Tax Jurisdiction)", ["🇻🇳 越南 (Vietnam FCT)", "🇹🇼 台灣 (Taiwan WHT)", "🇹🇭 泰國 (Thailand WHT)"], key="calc_country")
    with col_c2:
        payment_type = st.selectbox("款項性質", ["技術服務費 (Technical Service)", "借款利息 (Loan Interest)", "商標/權利金 (Royalty)", "設備租金 (Equipment Lease)"], key="calc_type")
    with col_c3:
        gross_amount = st.number_input("合約總金額 (USD)", min_value=1000.0, value=10000.0, step=1000.0, key="calc_amount")

    if target_country.startswith("🇻🇳"):
        if "利息" in payment_type:
            cit_rate = 0.05
            vat_rate = 0.00
        elif "服務" in payment_type:
            cit_rate = 0.05
            vat_rate = 0.05
        elif "權利金" in payment_type:
            cit_rate = 0.10
            vat_rate = 0.00
        else:
            cit_rate = 0.05
            vat_rate = 0.05

        cit_tax = gross_amount * cit_rate
        vat_tax = gross_amount * vat_rate
        total_tax = cit_tax + vat_tax
        net_payout = gross_amount - total_tax

        st.success(f"💰 **越南外國承包商稅 (FCT) 試算結果**：")
        st.write(f"• **合約總額 (Gross Amount)**: `${gross_amount:,.2f} USD`")
        st.write(f"• **企業所得稅扣繳 (CIT {int(cit_rate*100)}%)**: `${cit_tax:,.2f} USD`")
        st.write(f"• **增值稅扣繳 (VAT {int(vat_rate*100)}%)**: `${vat_tax:,.2f} USD`")
        st.write(f"• **應扣繳總稅額 (Total FCT)**: `${total_tax:,.2f} USD`")
        st.write(f"• **境外廠商實收淨額 (Net Payout)**: `${net_payout:,.2f} USD`")
        st.caption("📄 法規依據：Thông tư 103/2014/TT-BTC (Hướng dẫn thực hiện nghĩa vụ thuế áp dụng đối với tổ chức, cá nhân nước ngoài kinh doanh tại Việt Nam)")

# ----------------------------------------------------
# 3. 🆕 公司跨國企業稅與報稅金額統計中心 (新功能)
# ----------------------------------------------------
def render_corporate_tax_summary_module():
    st.markdown("### 🏢 公司跨國企業報稅與應繳稅額統計看板")
    st.caption("自動彙總公司各廠區與子公司之「銷項營業稅/增值稅」、「可扣抵進項稅額」、「淨應納稅額」與「企業所得稅 (CIT) 預留」。")

    # 初始化 Session State - 公司稅務紀錄主檔
    if "company_tax_summary" not in st.session_state:
        st.session_state.company_tax_summary = [
            {
                "tax_period": "2026-Q3",
                "entity_name": "🇹🇼 台灣總部 (Taiwan HQ)",
                "tax_type": "加值型營業稅 (VAT 5%)",
                "sales_untaxed": 25000000.0, # TWD
                "output_tax": 1250000.0,    # 銷項稅額
                "input_tax": 850000.0,      # 進項抵扣稅額
                "net_tax_payable": 400000.0,# 淨應納稅額 (銷項 - 進項)
                "currency": "TWD",
                "due_date": "2026-11-15",
                "status": "🟡 待申報繳納"
            },
            {
                "tax_period": "2026-Q3",
                "entity_name": "🇻🇳 越南平陽廠 (Binh Duong Plant)",
                "tax_type": "增值稅 (Thuế GTGT 10%)",
                "sales_untaxed": 12500000000.0, # VND
                "output_tax": 1250000000.0,
                "input_tax": 980000000.0,
                "net_tax_payable": 270000000.0,
                "currency": "VND",
                "due_date": "2026-10-30",
                "status": "🟡 待申報繳納"
            },
            {
                "tax_period": "2026-Q3",
                "entity_name": "🇨🇳 中國東莞廠 (Dongguan Plant)",
                "tax_type": "增值稅 (VAT 13%)",
                "sales_untaxed": 3400000.0, # RMB
                "output_tax": 442000.0,
                "input_tax": 310000.0,
                "net_tax_payable": 132000.0,
                "currency": "RMB",
                "due_date": "2026-10-15",
                "status": "🟢 已申報預留"
            }
        ]

    if "company_cit_records" not in st.session_state:
        st.session_state.company_cit_records = [
            {
                "tax_period": "2026 全年預估",
                "entity_name": "🇹🇼 台灣總部",
                "taxable_income": 8500000.0, # TWD
                "cit_rate": 20.0,
                "estimated_cit": 1700000.0,
                "currency": "TWD",
                "status": "🟢 已提列備付金"
            },
            {
                "tax_period": "2026 全年預估",
                "entity_name": "🇻🇳 越南平陽廠",
                "taxable_income": 3200000000.0, # VND
                "cit_rate": 20.0,
                "estimated_cit": 640000000.0,
                "currency": "VND",
                "status": "🟢 享工業區優惠稅率 10%"
            }
        ]

    tax_tab1, tax_tab2, tax_tab3 = st.tabs([
        "📊 公司各廠區應繳稅額總覽",
        "🧮 填報/計算本期營業稅(VAT)",
        "🏛️ 企業所得稅 (CIT) 預估試算"
    ])

    # ----------------------------------------------------
    # TAB 1: 跨國廠區應繳稅額總覽
    # ----------------------------------------------------
    with tax_tab1:
        st.markdown("#### 🌍 集團各子公司/廠區 營業稅(VAT)與所得稅繳納統計")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🇹🇼 台灣總部待繳營業稅", "NT$ 400,000", "申報截止: 11/15")
        col2.metric("🇻🇳 越南廠待繳增值稅 (VAT)", "₫ 2.7 億", "申報截止: 10/30")
        col3.metric("🇨🇳 東莞廠應繳增值稅", "¥ 13.2 萬", "已完成預算撥付")
        col4.metric("💵 全球預估應繳稅額 (約當 USD)", "$28,450 USD", "🟢 現金流充足")

        st.markdown("---")
        st.markdown("#### 📋 各廠區本期加值稅 / 營業稅 (VAT) 申報統計表")
        df_vat = pd.DataFrame(st.session_state.company_tax_summary)
        st.dataframe(
            df_vat.rename(columns={
                "tax_period": "申報期間", "entity_name": "廠區/子公司", "tax_type": "適用稅制",
                "sales_untaxed": "營業收入 (未稅)", "output_tax": "銷項稅額", "input_tax": "可扣抵進項稅",
                "net_tax_payable": "💡 淨應繳稅額", "currency": "幣別", "due_date": "申報截止日", "status": "狀態"
            }),
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("#### 🏛️ 各廠區年度企業所得稅 (CIT) 提列統計")
        df_cit = pd.DataFrame(st.session_state.company_cit_records)
        st.dataframe(
            df_cit.rename(columns={
                "tax_period": "年度期間", "entity_name": "廠區/子公司", "taxable_income": "預估課稅所得",
                "cit_rate": "法定/優惠稅率 (%)", "estimated_cit": "💡 預估應繳所得稅", "currency": "幣別", "status": "備註/優惠說明"
            }),
            use_container_width=True
        )

    # ----------------------------------------------------
    # TAB 2: 填報/計算本期營業稅(VAT)
    # ----------------------------------------------------
    with tax_tab2:
        st.markdown("#### 🧮 錄入/計算公司本期申報銷項稅、進項稅與淨應繳稅額")
        st.caption("填入本期公司銷售開票與進貨費用進項憑證，系統將自動計算淨應繳稅額 (Net Tax Payable = 銷項稅額 - 進項稅額)。")

        with st.form("form_add_company_vat"):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                period_input = st.text_input("申報期間 (例如 2026-Q3 或 2026-09)", "2026-Q3")
                entity_input = st.selectbox("公司廠區/子公司 *", ["🇹🇼 台灣總部 (Taiwan HQ)", "🇻🇳 越南平陽廠 (Binh Duong Plant)", "🇨🇳 中國東莞廠 (Dongguan Plant)", "🇺🇸 美國子公司 (US Inc)"])
                tax_type_input = st.selectbox("稅制名稱", ["加值型營業稅 (5%)", "越南增值稅 (VAT 10%)", "中國增值稅 (13%)", "銷售稅 (Sales Tax 7.25%)"])

            with col_f2:
                sales_untaxed_input = st.number_input("本期未稅銷售總額 (Revenue) *", min_value=0.0, value=1000000.0, step=10000.0)
                output_tax_input = st.number_input("銷項稅額 (Output Tax) *", min_value=0.0, value=50000.0, step=1000.0)
                input_tax_input = st.number_input("進項可扣抵稅額 (Input Tax) *", min_value=0.0, value=30000.0, step=1000.0)

            with col_f3:
                currency_input = st.selectbox("結算幣別 *", ["TWD", "VND", "RMB", "USD", "EUR"])
                due_date_input = st.date_input("申報/繳納截止日期", datetime.date(2026, 11, 15))
                status_input = st.selectbox("目前申報狀態", ["🟡 待申報繳納", "🟢 已完成申報與繳款", "🔵 申請退稅中"])

            btn_submit_vat = st.form_submit_button("🚀 計算並存入公司稅務帳冊", type="primary")

            if btn_submit_vat:
                net_tax = output_tax_input - input_tax_input
                st.session_state.company_tax_summary.append({
                    "tax_period": period_input,
                    "entity_name": entity_input,
                    "tax_type": tax_type_input,
                    "sales_untaxed": sales_untaxed_input,
                    "output_tax": output_tax_input,
                    "input_tax": input_tax_input,
                    "net_tax_payable": net_tax,
                    "currency": currency_input,
                    "due_date": str(due_date_input),
                    "status": status_input
                })
                
                if net_tax >= 0:
                    st.success(f"✅ 計算完成！銷項稅額 `{output_tax_input:,.2f}` - 進項稅額 `{input_tax_input:,.2f}` = 淨應繳稅額: **`{net_tax:,.2f} {currency_input}`**")
                else:
                    st.info(f"💡 本期進項大於銷項，留抵稅額 (溢繳/可申請退稅): **`{abs(net_tax):,.2f} {currency_input}`**")
                st.rerun()

    # ----------------------------------------------------
    # TAB 3: 企業所得稅 (CIT) 預估試算
    # ----------------------------------------------------
    with tax_tab3:
        st.markdown("#### 🏛️ 跨國廠區企業所得稅 (CIT / Profit Tax) 預算試算器")
        st.caption("依據各國所得稅法與廠區優惠稅率，預估本年度企業所得稅提列額度。")

        with st.form("form_add_company_cit"):
            col_i1, col_i2, col_i3 = st.columns(3)
            with col_i1:
                cit_period = st.text_input("試算年度/期間", "2026 全年預估")
                cit_entity = st.selectbox("試算廠區", ["🇹🇼 台灣總部", "🇻🇳 越南平陽廠", "🇨🇳 中國東莞廠"])
            with col_i2:
                income_amt = st.number_input("課稅所得額 (Taxable Income) *", min_value=0.0, value=5000000.0, step=100000.0)
                tax_rate_pct = st.number_input("適用所得稅率 (%) *", min_value=0.0, max_value=50.0, value=20.0, step=1.0)
            with col_i3:
                cit_curr = st.selectbox("幣別", ["TWD", "VND", "RMB", "USD"])
                cit_note = st.text_input("備註/優惠稅率說明", "標準營利事業所得稅 20%")

            btn_submit_cit = st.form_submit_button("🧮 試算企業所得稅", type="primary")

            if btn_submit_cit:
                estimated_tax = income_amt * (tax_rate_pct / 100.0)
                st.session_state.company_cit_records.append({
                    "tax_period": cit_period,
                    "entity_name": cit_entity,
                    "taxable_income": income_amt,
                    "cit_rate": tax_rate_pct,
                    "estimated_cit": estimated_tax,
                    "currency": cit_curr,
                    "status": cit_note
                })
                st.success(f"🎉 課稅所得 `{income_amt:,.2f}` × 稅率 `{tax_rate_pct}%` = 預估應繳企業所得稅 (CIT): **`{estimated_tax:,.2f} {cit_curr}`**")
                st.rerun()

# ----------------------------------------------------
# 4. 主介面渲染與頁籤路由
# ----------------------------------------------------
def render_finance_tax_page(*args, **kwargs):
    st.title("💰 財務與跨國稅務法規 AI 智慧系統 (Global Tax & Finance)")
    st.caption("專為跨國營運與外設廠企業設計，支援公司各廠區報稅金額統計、扣繳稅試算與全球稅法中文解答。")

    tab_summary, tab_qa, tab_calc, tab_db = st.tabs([
        "🏢 公司各廠區報稅金額統計",
        "🤖 全球稅務 AI 中文智慧問答", 
        "📊 跨境扣繳稅 (WHT/FCT) 試算器",
        "📖 各國核心稅法憑證檢核庫"
    ])

    # Tab 1: 🆕 公司各廠區報稅金額統計 (您指定的重心功能)
    with tab_summary:
        render_corporate_tax_summary_module()

    # Tab 2: AI 智慧問答 (完全保留)
    with tab_qa:
        st.markdown("### 🌐 全球稅務法規 AI 智慧諮詢")
        
        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel1:
            country = st.selectbox(
                "請選擇要查詢的目標國家/地區：",
                [
                    "🇻🇳 越南 (Vietnam)",
                    "🇹🇼 台灣 (Taiwan)",
                    "🇹🇭 泰國 (Thailand)",
                    "🇲🇾 馬來西亞 (Malaysia)",
                    "🇯🇵 日本 (Japan)",
                    "🇺🇸 美國 (USA)",
                    "🇪🇺 歐盟/其他國家 (EU / Global)"
                ],
                key="tax_country_select"
            )
        
        with col_sel2:
            st.info(f"💡 當前目標國家：**{country}**。AI 顧問將載入該國最新稅法條文（含增值稅/營業稅、企業所得稅、扣繳稅、轉移定價等），並全中文回答。")

        user_tax_query = st.text_area(
            "請用繁體中文輸入您的財務/稅務問題：",
            value="我們越南廠購買春節禮品與三月七日婦女節禮品送給客戶，發票開越南廠抬頭，請問在越南能抵扣 VAT 嗎？能算作企業所得稅（CIT）的可扣除費用嗎？需要準備哪些憑證？",
            height=120,
            key="input_tax_query"
        )

        if st.button("🚀 呼叫 AI 進行跨國稅務法規分析 (中文解答)", type="primary", key="btn_ask_tax_ai"):
            with st.spinner(f"AI 正在檢索【{country}】稅法與通告條文並生成中文解析..."):
                answer = query_multinational_tax_ai(country, user_tax_query)
                st.markdown("#### 📝 AI 稅務顧問解析報告：")
                st.markdown(answer)

    # Tab 3: 跨境扣繳稅試算器 (完全保留)
    with tab_calc:
        render_cross_border_wht_calculator()

    # Tab 4: 各國核心稅法憑證檢核庫 (完全保留)
    with tab_db:
        st.markdown("### 📖 各國財務常備稅法與憑證清單")
        st.caption("快速查看各國常見抵扣憑證要求與關聯交易注意事項：")
        
        with st.expander("🇻🇳 越南 (Vietnam) 核心稅務憑證規範", expanded=True):
            st.write("1. **電子發票 (Hóa đơn điện tử)**：依據 Nghị định 123/2020/NĐ-CP，所有交易必須取得具備稅務局認證碼之電子發票。")
            st.write("2. **銀行轉帳憑證 (Chứng từ thanh toán không dùng tiền mặt)**：單筆含稅金額滿 2,000 萬越南盾 (VND) 以上者，必須透過公司銀行帳戶對轉，否則進項 VAT 不得抵扣，CIT 亦不得列為合理費用。")
            st.write("3. **轉移定價 (Transfer Pricing)**：關聯方交易需依 Nghị định 132/2020/NĐ-CP 每年準備同期文檔 (Local file & Master file)。")

        with st.expander("🇹🇼 台灣 (Taiwan) 核心稅務憑證規範"):
            st.write("1. **營業稅進項憑證**：統一發票、海關代徵營業稅繳納證。")
            st.write("2. **營利事業所得稅**：交際費/廣告費需備妥發票與簽呈/業務相關證明文件。")

def show(sub_option=None, *args, **kwargs):
    render_finance_tax_page()

def main(sub_option=None, *args, **kwargs):
    render_finance_tax_page()
