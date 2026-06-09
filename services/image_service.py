import requests

# ── 이미지 생성용 프롬프트 빌드 ────────────────────────────
def build_image_prompt(menu_list):
    menu_text = ", ".join(menu_list[:4])
    return f"Korean school lunch tray with {menu_text}, bright colorful illustration style, appetizing food"

# ── Pollinations AI로 식단 이미지 생성 (외부 URL) ───────────
def generate_food_image(menu_list):
    prompt = build_image_prompt(menu_list)
    encoded = requests.utils.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=400&nologo=true"
    return image_url
