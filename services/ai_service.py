from openai import OpenAI

# ── Teams 마크다운 깨짐 방지 ────────────────────────────────
def sanitize_for_teams(text):
    if not text:
        return ""
    return text.replace("~~", "~").replace("~", "-")

# ── 분석 결과 섹션 간격 정리 ────────────────────────────────
def format_analysis_spacing(text):
    if not text:
        return ""

    headings = [
        "🚨 점심 위험도 분석",
        "💡 오늘의 대응 방안",
        "🎬 오늘의 자막",
    ]

    for heading in headings:
        text = text.replace(f"\n{heading}", f"\n\n{heading}")

    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    return text.strip()

# ── OpenAI 식단 분석 (밥밥디라라 톤 + 물 섭취량 분리) ─────
def analyze_nutrition(menu_list, api_key):
    client = OpenAI(api_key=api_key)
    menu_text = ", ".join(menu_list)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""
너는 '밥밥디라라'라는 이름의 학교 점심 알림 봇이야.

컨셉:
- 2000년대 인터넷 개그 감성
- 무한도전 자막처럼 짧고 웃긴 멘트
- 시스템 경고, 위험도 분석, 대응 방안 같은 가짜 분석 컨셉
- 하지만 메뉴 정보는 정확하고 보기 쉽게 전달
- 비속어, 공격적인 표현은 사용하지 않기
- 학생들이 아침에 보고 피식 웃을 정도의 톤
- 물결표(~)는 Teams에서 취소선으로 보일 수 있으니 절대 사용하지 않기
- 모든 문장은 한국어로만 작성하기. 영어, 러시아어, 일본어, 중국어 등 다른 언어를 섞지 않기

오늘 점심 식단:
{menu_text}

반드시 아래 형식 그대로만 써줘.
절대 내용 추가하거나 반복하지 마.

🤖 밥밥디라라 분석 결과
오늘의 메인: 메뉴명
한마디: 2000년대 개그 감성의 짧은 멘트 1~2줄


🚨 점심 위험도 분석
🔥 예상 칼로리: 약 XXX-XXXkcal
🌶️ 매운맛 경보: 낮음/중간/높음
🧂 짠맛 경보: 낮음/중간/높음
🍚 밥 추가 가능성: 낮음/중간/높음
😴 식후 졸림 위험도: 낮음/중간/높음
🥩 탄단지 출전표: 탄수화물 XXg / 단백질 XXg / 지방 XXg
⭐ 밥심 점수: X.X / 10


💡 오늘의 대응 방안
1~2줄


🎬 오늘의 자막
“짧은 자막 한 줄”

💧 WATER:XX.XL

마지막 줄은 반드시 💧 WATER:숫자L 형식으로만 써줘. 예: 💧 WATER:2.0L
"""
        }]
    )

    raw = format_analysis_spacing(sanitize_for_teams(response.choices[0].message.content))

    # 물 섭취량 분리
    water_amount = "2.0L"  # 기본값
    nutrition_lines = []
    for line in raw.split("\n"):
        if "WATER:" in line:
            try:
                water_amount = line.split("WATER:")[1].strip()
            except:
                pass
        else:
            nutrition_lines.append(line.rstrip())

    # Teams 카드에서 섹션 사이가 붙어 보이지 않도록 빈 줄 유지
    while nutrition_lines and nutrition_lines[-1] == "":
        nutrition_lines.pop()

    nutrition_text = "\n".join(nutrition_lines)
    return nutrition_text, water_amount

# ── 오늘의 밥밥디라라 한마디 ────────────────────────────
def get_bab_comment(menu_list, api_key):
    client = OpenAI(api_key=api_key)
    menu_text = ", ".join(menu_list)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"오늘 점심이 {menu_text}래. '밥밥디라라 등장!' 느낌으로 2000년대 인터넷 개그 감성 한마디만 해줘. 시스템 경고나 위험도 분석 느낌을 살리고, 이모지 1개 포함해서 1줄로 써줘. 물결표(~)는 Teams에서 취소선으로 보일 수 있으니 절대 사용하지 마. 모든 문장은 한국어로만 작성하고, 영어, 러시아어, 일본어, 중국어 등 다른 언어를 섞지 마."
        }]
    )
    return sanitize_for_teams(response.choices[0].message.content)
