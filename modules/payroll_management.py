import streamlit as st
import pandas as pd

def render_payroll_management_page():
    st.title("💰 每月薪資與考勤變動扣款系統")
    st.caption("支援跨國多幣別 (VND, TWD, RMB) 加班費計算與打卡機遲到扣款對接")

    col_site, col_month = st.columns(2)
    with col_site:
        site = st.selectbox("選擇計算廠區", ["🇻🇳 越南平陽廠 (VND)", "🇨🇳 中國東莞廠 (RMB)", "🇹🇼 台灣總部 (TWD)"])
    with col_month:
        month = st.date_input("選擇薪資結算月份")

    st.subheader("📋 員工薪資與考勤明細表")
    
    payroll_df = pd.DataFrame({
        "員工工號": ["BH-001", "BH-002", "BH-003"],
        "姓名": ["阮文A (Nguyễn Văn A)", "黎氏B (Lê Thị B)", "陳大明"],
        "基本薪資": ["₫ 12,000,000", "₫ 10,500,000", "NT$ 65,000"],
        "加班時數": ["12.5 小時", "8.0 小時", "2.0 小時"],
        "遲到/請假扣款": ["-₫ 150,000", "₫ 0", "NT$ 0"],
        "實發金額": ["₫ 13,850,000", "₫ 11,700,000", "NT$ 66,200"]
    })
    
    st.table(payroll_df)

def show():
    render_payroll_management_page()

def main():
    render_payroll_management_page()
