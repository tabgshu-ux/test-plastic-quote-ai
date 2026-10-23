# app.py (系統真正的進入點主畫面 - 自動路徑相容防呆版)
import streamlit as st

st.set_page_config(
    page_title="全球多產業 AI ERP 拼圖市集",
    page_icon="🧩",
    layout="wide"
)

# 自動偵測並載入拼圖選擇功能（無論它在 modules/ 還是根目錄都能抓到）
render_app_store = None
try:
    from modules.app_store import render_app_store
except ImportError:
    try:
        from app_store import render_app_store
    except ImportError:
        pass

def main():
    st.sidebar.markdown("### 🚀 全球 SaaS ERP 多租戶管理")
    nav_mode = st.sidebar.radio("系統導覽選單", ["🧩 樂高模組拼圖市集 (App Store)", "📊 企業租戶儀表板"])
    
    if nav_mode == "🧩 樂高模組拼圖市集 (App Store)":
        if render_app_store is not None:
            render_app_store()
        else:
            st.error("⚠️ 找不到 app_store 模組！請確認您的 app_store.py 檔案是否存在於專案中。")
    else:
        st.markdown("## 📊 企業租戶營運總覽")
        st.info("💡 此處為企業租戶管理與即時數據看板。")

if __name__ == "__main__":
    main()
