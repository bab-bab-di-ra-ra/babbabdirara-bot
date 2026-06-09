# 🍱 밥밥디라라 (babbabdirara-bot)

매일 오전 9시(KST), **광명 폴리텍 학식 식단**을 스크래핑해서
AI 영양 분석과 식단 이미지를 곁들여 **Microsoft Teams**로 알려주는 봇입니다.

2000년대 인터넷 개그 감성의 "밥밥디라라" 톤으로, 위험도 분석·대응 방안·오늘의 자막 같은
가짜 시스템 경고 컨셉을 입혀 아침에 피식 웃게 만드는 게 목표입니다.

---

## ✨ 주요 기능

- 📋 **식단 스크래핑** — 폴리텍 학식 페이지에서 오늘 요일의 점심 메뉴 추출
- 🌤️ **날씨 표시** — 광명시 현재 날씨 (wttr.in)
- 🎨 **식단 이미지 생성** — OpenAI `gpt-image-1`로 식판 일러스트 생성 후 imgbb에 업로드, 정적 URL을 카드에 삽입
- 🔬 **AI 영양 분석** — 예상 칼로리, 매운맛/짠맛 경보, 탄단지 비율, 권장 물 섭취량 등
- 🧚 **오늘의 한마디** — 밥밥디라라 감성 멘트
- 💬 **Teams 전송** — Adaptive Card 형태로 Webhook 전송

---

## 🗂️ 프로젝트 구조

```
babbabdirara-bot/
├─ scraper.py              # 메인 실행 (오케스트레이터)
├─ requirements.txt        # 의존성 목록
├─ services/
│  ├─ menu_service.py      # scrape_menu() — 식단 스크래핑
│  ├─ weather_service.py   # get_weather() — 날씨
│  ├─ image_service.py     # 식단 이미지 생성 (OpenAI) → imgbb 업로드 → URL
│  ├─ ai_service.py        # 영양 분석 / 한마디 (OpenAI)
│  └─ teams_service.py     # 이모지 매핑 / Teams 카드 전송
└─ .github/workflows/
   └─ lunch.yml            # 매일 오전 9시 자동 실행
```

---

## 🚀 실행 방법 (로컬)

> Python 3.9 이상 필요

```bash
# 1. 저장소 클론
git clone <repo-url>
cd babbabdirara-bot

# 2. 가상환경 생성 & 활성화
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 실행 (인자 순서: Teams Webhook → OpenAI API 키 → imgbb API 키)
python3 scraper.py "<TEAMS_WEBHOOK_URL>" "<OPENAI_API_KEY>" "<IMGBB_API_KEY>"
```

환경변수로 빼서 쓰면 편합니다:

```bash
export WEBHOOK_URL="https://..."
export OPENAI_KEY="sk-..."
export IMGBB_KEY="..."
python3 scraper.py "$WEBHOOK_URL" "$OPENAI_KEY" "$IMGBB_KEY"
```

> imgbb 키는 세 번째 인자 대신 `IMGBB_KEY` 환경변수로 줘도 됩니다.
> 키가 없으면 이미지 없이 카드만 전송됩니다.

---

## 🔑 필요한 키

| 키 | 용도 | 발급처 |
|----|------|--------|
| `TEAMS_WEBHOOK` | Teams 채널에 메시지 전송 | Teams 채널 → Incoming Webhook 커넥터 |
| `OPENAI_API_KEY` | 영양 분석 + 이미지 생성 | https://platform.openai.com |
| `IMGBB_KEY` | 생성한 이미지 호스팅 (URL 발급) | https://api.imgbb.com (무료) |

> ⚠️ `gpt-image-1` 이미지 생성은 OpenAI 조직이 **verified** 상태여야 호출됩니다 (미인증 시 403).
> 미인증이거나 imgbb 키가 없으면 이미지 없이 카드만 정상 전송됩니다.

---

## ⏰ 자동 실행 (GitHub Actions)

`.github/workflows/lunch.yml`이 **평일 오전 9시(KST)** 자동 실행합니다.
저장소 **Settings → Secrets and variables → Actions**에 아래 두 개를 등록하세요:

- `TEAMS_WEBHOOK`
- `OPENAI_API_KEY`
- `IMGBB_KEY`

`workflow_dispatch`로 수동 실행(테스트 버튼)도 가능합니다.

---

## 📝 참고

- `.venv`, `__pycache__`, `.env`는 커밋되지 않습니다 (`.gitignore` 처리).
- 이미지는 base64로 카드에 직접 넣지 않습니다. Teams Adaptive Card는 크기 한도(약 28KB)가 있어 base64를 박으면 페이로드가 한도를 넘겨 메시지가 조용히 사라집니다. 그래서 imgbb에 업로드한 정적 URL만 카드에 넣고, 비용/속도를 위해 이미지 품질은 `low`로 생성합니다.
