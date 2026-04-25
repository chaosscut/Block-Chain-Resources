import requests
from bs4 import BeautifulSoup
import re
import os

def get_mstr_mnav():
    url = "https://www.strategy.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        # 使用 BeautifulSoup 解析 HTML 结构
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 策略 1：定位包含 "mNAV" 文本的标签
        # strategy.com 的数值通常放在某个特定的 class 或 span 中
        # 我们先打印出所有包含 mNAV 的文本块进行精准定位
        mnav_elements = soup.find_all(string=re.compile("mNAV"))
        
        for element in mnav_elements:
            # 寻找该文本附近的数字（通常是下一个兄弟节点或父节点的内容）
            parent_text = element.parent.get_text()
            # 匹配 1.xx 或 2.xx 这种符合常理的溢价率
            match = re.search(r'([0-2]\.\d{2})', parent_text)
            if match:
                return float(match.group(1))
        
        # 策略 2：如果策略 1 失败，使用备用可靠数据源 (MSTRTracker)
        # 这个网站的数据结构更简单，专门为抓取设计
        backup_res = requests.get("https://mstrtracker.com/", timeout=10)
        # 寻找类似 1.25x 的字符串
        backup_match = re.search(r'(\d+\.\d+)x', backup_res.text)
        if backup_match:
            val = float(backup_match.group(1))
            if 0.5 < val < 10.0: # 确保数值在合理区间
                return val
                
        return None
    except Exception as e:
        print(f"抓取异常: {e}")
        return None

def send_notification(mnav):
    # 这里的名字确保和 GitHub Secrets 里的一致
    bark_key = os.getenv("PUSH_TOKEN") 
    if not bark_key: return

    # Bark 的标准接口：地址/Key/标题/内容
    # 我们加入参数使它在 Apple Watch 上显示更美观
    url = f"https://api.day.app/{bark_key}/MSTR买入告警/当前mNAV为:{mnav}?group=MSTR&icon=https://www.microstrategy.com/favicon.ico"
    
    print("正在通过 Bark 发送推送...")
    try:
        response = requests.get(url, timeout=15)
        print(f"Bark 返回结果: {response.text}")
    except Exception as e:
        print(f"Bark 请求失败: {e}")
        
if __name__ == "__main__":
    current_mnav = get_mstr_mnav()
    print(f"Final Checked mNAV: {current_mnav}")
    
    THRESHOLD = 1.90 
    print(f"Checking threshold: {current_mnav} <= {THRESHOLD}")

    if current_mnav and current_mnav <= THRESHOLD:
        print("Conditions met. Attempting to send notification...")
        send_notification(current_mnav)
    else:
        print("Conditions NOT met. Skipping notification.")
