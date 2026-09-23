# ====================================================
# 頁面主進入點 (供 app.py 呼叫)
# ====================================================
def render_sales_quotation_page(sub_option="📝 AI 即時報價 & CAD/3D Pipeline"):
    """業務報價模組主進入點"""
    st.title("💼 業務/行銷 — 報價與 CAD/3D Pipeline 系統")
    
    if "歷史報價" in sub_option:
        render_sales_overview()
    else:
        render_sales_frontend()

def show(sub_option="📝 AI 即時報價 & CAD/3D Pipeline"):
    render_sales_quotation_page(sub_option)

def main(sub_option="📝 AI 即時報價 & CAD/3D Pipeline"):
    render_sales_quotation_page(sub_option)
