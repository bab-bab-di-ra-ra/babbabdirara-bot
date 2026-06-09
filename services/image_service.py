import requests
from openai import OpenAI

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

The tray has exactly 5 compartments:
- Top-left: {bap} (cooked rice)
- Top-right: {guk} (Korean soup or stew)
- Center (largest): {main1} (main dish)
- Bottom-left: {main2} (side dish)
- Bottom-right: {kimchi} (kimchi)
{"- Extra side dish: " + extra if extra else ""}

Realistic food photography, top-down view, warm lighting,
traditional Korean stainless steel divided tray,
each dish looks freshly cooked, ultra detailed, photorealistic,
plain white background, no clutter, no people.
"""

def generate_food_image(menu_list, api_key):
    client = OpenAI(api_key=api_key)
    prompt = build_image_prompt(menu_list)

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt.strip(),
        size="1024x1024",
        quality="standard",
        n=1
    )
    print("이미지 생성 성공! 🎨")
    return response.data[0].url