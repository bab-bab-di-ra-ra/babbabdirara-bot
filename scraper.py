import os
import requests
import sys
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

from services.menu_service import scrape_menu
from services.weather_service import get_weather
from services.image_service import generate_food_image
from services.ai_service import analyze_nutrition, get_bab_comment, get_vacation_mission
from services.teams_service import send_to_teams, send_vacation_mission

# ── 실행 ────────────────────────────────────────────────────
if __name__ == "__main__":
    webhook_url = sys.argv[1]
    openai_key  = sys.argv[2]
    imgbb_key   = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("IMGBB_KEY", "")

    # 방학 모드: 방학 기간에는 매일 취준 동기부여 미션을 보낸다.
    # GitHub 저장소 변수 VACATION_MODE=on 으로 켜고, 개강하면 꺼서 원래 폴백으로 복귀.
    # 학식 페이지에 지난 학기 표가 남아 있어도 미션이 나가도록 스크래핑보다 먼저 판단한다.
    vacation_mode = os.environ.get("VACATION_MODE", "").strip().lower() in ("on", "true", "1", "yes")

    if vacation_mode:
        print("방학 모드! 오늘의 미션 생성 중... 🎯")
        mission_text = get_vacation_mission(openai_key)
        send_vacation_mission(mission_text, webhook_url)
        print("오늘의 방학 미션 전송 완료 🎉")
        sys.exit(0)

    print("밥 어딨어? 찾는 중...")
    menu_list, day_text = scrape_menu()

    if not menu_list:
        today = datetime.now(KST).strftime("%Y년 %m월 %d일")
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
        image_url = generate_food_image(menu_list, openai_key, imgbb_key)
        print("AI한테 칼로리 물어보는 중...")
        nutrition_text, water_amount = analyze_nutrition(menu_list, openai_key)
        print("오늘의 한마디 생성 중...")
        bab_comment = get_bab_comment(menu_list, openai_key)
        print("밥밥디라라~ 전송 중...")
        send_to_teams(menu_list, day_text, nutrition_text, water_amount, image_url, weather_text, bab_comment, webhook_url)
        print("밥밥디라라!! 완료 🎉")
