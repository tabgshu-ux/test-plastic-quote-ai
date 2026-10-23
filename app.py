# app.py (系統真正的進入點主畫面)
import streamlit as st

# 設定頁面基本屬性
st.set_page_config(
    page_title="全球多產業 AI ERP 拼圖市集",
    page_icon="🧩",
    layout="wide"
)

# 1. 安全載入您專屬的拼圖選擇模組 (app_store)
try:
    from modules.app_store import render_app_store
except ImportError:
    try:
        from app_store import render_app_store
    except ImportError:
        def render_app_store(current_tenant=None, all_departments=None):
            st.error("⚠️ 找不到 modules/app_store.py 檔案，請確認您的檔案路徑！")

def main():
    # 主畫面的頂部導覽列或側邊欄切換
    st.sidebar.markdown("### 🚀 全球 SaaS ERP 多租戶管理")
    nav_mode = st.sidebar.radio("系統導覽選單", ["🧩 樂高模組拼圖市集 (App Store)", "📊 企業租戶儀表板"])
    
    if nav_mode == "🧩 樂高模組拼圖市集 (App Store)":
        # 呼叫您辛辛苦苦建立的拼圖選擇功能
        render_app_store()
    else:
        st.markdown("## 📊 企業租戶營運總覽")
        st.info("💡 此處為企業租戶管理與即時數據看板。")

if __name__ == "__main__":
    main()
