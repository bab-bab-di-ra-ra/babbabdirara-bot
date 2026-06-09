import requests

from openai import OpenAI

# ── 이미지 생성용 프롬프트 빌드 ────────────────────────────
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

IMPORTANT: Do NOT include any text, letters, words, captions, labels, numbers,
or writing anywhere in the image. The image must contain zero text.
"""

# ── imgbb 업로드 (base64 또는 이미지 URL → 정적 URL) ───────
def upload_to_imgbb(image_data, imgbb_key):
    """base64 또는 이미지 URL을 imgbb에 올리고 정적 이미지 URL을 반환한다. 실패 시 None.

    imgbb의 image 필드는 base64뿐 아니라 이미지 URL도 받아 알아서 다시 호스팅한다.
    """
    try:
        res = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": imgbb_key},
            data={"image": image_data},
            timeout=60,
        )
        res.raise_for_status()
        url = res.json()["data"]["url"]
        print(f"imgbb 업로드 완료: {url}")
        return url
    except Exception as e:
        print(f"imgbb 업로드 실패(이미지 없이 진행): {e}")
        return None

# ── gpt-image-1로 식단 이미지 생성 후 imgbb 호스팅 ─────────
def generate_food_image(menu_list, openai_key, imgbb_key):
    """식단 이미지를 생성해 imgbb에 올린 뒤 정적 URL을 반환한다.

    base64를 카드에 직접 박으면 Teams 카드 크기 한도(약 28KB)를 넘겨 메시지가
    조용히 사라지므로, gpt-image-1이 돌려준 base64를 imgbb에 올려 정적 URL만 카드에 넣는다.

    이미지 생성/업로드가 실패하면 None을 반환해 카드에서 이미지 블록을 생략한다.
    """
    if not imgbb_key:
        print("imgbb 키가 없어 이미지 없이 진행")
        return None

    prompt = build_image_prompt(menu_list)
    client = OpenAI(api_key=openai_key)

    try:
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt.strip(),
            size="1536x1024",        # 가로형 식판
            quality="low",           # 비용/생성속도 절약
        )
        print("이미지 생성 성공! 🎨")
    except Exception as e:
        print(f"이미지 생성 실패(이미지 없이 진행): {e}")
        return None

    b64 = result.data[0].b64_json
    if not b64:
        print("이미지 생성 결과가 비어 있음(이미지 없이 진행)")
        return None

    return upload_to_imgbb(b64, imgbb_key)
