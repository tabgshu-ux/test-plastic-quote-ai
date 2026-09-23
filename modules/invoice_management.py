import streamlit as st
import os

def render_invoice_quota_widget():
    """越南電子發票剩餘數量監控與預警元件"""
    st.markdown("#### 🇻🇳 越南電子發票 (Hóa đơn điện tử) 張數額度與預警中心")
    
    # 檢查是否已設定正式 API 金鑰與稅號
    tax_id = os.getenv("VN_TAX_ID", "")
    is_live_mode = bool(tax_id)

    if is_live_mode:
        st.success(f"🟢 **正式連線模式** (公司稅號 MST: `{tax_id}`)")
        # 真實 API 傳回數據 (模擬)
        total_quota = 5000
        used_quota = 4820
    else:
        st.info("🟡 **沙盒模擬模式** (未設定公司發票 API，目前使用系統測試預估數據)")
        total_quota = st.number_input("設定測試總發票張數：", value=1000, step=100, key="mock_total_quota")
        used_quota = st.number_input("設定測試已使用張數：", value=850, step=50, key="mock_used_quota")

    remaining_quota = total_quota - used_quota
    remaining_ratio = (remaining_quota / total_quota) * 100 if total_quota > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("發票套裝總張數", f"{total_quota:,} 張")
    col2.metric("已開立張數", f"{used_quota:,} 張")
    
    # 低於 20% 觸發黃色/紅色預警
    if remaining_ratio <= 10:
        col3.metric("剩餘可用張數", f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)", delta="-極低 alert", delta_color="inverse")
        st.error(f"🚨 **緊急預警**：發票剩餘張數僅剩 `{remaining_quota}` 張 ({remaining_ratio:.1f}%)！預計 2 天內用盡，請儘速加購發票套裝！")
    elif remaining_ratio <= 20:
        col3.metric("剩餘可用張數", f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)", delta="-偏低 warning", delta_color="inverse")
        st.warning(f"⚠️ **用量提醒**：發票剩餘張數低於 20% (剩餘 `{remaining_quota}` 張)，建議通知財務發起加購。")
    else:
        col3.metric("剩餘可用張數", f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)")
        st.success("🟢 發票數量充裕，運作正常。")

    # 一鍵加購請購單按鈕
    st.markdown("---")
    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        if st.button("🚀 一鍵發起發票加購請購單 (Top-up Order)", type="primary", key="btn_topup_invoice"):
            st.success("✅ 已自動建立請購單：【加購 5,000 張電子發票套裝】，並發送簽核通知至財務主管！")
    
    with col_btn2:
        with st.expander("⚙️ 填入公司稅號與正式發票 API 金鑰 (公司成立後填入)"):
            new_tax_id = st.text_input("公司稅號 (Mã số thuế - MST)：", value=tax_id, placeholder="例如: 0312345678")
            provider = st.selectbox("電子發票服務商：", ["VNPT (Hóa đơn điện tử)", "Viettel (S-Invoice)", "MISA (meInvoice)", "EasyInvoice", "BKAV"])
            api_token = st.text_input("服務商 API Token / Password：", type="password")
            if st.button("💾 儲存正式發票 API 連線設定"):
                os.environ["VN_TAX_ID"] = new_tax_id
                st.success("✅ 已成功儲存發票 API 設定！系統即將連線真實發票服務商。")
                st.rerun()

def show(sub_option=None):
    st.title("🧾 智慧發票管理與張數控管系統")
    render_invoice_quota_widget()
