import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# =========================
# 데이터
# =========================
words = [
"벚꽃","버터떡","두쫀쿠","중간고사","딸기라떼","카공",
"말차","꽃구경","아아","벚꽃","핑크색","커피","벚꽃",
"아아","두쫀쿠","버터떡","말차","개나리","벚꽃",
"두쫀쿠","케이크","공부","케이크","꽃"
]

# =========================
# 설정
# =========================
WIDTH, HEIGHT = 800, 500
FPS = 2
MAX_STACK = 10

# 폰트
font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 24)

# ✅ AVI + XVID (가장 안정적)
video = cv2.VideoWriter(
    "stack_animation.avi",
    cv2.VideoWriter_fourcc(*'XVID'),
    FPS,
    (WIDTH, HEIGHT)
)

stack = []

# =========================
# 화면 그리기
# =========================
def draw_frame(text, stack):
    img = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)

    # 🔵 파란 테두리
    margin = 20
    draw.rectangle(
        (margin, margin, WIDTH - margin, HEIGHT - margin),
        outline=(255, 180, 120),
        width=4
    )

    # 텍스트
    draw.text((50, 80), text, font=font, fill=(0,0,0))

    # 스택
    x, y = 450, 100
    w, h = 200, 40

    for i, item in enumerate(reversed(stack)):
        yy = y + i*h
        draw.rectangle((x, yy, x+w, yy+h), outline=(0,0,0))
        draw.text((x+10, yy+10), item, font=font, fill=(0,0,0))

    return np.array(img_pil)

# =========================
# 애니메이션
# =========================
for word in words:
    if len(stack) < MAX_STACK:
        stack.append(word)
        video.write(draw_frame(f'stack.push("{word}")', stack))

    if len(stack) >= 5:
        popped = stack.pop()
        video.write(draw_frame(f'stack.pop() -> "{popped}"', stack))

if stack:
    video.write(draw_frame(f'stack.top() -> "{stack[-1]}"', stack))

video.release()

print("✅ AVI 영상 생성 완료 (이 파일로 제출 가능)")