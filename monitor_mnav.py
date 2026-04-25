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
    push_token = os.getenv("PUSH_TOKEN")
    if not push_token:
        return

    # 方案 C：使用最原始、兼容性最强的接口
    # 彻底避开 api2，直接请求 pushdeer.com 的后端
    url = f"https://www.pushdeer.com/send?pushkey={push_token}&text=MSTR告警&desp=当前mNAV:{mnav}"
    
    # 关键：模拟一个真实的浏览器，防止被服务器识别为机器人而重定向
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }

    try:
        # 强制不跟随重定向 (allow_redirects=False)
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=False)
        
        # 如果返回的是 200 且包含 JSON，则成功
        if response.status_code == 200:
            print(f"推送成功: {response.text[:100]}")
        else:
            print(f"推送异常，状态码: {response.status_code}")
            # 如果还是不行，打印出最终生成的 URL (隐藏部分 key 以保安全)
            print(f"Debug URL: {url[:30]}***{url[-10:]}")
    except Exception as e:
        print(f"请求失败: {e}")
        
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
