import streamlit as st
import pandas as pd
from datetime import datetime

def render_approval_center(lang):
    st.title("📑 企業 AI 簽核與表單審核中心")
    st.caption("跨部門表單簽核關卡、待辦清單與歷史簽核履歷管理")

    # 初始化簽核資料庫 (若尚未存在)
    if "approval_queue" not in st.session_state:
        st.session_state.approval_queue = [
            {
                "簽核單號": "APV-20260926-01",
                "來源模組": "🏢 總務部 - 零用金",
                "申請人": "李大同",
                "申請項目": "拜訪客戶計程車費 ($45.0 USD)",
                "申請日期": "2026-09-25",
                "當前關卡": "關卡 1：部門主管審核",
                "簽核層級需求": ["部門主管", "財務主管"],
                "狀態": "🟡 待簽核",
                "簽核歷程": []
            },
            {
                "簽核單號": "APV-20260926-02",
                "來源模組": "🏢 總務部 - 固定資產",
                "申請人": "張小美",
                "申請項目": "報廢行政部舊印表機 (FA-2022-005)",
                "申請日期": "2026-09-26",
                "當前關卡": "關卡 2：總務主管複核",
                "簽核層級需求": ["總務主管", "總經理"],
                "狀態": "🟡 待簽核",
                "簽核歷程": [
                    {"簽核人": "張主管", "動作": "🟢 同意", "時間": "2026-09-26 10:00", "意見": "符合報廢年限"}
                ]
            }
        ]

    # KPI 統計卡片
    queue = st.session_state.approval_queue
    pending_cnt = sum(1 for item in queue if "待簽核" in item["狀態"])
    approved_cnt = sum(1 for item in queue if "已核准" in item["狀態"])
    rejected_cnt = sum(1 for item in queue if "已駁回" in item["狀態"])

    c1, c2, c3 = st.columns(3)
    c1.metric("⌛ 我的待簽核單據", f"{pending_cnt} 筆", delta="需處理" if pending_cnt > 0 else "無待辦")
    c2.metric("🟢 本月已核准單據", f"{approved_cnt} 筆")
    c3.metric("🔴 已駁回/退回單據", f"{rejected_cnt} 筆")

    st.markdown("---")

    # 📥 待辦簽核面板
    st.markdown("### 📥 待審核單據列表")
    pending_items = [item for item in queue if "待簽核" in item["狀態"]]

    if pending_items:
        for idx, item in enumerate(pending_items):
            with st.expander(f"📄 [{item['簽核單號']}] {item['來源模組']} — {item['申請項目']} (申請人: {item['申請人']})", expanded=(idx==0)):
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**申請日期：** {item['申請日期']}")
                    st.write(f"**來源模組：** {item['來源模組']}")
                    st.write(f"**當前審核關卡：** `{item['當前關卡']}`")
                with col_info2:
                    st.write(f"**申請人：** {item['申請人']}")
                    st.write(f"**申請詳情：** {item['申請項目']}")

                # 簽核歷程展示
                if item["簽核歷程"]:
                    st.markdown("**📜 歷史簽核紀錄：**")
                    for log in item["簽核歷程"]:
                        st.caption(f"• {log['時間']} | {log['簽核人']} : {log['動作']} — 意見: {log['意見']}")

                # ✍️ 簽核操作表單
                st.markdown("---")
                with st.form(f"form_approval_{item['簽核單號']}"):
                    user_role = st.session_state.user_info["role"]
                    user_name = st.session_state.user_info["name"]
                    
                    st.write(f"**當前簽核執行人：** {user_name} ({user_role})")
                    comment = st.text_input("審核意見 / 備註", placeholder="請輸入同意或駁回之原因...")
                    
                    btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 2])
                    with btn_c1:
                        btn_approve = st.form_submit_button("🟢 同意 (Approve)", type="primary")
                    with btn_c2:
                        btn_reject = st.form_submit_button("🔴 駁回 (Reject)")

                    if btn_approve:
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        item["簽核歷程"].append({
                            "簽核人": f"{user_name} ({user_role})",
                            "動作": "🟢 同意",
                            "時間": now_str,
                            "意見": comment if comment else "同意辦理"
                        })
                        item["狀態"] = "🟢 已核准"
                        st.success(f"✅ 單號 {item['簽核單號']} 已順利核准！")
                        st.rerun()

                    if btn_reject:
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        item["簽核歷程"].append({
                            "簽核人": f"{user_name} ({user_role})",
                            "動作": "🔴 駁回",
                            "時間": now_str,
                            "意見": comment if comment else "退回重審"
                        })
                        item["狀態"] = "🔴 已駁回"
                        st.error(f"❌ 單號 {item['簽核單號']} 已駁回！")
                        st.rerun()
    else:
        st.success("🎉 目前沒有任何待您審核的表單單據！")

    st.markdown("---")

    # 📜 歷史簽核清單
    st.markdown("### 📜 歷史簽核紀錄與歸檔")
    df_queue = pd.DataFrame(queue)
    st.dataframe(df_queue, use_container_width=True)
