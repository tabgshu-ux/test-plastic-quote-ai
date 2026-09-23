import streamlit as st
import google.generativeai as genai
import os

def query_multinational_tax_ai(country, user_query):
    """呼叫 Gemini AI 進行多國稅務法規中文解析與解答"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key:
        return "⚠️ 未檢測到 GEMINI_API_KEY 環境變數。請在系統設定或 .env 中設定 API Key 以啟用全球稅務 AI 顧問。"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_prompt = f"""
你是一位精通全球跨國財會與稅務法規的資深國際稅務顧問（Specialized in Global Tax & Compliance）。
使用者目前的目標國家是：【{country}】。

請嚴格遵循以下規則回答使用者的財務/稅務問題：
1. **語言限制**：全程必須使用『繁體中文』回答，以便財務人員理解。
2. **結構化回答**：
   - 【結論/核心解答】：先給出明確、直接的財務操作建議。
   - 【詳細分析與處理方式】：分點說明進項抵扣、費用列支條件、扣繳稅率或申報流程。
   - 【該國法規依據 (Căn cứ pháp lý / Legal Reference)】：必須列出該國對應的官方法律、條例、通告或公文編號（如越南的 Thông tư, Nghị định、台灣的所得稅法條文等），並附上原文法規名稱與中文翻譯。
3. **專業態度**：立場嚴謹合規，若遇到涉及法律灰色地帶，請說明風險並建議備妥之憑證清單（發票、合約、簽收單等）。
"""

        full_prompt = f"{system_prompt}\n\n使用者財務問題：{user_query}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"❌ 呼叫 AI 稅務顧問時發生錯誤: {str(e)}"

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

def render_finance_tax_page():
    st.title("💰 財務與跨國稅務法規 AI 智慧系統 (Global Tax & Finance)")
    st.caption("專為跨國營運與外設廠企業設計，支援全球各國稅法中文智慧解答、合規憑證建議與扣繳稅試算。")

    tab_qa, tab_calc, tab_db = st.tabs([
        "🤖 全球稅務 AI 中文智慧問答", 
        "📊 跨境扣繳稅 (WHT/FCT) 試算器",
        "📖 各國核心稅法憑證檢核庫"
    ])

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

    with tab_calc:
        render_cross_border_wht_calculator()

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

def show(sub_option=None):
    render_finance_tax_page()

def main(sub_option=None):
    render_finance_tax_page()
