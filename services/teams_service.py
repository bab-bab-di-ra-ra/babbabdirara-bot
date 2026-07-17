import requests
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

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
    today = datetime.now(KST).strftime("%Y년 %m월 %d일")
    menu_text = "\n".join(f"{get_menu_emoji(m)} {m}" for m in menu_list)

    # 이미지 생성에 성공했을 때만 Image 블록을 넣는다 (없으면 깨진 아이콘 대신 생략)
    image_block = [{
        "type": "Image",
        "url": image_url,
        "size": "Stretch",
        "spacing": "Medium"
    }] if image_url else []

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
                    *image_block,
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
                    },
                    {
                        "type": "Action.OpenUrl",
                        "title": "🎵 밥밥디라라 노래 듣기",
                        "url": "https://www.youtube.com/watch?v=XLfCED9MIGc&list=RDXLfCED9MIGc&start_radio=1"
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

# ── 방학 미션 카드 전송 (학식이 없을 때) ───────────────────
def send_vacation_mission(mission_text, webhook_url):
    today = datetime.now(KST).strftime("%Y년 %m월 %d일")

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
                        "text": "🎉 방학을 축하합니다!",
                        "color": "Accent"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"📅 {today} · 학식은 없지만 우리의 취업은 계속된다",
                        "isSubtle": True,
                        "spacing": "None"
                    },
                    {
                        "type": "Container",
                        "style": "accent",
                        "spacing": "Large",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "🎯 오늘의 방학 미션",
                                "weight": "Bolder",
                                "size": "Medium",
                                "horizontalAlignment": "Center"
                            },
                            {
                                "type": "TextBlock",
                                "text": mission_text,
                                "wrap": True,
                                "spacing": "Small",
                                "horizontalAlignment": "Center"
                            }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": "우리는 폴리텍, 취업으로 모인 사이! 오늘도 한 걸음 💪",
                        "wrap": True,
                        "spacing": "Medium",
                        "isSubtle": True,
                        "horizontalAlignment": "Center"
                    }
                ],
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "🎵 데분과 1집 발매 - 넥서스를 향한 길",
                        "url": "https://www.youtube.com/watch?v=IOP3KsOK72M"
                    }
                ]
            }
        }]
    }

    res = requests.post(webhook_url, json=payload)
    print(f"방학 미션 전송 결과: {res.status_code}")
    if res.status_code >= 400:
        print(f"거부 사유: {res.text}")
