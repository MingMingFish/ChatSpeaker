import re

async def get_vid(url: str) -> str | None:
    # 1. 處理純 11 碼的影片 ID (排除包含網址斜線等情況)
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    # 2. 使用正規表示式萃取 YouTube ID
    # 支援格式：watch?v=, youtu.be/, live/, shorts/
    pattern = r'(?:v=|live\/|youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1) # 回傳括號內捕捉到的 11 碼 ID
    
    return None