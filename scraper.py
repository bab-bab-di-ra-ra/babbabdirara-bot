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

# ── 3. 날씨 가져오기 (광명시) ───────────────────────────────
def get_weather():
    try:
        url = "https://wttr.in/Gwangmyeong?format=%C+%t+%h"
        res = requests.get(url, timeout=5)
        weather = res.text.strip()
        return f"🌤️ 광명 날씨: {weather}"
    except:
        return "🌤️ 날씨 정보를 가져오지 못했어요"

# ── 4. Pollinations AI로 식단 이미지 생성 ───────────────────
def generate_food_image(menu_list):
    menu_text = ", ".join(menu_list[:4])
    prompt = f"Korean school lunch tray with {menu_text}, bright colorful illustration style, appetizing food"
    encoded = requests.utils.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=400&nologo=true"
    return image_url

# ── 5. OpenAI 영양 분석 (영양정보 + 물 섭취량 분리) ─────────
def analyze_nutrition(menu_list, api_key):
    client = OpenAI(api_key=api_key)
    menu_text = ", ".join(menu_list)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""오늘의 점심 식단: {menu_text}

반드시 아래 형식 그대로만 써줘. 절대 내용 추가하거나 반복하지 마:
🔥 총 예상 칼로리: XXXkcal
🧂 예상 나트륨: XXXmg (하루 권장량의 XX%)
🥩 탄수화물 XXg / 단백질 XXg / 지방 XXg
💡 건강 한마디: (한 줄)
💧 WATER:XX.XL

마지막 줄은 반드시 💧 WATER:숫자L 형식으로만 써줘. (예: 💧 WATER:2.5L)"""
        }]
    )

    raw = response.choices[0].message.content

    # 물 섭취량 분리
    water_amount = "2.0L"  # 기본값
    nutrition_lines = []
    for line in raw.split("\n"):
        if "WATER:" in line:
            try:
                water_amount = line.split("WATER:")[1].strip()
            except:
                pass
        elif line.strip():
            nutrition_lines.append(line.strip())

    nutrition_text = "\n".join(nutrition_lines)
    return nutrition_text, water_amount

# ── 6. 오늘의 밥밥디라라 한마디 ────────────────────────────
def get_bab_comment(menu_list, api_key):
    client = OpenAI(api_key=api_key)
    menu_text = ", ".join(menu_list)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"오늘 점심이 {menu_text}래. 친구한테 급식 메뉴 알려주듯이 짧게 한마디만 해줘. 이모지 1개 포함, 1줄."
        }]
    )
    return response.choices[0].message.content

# ── 7. Teams Webhook 전송 ───────────────────────────────────
def send_to_teams(menu_list, day_text, nutrition_text, water_amount, image_url, weather_text, bab_comment, webhook_url):
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
                        "size": "ExtraLarge",
                        "weight": "Bolder",
                        "text": "🍱 밥밥디라라~",
                        "color": "Accent"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"📅 {today} {day_text}",
                        "isSubtle": True,
                        "spacing": "None"
                    },
                    {
                        "type": "TextBlock",
                        "text": weather_text,
                        "isSubtle": True,
                        "spacing": "None"
                    },
                    {
                        "type": "Image",
                        "url": image_url,
                        "size": "Stretch",
                        "spacing": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "size": "Medium",
                        "weight": "Bolder",
                        "text": "📋 오늘의 메뉴",
                        "spacing": "ExtraLarge",
                        "separator": True
                    },
                    {
                        "type": "TextBlock",
                        "text": menu_text,
                        "wrap": True,
                        "spacing": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "size": "Medium",
                        "weight": "Bolder",
                        "text": "🔬 AI가 분석한 오늘 식판",
                        "spacing": "ExtraLarge",
                        "separator": True
                    },
                    {
                        "type": "TextBlock",
                        "text": nutrition_text,
                        "wrap": True,
                        "spacing": "Medium"
                    },
                    # 💧 물 섭취량 강조 박스
                    {
                        "type": "Container",
                        "style": "accent",
                        "spacing": "Large",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "💧 오늘의 권장 물 섭취량",
                                "weight": "Bolder",
                                "size": "Medium",
                                "horizontalAlignment": "Center"
                            },
                            {
                                "type": "TextBlock",
                                "text": water_amount,
                                "weight": "Bolder",
                                "size": "ExtraLarge",
                                "color": "Accent",
                                "horizontalAlignment": "Center",
                                "spacing": "None"
                            }
                        ]
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
                        "wrap": True,
                        "size": "Large",
                        "weight": "Bolder"
                    }]
                }
            }]
        }
        requests.post(webhook_url, json=payload)
        print("밥이 없다고 알렸어 😭")
    else:
        print(f"오늘 밥 찾았다!! {menu_list}")
        print("날씨 확인 중...")
        weather_text = get_weather()
        print("이미지 생성 중... 🎨")
        image_url = generate_food_image(menu_list)
        print("AI한테 칼로리 물어보는 중...")
        nutrition_text, water_amount = analyze_nutrition(menu_list, openai_key)
        print("오늘의 한마디 생성 중...")
        bab_comment = get_bab_comment(menu_list, openai_key)
        print("밥밥디라라~ 전송 중...")
        send_to_teams(menu_list, day_text, nutrition_text, water_amount, image_url, weather_text, bab_comment, webhook_url)
        print("밥밥디라라!! 완료 🎉")
