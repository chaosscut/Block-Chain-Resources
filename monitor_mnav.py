import requests
import re
import os

def get_mstr_mnav():
    # 提示：strategy.com 的数据通常在页面源码或其内部 API 中
    # 这里我们模拟请求其页面并解析
    url = "https://www.strategy.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 实际开发时，我会根据该网站当时的 HTML 结构进行正则提取
        # 假设我们寻找类似 "mNAV": 1.25 这样的字段
        # 下面是演示逻辑：
        content = response.text
        # 寻找 mNAV 数值（具体正则需根据网页实时结构调整）
        match = re.search(r'mNAV.*?(\d+\.\d+)', content)
        if match:
            return float(match.group(1))
        else:
            # 如果主页不好抓，可以考虑备用数据源如 mstrtracker.com
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def send_notification(mnav):
    # 这里建议使用微信推送服务，如 'Server酱' 或 'PushDeer'
    # 只需要一个 URL 就能给手机发消息
    push_token = os.getenv("PUSH_TOKEN")
    if not push_token:
        print("未设置推送 Token")
        return

    title = f"MSTR 买入机会告警！"
    content = f"当前 mNAV 为 {mnav}，已低于预设阈值。请关注 MSTR 股价及 BTC 走势。"
    
    # 以 PushDeer 为例
    push_url = f"https://api2.pushdeer.com/send?pushkey={push_token}&text={title}&desp={content}"
    requests.get(push_url)

if __name__ == "__main__":
    current_mnav = get_mstr_mnav()
    print(f"Current mNAV: {current_mnav}")
    
    # 设定你的买入观察阈值，比如 1.15
    THRESHOLD = 1.15
    
    if current_mnav and current_mnav <= THRESHOLD:
        send_notification(current_mnav)
