import streamlit as st
import datetime

def render_mobile_field_worker(current_tenant):
    # 手機優先樣式優化：放大按鈕與字體
    st.markdown("""
        <style>
        .stButton>button { width: 100%; height: 60px; font-size: 18px; font-weight: bold; border-radius: 12px; }
        .mobile-card { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 📱 工地師傅手機快速回報")
    st.info("💡 *極簡大按鈕設計，專為戶外工地、單手操作、非電腦背景師傅打造。*")

    # 模擬當前登入的外地師傅
    worker_name = st.session_state.get("current_tenant_user", {}).get("name", "外地第一線師傅")
    st.markdown(f"👷 **目前登入師傅**: `{worker_name}` | 📍 **狀態**: `線上作業中`")
    st.markdown("---")

    # 手機端四大直覺大按鈕功能頁籤
    action_tab = st.radio(
        "選擇回報動作",
        ["📸 1. 拍照上傳施工進度", "⏱️ 2. 一鍵回報今日點工/工時", "📦 3. 現場領料/叫料需求", "⚠️ 4. 回報現場異常狀況"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if "拍照上傳" in action_tab:
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.markdown("### 📸 拍照上傳施工現況")
        st.write("直接用手機拍照，系統會自動記錄GPS與時間。")
        
        project_site = st.selectbox("選擇目前施工案場/區域", ["越南平陽廠區一期", "越南平陽廠區二期配電室", "辦公大樓水電維護"])
        captured_image = st.file_uploader("點擊拍攝或上傳現場照片", type=["jpg", "png", "jpeg"])
        note = st.text_area("備註說明（可留空或口述）", placeholder="例：配電管線已拉好...")
        
        if st.button("🚀 一鍵送出施工照片", type="primary"):
            st.success("✅ 回報成功！照片與定位已即時同步回總公司後台與戰情室。")
        st.markdown('</div>', unsafe_allow_html=True)

    elif "一鍵回報" in action_tab:
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.markdown("### ⏱️ 今日工時快速登記")
        hours = st.slider("選擇今日工作時數 (小時)", 1, 12, 8)
        overtime = st.checkbox("有加班 (+2 小時)")
        
        if st.button("✅ 確認登記今日工時", type="primary"):
            total_h = hours + (2 if overtime else 0)
            st.success(f"🎉 成功登記 {total_h} 小時！已同步至薪資與專案成本系統。")
        st.markdown('</div>', unsafe_allow_html=True)

    elif "現場領料" in action_tab:
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.markdown("### 📦 快速領料 / 叫料申請")
        material = st.selectbox("選擇常用材料項目", ["PVC 電線管 2寸", "無熔絲開關 50A", "銅線 5.5mm²", "LED 燈具組"])
        qty = st.number_input("所需數量", min_value=1, value=5)
        
        if st.button("📦 送出叫料申請（通知倉庫）", type="primary"):
            st.success(f"✅ 叫料成功！已通知倉庫準備 [{material}] 共 [{qty}] 份。")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.markdown("⚠️ 現場突發狀況回報")
        issue_type = st.selectbox("問題類型", ["材料不足", "機台停擺/斷電", "圖紙與現場不符", "安全衛生疑慮"])
        description = st.text_area("簡述狀況", placeholder="請簡單輸入或說明...")
        
        if st.button("🚨 發送緊急求助訊號", type="primary"):
            st.error("🚨 警報已發送！工地主任與總工程師已收到您的即時推播通知。")
        st.markdown('</div>', unsafe_allow_html=True)
