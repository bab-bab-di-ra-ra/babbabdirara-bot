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
"""

# ── imgbb 업로드 (base64 → 정적 URL) ───────────────────────
def upload_to_imgbb(b64, imgbb_key):
    """base64 이미지를 imgbb에 올리고 정적 이미지 URL을 반환한다. 실패 시 None."""
    try:
        res = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": imgbb_key},
            data={"image": b64},
            timeout=60,
        )
        res.raise_for_status()
        url = res.json()["data"]["url"]
        print(f"imgbb 업로드 완료: {url}")
        return url
    except Exception as e:
        print(f"imgbb 업로드 실패(이미지 없이 진행): {e}")
        return None

# ── DALL·E 3로 식단 이미지 생성 후 imgbb 호스팅 ────────────
def generate_food_image(menu_list, openai_key, imgbb_key):
    """식단 이미지를 생성해 imgbb에 올린 뒤 정적 URL을 반환한다.

    base64를 카드에 직접 박으면 Teams 카드 크기 한도(약 28KB)를 넘겨 메시지가
    조용히 사라지므로, 외부 호스트(imgbb)에 올린 '완성된 정적 URL'만 카드에 넣는다.
    DALL·E 3 자체도 URL을 주지만 그 URL은 약 1~2시간 뒤 만료되므로, 영구 보관되는
    imgbb URL을 쓴다. (DALL·E 3는 조직 verified 없이도 호출돼 403 위험이 없다.)

    이미지 생성/업로드가 실패하면 None을 반환해 카드에서 이미지 블록을 생략한다.
    """
    if not imgbb_key:
        print("imgbb 키가 없어 이미지 없이 진행")
        return None

    prompt = build_image_prompt(menu_list)
    client = OpenAI(api_key=openai_key)

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt.strip(),
            size="1024x1024",
            quality="standard",
            response_format="b64_json",   # URL 대신 base64로 받아 imgbb에 올림
            n=1,
        )
        print("이미지 생성 성공! 🎨")
    except Exception as e:
        print(f"이미지 생성 실패(이미지 없이 진행): {e}")
        return None

    b64 = response.data[0].b64_json
    if not b64:
        print("이미지 생성 결과가 비어 있음(이미지 없이 진행)")
        return None

    return upload_to_imgbb(b64, imgbb_key)
