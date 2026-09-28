import os
import re
import streamlit as st

# ----------------------------------------------------
# 🛡️ 1. 文字輸入安全清洗 (防範 SQLi / XSS 攻擊)
# ----------------------------------------------------
def sanitize_user_input(text_input: str) -> str:
    """過濾常見的 SQL / HTML 惡意標籤字元"""
    if not text_input:
        return ""
    cleaned = re.sub(r"[<>'\"\\;]", "", text_input)
    return cleaned.strip()

# ----------------------------------------------------
# 🦠 2. 檔案病毒掃描邏輯 (以 ClamAV 為例)
# ----------------------------------------------------
def scan_file_for_viruses(uploaded_file) -> bool:
    """
    回傳 True 代表檔案安全；回傳 False 代表偵測到潛在病毒/惡意檔案
    """
    if uploaded_file is None:
        return True

    try:
        # 若系統環境有安裝 clamd 服務
        import clamd
        cd = clamd.ClamdUnixSocket()
        scan_result = cd.instream(uploaded_file)
        
        # 檢查掃描結果
        if scan_result and scan_result.get("stream")[0] == "FOUND":
            return False # 發現病毒
        return True # 安全
    except Exception:
        # 若未安裝 ClamAV，進行基本副檔名與雙重副檔名防護檢查
        filename = uploaded_file.name.lower()
        danger_extensions = [".exe", ".bat", ".vbs", ".php", ".js", ".sh", ".py"]
        
        # 檢查是否包含可執行檔副檔名
        if any(filename.endswith(ext) for ext in danger_extensions):
            return False
        # 防範雙重副檔名欺騙 (如 invoice.pdf.exe)
        if len(filename.split(".")) > 2:
            return False
            
        return True
