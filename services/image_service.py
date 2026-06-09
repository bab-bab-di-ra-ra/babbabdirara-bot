import requests
from openai import OpenAI

# ── 이미지 생성용 프롬프트 빌드 ─────────────────────────────
def build_image_prompt(menu_list):
    menu_count = len(menu_list)

    bap    = menu_list[0] if menu_count > 0 else "흰쌀밥"
    guk    = menu_list[1] if menu_count > 1 else "된장찌개"
    main1  = menu_list[2] if menu_count > 2 else "메인반찬"
    main2  = menu_list[3] if menu_count > 3 else "나물"
    kimchi = menu_list[4] if menu_count > 4 else "김치"
    extra  = ", ".join(menu_list[5:]) if menu_count > 5 else ""

    return f"""
A top-down close-up photograph of a traditional Korean school cafeteria
stainless steel divided lunch tray on a plain white table.

The tray has exactly 5 compartments arranged as:
- Top-left compartment: {bap} (cooked rice, clearly visible grains)
- Top-right compartment: {guk} (Korean soup or stew with visible ingredients)
- Center compartment (largest): {main1} (main dish, most prominent)
- Bottom-left compartment: {main2} (side dish)
- Bottom-right compartment: {kimchi} (red kimchi, clearly recognizable)
{"- Small bowl beside tray: " + extra if extra else ""}

Photography requirements:
- Shot directly from above (bird's eye view)
- Each dish is freshly cooked and steaming
- Vivid, natural food colors, highly appetizing
- Photorealistic, ultra detailed, 4K quality
- Plain white or light gray background, no clutter, no people
- Only the tray visible, nothing else in frame
"""

# ── DALL-E 3로 식단 이미지 생성 ─────────────────────────────
def generate_food_image(menu_list, api_key):
    client = OpenAI(api_key=api_key)
    prompt = build_image_prompt(menu_list)

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt.strip(),
            size="1024x1024",
            quality="standard",
            style="natural",
            n=1
        )
        print("이미지 생성 성공! 🎨")
        return response.data[0].url

    except Exception as e:
        print(f"DALL-E 실패, Pollinations로 대체: {e}")
        menu_text = ", ".join(menu_list[:4])
        encoded = requests.utils.quote(
            f"Korean school lunch tray with {menu_text}, realistic food photo, top view, white background"
        )
        return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"