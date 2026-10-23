# app.py (系統進入點主畫面 - 精準對應 modules 資料夾架構)
import streamlit as st

st.set_page_config(
    page_title="全球多產業 AI ERP 拼圖市集",
    page_icon="🧩",
    layout="wide"
)

# 從您的 modules 資料夾中精準引入拼圖選擇模組
try:
    from modules.app_store import render_app_store
except ImportError:
    # 預防萬一的備用載入
    try:
        from app_store import render_app_store
    except ImportError:
        render_app_store = None

def main():
    st.sidebar.markdown("### 🚀 全球 SaaS ERP 多租戶管理")
    nav_mode = st.sidebar.radio("系統導覽選單", ["🧩 樂高模組拼圖市集 (App Store)", "📊 企業租戶儀表板"])
    
    if nav_mode == "🧩 樂高模組拼圖市集 (App Store)":
        if render_app_store is not None:
            # 成功呼叫您的拼圖選擇程式與外掛架構
            render_app_store()
        else:
            st.error("⚠️ 找不到 modules/app_store.py 檔案，請檢查 GitHub 上的 modules 資料夾是否包含 app_store.py。")
    else:
        st.markdown("## 📊 企業租戶營運總覽")
        st.info("💡 此處為企業租戶管理與即時數據看板。")

if __name__ == "__main__":
    main()
