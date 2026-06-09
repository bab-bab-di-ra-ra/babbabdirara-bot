import time

import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ── 학식 페이지 요청 (재시도 포함) ─────────────────────────
def _fetch_menu_html():
    """학식 페이지 HTML을 가져온다. kopo.ac.kr이 느려 타임아웃이 잦으므로
    타임아웃을 넉넉히 주고 몇 번 재시도한다. 끝까지 실패하면 None."""
    url = "https://www.kopo.ac.kr/gm/content.do?menu=12623"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for attempt in range(1, 4):  # 최대 3회 시도
        try:
            # (연결 타임아웃 10s, 읽기 타임아웃 30s)
            res = requests.get(url, headers=headers, timeout=(10, 30))
            res.raise_for_status()
            return res.text
        except Exception as e:
            print(f"학식 페이지 요청 실패 ({attempt}/3): {e}")
            if attempt < 3:
                time.sleep(3)

    return None

# ── 식단 스크래핑 ────────────────────────────────────────
def scrape_menu():
    html = _fetch_menu_html()
    if not html:
        print("학식 페이지를 끝내 못 가져옴")
        return None, None

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    if not table:
        return None, None

    rows = table.find_all("tr")
    today_weekday = datetime.now().weekday()
    weekday_names = ["월요일", "화요일", "수요일", "목요일", "금요일"]

    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue
        day_text = cells[0].get_text(strip=True)
        if today_weekday < 5 and weekday_names[today_weekday] in day_text:
            lunch_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            if lunch_text:
                menu_list = [m.strip() for m in lunch_text.split(",") if m.strip()]
                return menu_list, day_text

    return None, None
