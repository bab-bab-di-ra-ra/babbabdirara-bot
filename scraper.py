import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import sys
from datetime import datetime, timedelta

# ── 1. 오늘 날짜 기준 이번 주 월요일 계산 ──────────────────
def get_this_week_monday():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%Y%m%d")

# ── 2. 식단 스크래핑 ────────────────────────────────────────
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
    today_weekday = datetime.now().weekday()  # 0=월, 1=화, 2=수, 3=목, 4=금

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

# ── 3. OpenAI 영양 분석 ─────────────────────────────────────
def analyze_nutrition(menu_list, api_key):
    client = OpenAI(api_key=api_key)
    menu_text = ", ".join(menu_list)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""오늘의 점심 식단: {menu_text}

다음 항목을 분석해서 이모지와 함께 보기 좋게 정리해줘:
🔥 총 예상 칼로리 (kcal)
🧂 예상 나트륨 (mg) - 하루 권장량 2000mg 대비 몇 %인지 포함
🥩 탄수화물 / 단백질 / 지방 (g)
💧 이 식단 후 권장 물 섭취량과 이유 (1-2줄)
💡 오늘의 건강 한마디

숫자는 구체적으로, 전체 5줄 이내로 간결하게."""
        }]
    )
    return response.choices[0].message.content

# ── 4. Teams Webhook 전송 ───────────────────────────────────
def send_to_teams(menu_list, day_text, nutrition_text, webhook_url):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    menu_text = "\n".join(f"• {m}" for m in menu_list)

    payload = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "size": "Large",
                        "weight": "Bolder",
                        "text": f"🍱 {today} 밥밥디라라~ {day_text} 점심은요!"
                    },
                    {
                        "type": "TextBlock",
                        "text": menu_text,
                        "wrap": True,
                        "spacing": "Small"
                    },
                    {
                        "type": "TextBlock",
                        "size": "Medium",
                        "weight": "Bolder",
                        "text": "🤖 AI한테 물어봤는데 이래",
                        "spacing": "Large",
                        "separator": True
                    },
                    {
                        "type": "TextBlock",
                        "text": nutrition_text,
                        "wrap": True,
                        "spacing": "Small"
                    }
                ]
            }
        }]
    }

    res = requests.post(webhook_url, json=payload)
    print(f"전송 결과: {res.status_code}")

# ── 실행 ────────────────────────────────────────────────────
if __name__ == "__main__":
    webhook_url = sys.argv[1]
    openai_key  = sys.argv[2]

    print("밥 어딨어? 찾는 중...")
    menu_list, day_text = scrape_menu()

    if not menu_list:
        today = datetime.now().strftime("%Y년 %m월 %d일")
        payload = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                    "body": [{
                        "type": "TextBlock",
                        "text": f"🍱 {today} 오늘은 밥밥디... 없다 😭 학식 확인해봐",
                        "wrap": True
                    }]
                }
            }]
        }
        requests.post(webhook_url, json=payload)
        print("밥이 없다고 알렸어 😭")
    else:
        print(f"오늘 밥 찾았다!! {menu_list}")
        print("AI한테 칼로리 물어보는 중...")
        nutrition_text = analyze_nutrition(menu_list, openai_key)
        print("밥밥디라라~ 전송 중...")
        send_to_teams(menu_list, day_text, nutrition_text, webhook_url)
        print("밥밥디라라!! 완료 🎉")
