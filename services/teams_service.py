import requests
from datetime import datetime

# ── 메뉴별 이모지 매핑 ─────────────────────────────────────
def get_menu_emoji(menu_name):
    emoji_map = {
        "닭": "🍗",
        "치즈": "🧀",
        "밥": "🍚",
        "찌개": "🥣",
        "국": "🥣",
        "탕": "🥣",
        "어묵": "🍢",
        "김치": "🥬",
        "쌈무": "🥬",
        "돈까스": "🍖",
        "카레": "🍛",
        "짜장": "🍜",
        "우동": "🍜",
        "면": "🍜",
        "생선": "🐟",
        "계란": "🥚",
        "불고기": "🥩",
        "제육": "🥩",
        "샐러드": "🥗",
        "떡": "🍡",
        "만두": "🥟",
    }

    for keyword, emoji in emoji_map.items():
        if keyword in menu_name:
            return emoji

    return "•"

# ── Teams Webhook 전송 ───────────────────────────────────
def send_to_teams(menu_list, day_text, nutrition_text, water_amount, image_url, weather_text, bab_comment, webhook_url):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    menu_text = "\n".join(f"{get_menu_emoji(m)} {m}" for m in menu_list)

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
                        "text": f"🧚 {bab_comment}",
                        "wrap": True,
                        "spacing": "Medium",
                        "weight": "Bolder"
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
                ],
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "🍱 식단 페이지 보러가기",
                        "url": "https://www.kopo.ac.kr/gm/content.do?menu=12623"
                    }
                ]
            }
        }]
    }

    import json
    payload_kb = len(json.dumps(payload).encode("utf-8")) / 1024
    print(f"payload 크기: {payload_kb:.1f} KB")

    res = requests.post(webhook_url, json=payload)
    print(f"전송 결과: {res.status_code}")
    if res.status_code >= 400:
        print(f"거부 사유: {res.text}")
