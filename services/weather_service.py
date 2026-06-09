import requests

# ── 날씨 가져오기 (광명시) ───────────────────────────────
def get_weather():
    try:
        url = "https://wttr.in/Gwangmyeong?format=%C+%t+%h&m"
        res = requests.get(url, timeout=5)
        weather = res.text.strip()
        return f"🌤️ 광명 날씨: {weather}"
    except:
        return "🌤️ 날씨 정보를 가져오지 못했어요"
