from datetime import datetime, timezone, timedelta, date
from openai import OpenAI

KST = timezone(timedelta(hours=9))

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

    system_prompt = """
너는 '밥밥디라라'라는 이름의 학교 점심 알림 봇이야.

컨셉:
- 2000년대 인터넷 개그 감성
- 무한도전 자막처럼 짧고 웃긴 멘트
- 시스템 경고, 위험도 분석, 대응 방안 같은 가짜 분석 컨셉
- 하지만 메뉴 정보는 정확하고 보기 쉽게 전달
- 비속어, 공격적인 표현은 사용하지 않기
- 학교 식단이므로 술(소주, 맥주, 와인 등)이나 음주 관련 표현은 절대 사용하지 않기
- 메뉴명에 숫자나 온도처럼 들리는 말(예: '사천'짜장 → 4천 원?, '천도'볶음 → 1000도?, '백도' → 100도?)이 있으면 그걸 엉뚱하게 오해한 척 말장난하기. 예: "사천짜장이면 사천 원인가요? 하하", "천도라니 너무 뜨거운 거 아니에요?". 단 억지로 끼워넣지 말고 해당하는 메뉴가 있을 때만 자연스럽게
- 아이스티가 나오면 마치 술처럼 어른들이나 마시는 금단의 음료인 척 능청맞게 농담하기. 예: "아이스티라니.. 우린 다 어른인데 마셔도 되는 걸까요?". 단 아이스티가 있을 때만
- 학생들이 아침에 보고 피식 웃을 정도의 톤
- 물결표(~)는 Teams에서 취소선으로 보일 수 있으니 절대 사용하지 않기
- 모든 문장은 한국어로만 작성하기. 영어, 러시아어, 일본어, 중국어 등 다른 언어를 섞지 않기

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
물양은 항상 2.0L로 고정하지 말고, 메뉴의 짠맛/매운맛/기름기가 강할수록 늘려서 1.5L~2.5L 범위에서 0.1 단위로 메뉴에 맞게 정해줘.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"오늘 점심 식단:\n{menu_text}"},
        ]
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

    system_prompt = """너는 '밥밥디라라'라는 학교 점심 알림 봇이야. '밥밥디라라 등장!' 느낌으로 2000년대 인터넷 개그 감성 한마디만 해줘. 시스템 경고나 위험도 분석 느낌을 살리고, 이모지 1개 포함해서 1줄로 써줘. 학교 식단이므로 술(소주, 맥주, 와인 등)이나 음주 관련 표현은 절대 사용하지 마. 메뉴명에 숫자나 온도처럼 들리는 말(예: '사천'짜장→4천 원?, '천도'→1000도?, '백도'→100도?)이 있으면 그걸 엉뚱하게 오해한 척 말장난해도 좋아(예: "사천짜장이면 사천 원인가요? 하하"). 단 해당하는 메뉴가 있을 때만 자연스럽게. 아이스티가 나오면 마치 아이들만 마셔야 하는 음료인 척 능청맞게 농담해도 좋아(예: "아이스티라니.. 우린 다 어른인데 마셔도 되는 걸까요?"). 단 아이스티가 있을 때만. 물결표(~)는 Teams에서 취소선으로 보일 수 있으니 절대 사용하지 마. 모든 문장은 한국어로만 작성하고, 영어, 러시아어, 일본어, 중국어 등 다른 언어를 섞지 마."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"오늘 점심이 {menu_text}래."},
        ]
    )
    return sanitize_for_teams(response.choices[0].message.content)

# ── 방학 미션 주제 (취준 중심 + 리프레시 살짝) ──────────────
# 폴리텍 취업 목적 모임이라 지원/자격증/코테/포트폴리오/이력서/면접이 메인,
# 번아웃 방지를 위해 운동·휴식 주제를 사이사이 섞는다.
VACATION_MISSIONS = [
    "관심 있는 회사 채용 공고를 하나 찾아 지원서 넣어보기",
    "오늘은 자격증데이! 개념 한 챕터 공부하기",
    "인프라(리눅스, AWS, 네트워크 등) 개념 정리하기",
    "코딩테스트 문제 한 문제 풀어보기",
    "깃허브/포트폴리오 프로젝트 하나 README 정리하기",
    "이력서·자기소개서 문장 한 줄 다듬기",
    "면접 예상 질문 하나 골라 답변 소리 내어 연습하기",
    "새로운 기술이나 개념 하나를 30분 동안 공부하기",
    "가볍게 산책하거나 운동하면서 머리 식히기",  # 리프레시
    "지원하고 싶은 회사·직무를 3곳 리서치해서 정리하기",
    "지난 프로젝트를 회고하며 배운 점 한 가지 메모하기",
    "채용 사이트나 링크드인 둘러보며 시장 감 익히기",
    "오늘은 푹 쉬면서 좋아하는 걸로 에너지 충전하기",  # 리프레시
]

# 평일 순차 회전의 기준점: 이 월요일을 인덱스 0(지원서)으로 맞추고,
# 이후 평일마다 한 칸씩(주말은 세지 않고 건너뜀) 순서대로 굴린다.
VACATION_ANCHOR = date(2026, 7, 20)  # 월요일
VACATION_ANCHOR_INDEX = 0

# ── 기준일로부터 평일(월~금) 경과 수 (주말은 세지 않음) ────
def _weekdays_since_anchor(today):
    diff = today.toordinal() - VACATION_ANCHOR.toordinal()
    full_weeks, rem = divmod(diff, 7)  # rem: 0~6 (음수 diff에도 0~6 유지)
    return full_weeks * 5 + min(rem, 5)  # 토(5)/일(6)은 같은 칸으로 접음(평일만 실행되므로 무해)

# ── 오늘의 방학 미션 (학식이 없을 때) ─────────────────────
def get_vacation_mission(api_key):
    now = datetime.now(KST)
    # 평일마다 한 칸씩 순차 진행. 07/20(월)=0번(지원서)부터 시작해 하나도 건너뛰지 않고 순환
    idx = (VACATION_ANCHOR_INDEX + _weekdays_since_anchor(now.date())) % len(VACATION_MISSIONS)
    theme = VACATION_MISSIONS[idx]

    client = OpenAI(api_key=api_key)
    system_prompt = """너는 '밥밥디라라'라는 학교 알림 봇이야. 지금은 방학이라 학식이 없어.
우리는 폴리텍대학교 학생들이고 취업을 위해 모인 사이라, 방학 동안 서로 동기부여를 해주려고 해.
2000년대 인터넷 개그 감성으로, '방학 미션 등장!' 느낌의 밝고 응원하는 톤으로 써줘.

반드시 아래 형식 그대로, 딱 두 줄만 써줘. 다른 말은 절대 추가하지 마.
미션: (주어진 오늘의 미션을 밥밥디라라 말투로 한 문장으로. 이모지 1개 포함)
한마디: (짧고 힘나는 응원 한마디. 이모지 1개 포함)

규칙:
- 비속어, 공격적인 표현 금지
- 술이나 음주 관련 표현 절대 금지
- 물결표(~)는 Teams에서 취소선으로 보이니 절대 사용 금지
- 모든 문장은 한국어로만. 다른 언어를 섞지 않기
- 부담 주지 말고 가볍고 응원하는 느낌으로"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"오늘의 미션: {theme}"},
        ]
    )
    return sanitize_for_teams(response.choices[0].message.content)
