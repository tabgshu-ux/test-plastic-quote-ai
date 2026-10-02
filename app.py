# ==========================================
# 6. 模組化導向 (分流呼叫各獨立模組，並帶入當前語系)
# ==========================================
curr_lang = st.session_state.current_lang

if menu_choice == "exec":
    executive_dashboard.render(engine, t, lang=curr_lang)
elif menu_choice == "ap":
    # 帶入 lang 參數，讓採購模組動態切換成越南文/英文/中文
    procurement_ap.render_procurement_ap_page(engine=engine, lang=curr_lang)
elif menu_choice == "ar":
    sales_order_ar.render_sales_order_ar_page(engine=engine, lang=curr_lang)
elif menu_choice == "hr":
    employee_management.render_employee_management(engine=engine, t=t, lang=curr_lang)
elif menu_choice == "ga":
    asset_management.render_asset_management_page(lang=curr_lang)
elif menu_choice in ["sheet_metal", "painting", "assembly"]:
    st.title(selected_menu_label)
    st.info("Hệ thống đang hoạt động bình thường / 現場工單追蹤與 QC 品質檢驗模組順利運作中。")
elif menu_choice == "warehouse":
    warehouse_management.render_warehouse_management(engine=engine, t=t, lang=curr_lang)
elif menu_choice == "approval":
    approval_workflow.render_approval_center(lang=curr_lang)
elif menu_choice == "it":
    user_management.render_user_management_page(lang=curr_lang)
