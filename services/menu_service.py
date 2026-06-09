import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ── 식단 스크래핑 ────────────────────────────────────────
def scrape_menu():
    url = "https://www.kopo.ac.kr/gm/content.do?menu=12623"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

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
