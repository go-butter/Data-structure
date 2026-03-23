import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── 설정 ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 30
import os, sys
if sys.platform == "win32":
    FONT_PATH = "C:/Windows/Fonts/malgun.ttf"   # 맑은 고딕 (Windows 기본 한글 폰트)
else:
    FONT_PATH = "/usr/share/fonts/opentype/unifont/unifont.otf"  # Linux fallback
OUTPUT_PATH = "20251223.mp4"

# ── 색상 (BGR은 cv2용, RGB는 PIL용) ──────────────────────────────────
BG_COLOR       = (245, 245, 250)   # 연한 배경
STACK_BG       = (255, 255, 255)   # 스택 박스 배경
STACK_BORDER   = (70, 130, 200)    # 스택 테두리 파란색
CELL_COLORS = [
    (255, 220, 220),  # 연분홍
    (220, 240, 255),  # 연하늘
    (220, 255, 220),  # 연초록
    (255, 255, 200),  # 연노랑
    (240, 220, 255),  # 연보라
    (255, 235, 210),  # 연주황
    (210, 255, 250),  # 연민트
    (255, 215, 215),  # 연빨강
    (230, 230, 255),  # 연라벤더
    (215, 245, 215),  # 연연두
]
TOP_HIGHLIGHT  = (255, 160, 50)    # top 포인터 색 (주황)
CODE_BG        = (30, 30, 50)      # 코드 패널 배경
CODE_TEXT_PUSH = (120, 220, 120)   # push → 초록
CODE_TEXT_POP  = (255, 120, 120)   # pop  → 빨강
CODE_TEXT_TOP  = (120, 200, 255)   # top  → 파랑
CODE_TEXT_DEF  = (230, 230, 230)   # 기본 텍스트
TITLE_COLOR    = (50, 80, 180)     # 제목
INFO_COLOR     = (80, 80, 120)     # 부가 정보

# ── 레이아웃 ──────────────────────────────────────────────────────────
STACK_LEFT   = 620   # 스택 그리기 시작 x
STACK_TOP    = 65    # 스택 상단 y
STACK_W      = 260   # 스택 너비
CELL_H       = 46    # 셀 높이
MAX_VISIBLE  = 10    # 최대 스택 크기
CODE_X       = 40    # 코드 패널 x
CODE_Y       = 100   # 코드 패널 y
CODE_W       = 530   # 코드 패널 너비
CODE_H       = 80    # 코드 패널 높이

# ── 연산 시퀀스 정의 ─────────────────────────────────────────────────
# (operation, word, member_name)
# operation: "declare" | "push" | "pop" | "top"
OPERATIONS = [
    # 3) stack 선언부터 시작
    ("declare", "",         ""),
    # 이유민: 벚꽃, 버터떡, 두쫀쿠
    ("push",    "벚꽃",     "이유민"),
    ("push",    "버터떡",   "이유민"),
    ("push",    "두쫀쿠",   "이유민"),
    # 김효린: 중간고사, 딸기라떼, 카공
    ("push",    "중간고사", "김효린"),
    ("push",    "딸기라떼", "김효린"),
    ("top",     "",         ""),        # top → 딸기라떼  (size=5)
    ("pop",     "",         ""),        # size=4
    ("push",    "카공",     "김효린"),
    # 이승주: 말차, 꽃구경, 아아
    ("push",    "말차",     "이승주"),
    ("push",    "꽃구경",   "이승주"),
    ("top",     "",         ""),        # top → 꽃구경  (size=7)
    ("pop",     "",         ""),        # size=6
    ("push",    "아아",     "이승주"),
    # 김태연: 핑크색, 커피 (벚꽃은 이미 있음)
    ("push",    "핑크색",   "김태연"),
    ("top",     "",         ""),        # top → 핑크색  (size=8)
    ("pop",     "",         ""),        # size=7
    ("push",    "커피",     "김태연"),
    # 유지민: 개나리 (버터떡·말차는 이미 있음)
    ("push",    "개나리",   "유지민"),
    # 이시현: 케이크 (벚꽃·두쫀쿠는 이미 있음)
    ("push",    "케이크",   "이시현"),
    ("top",     "",         ""),        # top → 케이크  (size=10)
    ("pop",     "",         ""),        # size=9
    ("pop",     "",         ""),        # size=8
    # 서지윤: 공부, 꽃 (케이크는 이미 있음)
    ("push",    "공부",     "서지윤"),
    ("push",    "꽃",       "서지윤"),
    ("top",     "",         ""),        # top → 꽃  (size=10)
    ("pop",     "",         ""),
    ("pop",     "",         ""),
    ("pop",     "",         ""),
]

# ── 폰트 로드 ─────────────────────────────────────────────────────────
def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)

# ── PIL → numpy (cv2용) ───────────────────────────────────────────────
def pil_to_cv2(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# ── 둥근 사각형 그리기 (PIL) ──────────────────────────────────────────
def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                           outline=outline, width=width)

# ── 코드 텍스트 색상 결정 ─────────────────────────────────────────────
def code_color(op):
    if op == "push":    return CODE_TEXT_PUSH
    if op == "pop":     return CODE_TEXT_POP
    if op == "top":     return CODE_TEXT_TOP
    return CODE_TEXT_DEF

# ── 한 프레임 그리기 ──────────────────────────────────────────────────
def draw_frame(stack, op, word, member, top_result=None, highlight_idx=None):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    f_title = load_font(34)
    f_code  = load_font(30)
    f_cell  = load_font(26)
    f_label = load_font(20)
    f_info  = load_font(22)

    # ── 제목 ──
    draw.text((40, 30), "Stack Animation", font=f_title, fill=TITLE_COLOR)
    draw.text((40, 70), "자료구조 스택 시각화", font=f_label, fill=INFO_COLOR)

    # ── 스택 외곽 박스 ──
    stack_bottom = STACK_TOP + CELL_H * MAX_VISIBLE + 10
    draw_rounded_rect(draw,
        (STACK_LEFT - 8, STACK_TOP - 8, STACK_LEFT + STACK_W + 8, stack_bottom),
        radius=12, fill=STACK_BG, outline=STACK_BORDER, width=3)

    # ── "Stack" 레이블 ──
    draw.text((STACK_LEFT + STACK_W // 2 - 25, stack_bottom + 6),
              "Stack", font=f_label, fill=STACK_BORDER)

    # ── 인덱스 선 (격자) ──
    for i in range(MAX_VISIBLE + 1):
        y = STACK_TOP + i * CELL_H
        draw.line([(STACK_LEFT, y), (STACK_LEFT + STACK_W, y)],
                  fill=(200, 200, 210), width=1)

    # ── 스택 셀 그리기 (아래에서 위로) ──
    for i, item in enumerate(stack):
        # i=0 이 bottom, i=len-1 이 top
        row = MAX_VISIBLE - 1 - i   # 화면 row (0=맨위)
        x0 = STACK_LEFT
        y0 = STACK_TOP + row * CELL_H
        x1 = STACK_LEFT + STACK_W
        y1 = y0 + CELL_H

        color = CELL_COLORS[i % len(CELL_COLORS)]
        is_top = (i == len(stack) - 1)
        is_highlight = (i == highlight_idx)

        cell_fill = color
        if is_highlight:
            cell_fill = (255, 200, 80)  # 하이라이트 노랑

        draw.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=cell_fill)

        # 텍스트
        bbox = draw.textbbox((0, 0), item, font=f_cell)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x0 + (STACK_W - tw) // 2, y0 + (CELL_H - th) // 2),
                  item, font=f_cell, fill=(40, 40, 80))

        # top 포인터 화살표
        if is_top:
            ax = STACK_LEFT + STACK_W + 15
            ay = y0 + CELL_H // 2
            draw.polygon([(ax, ay - 10), (ax, ay + 10), (ax + 22, ay)],
                         fill=TOP_HIGHLIGHT)
            draw.text((ax + 28, ay - 10), "← top", font=f_label, fill=TOP_HIGHLIGHT)

    # ── 스택 크기 표시 ──
    size_text = f"size: {len(stack)} / {MAX_VISIBLE}"
    draw.text((STACK_LEFT, stack_bottom + 28), size_text, font=f_label, fill=INFO_COLOR)

    # ── 코드 패널 ──
    draw_rounded_rect(draw,
        (CODE_X, CODE_Y, CODE_X + CODE_W, CODE_Y + CODE_H),
        radius=10, fill=CODE_BG)

    if op == "declare":
        code_str = "stack = Stack()  # 선언"
        color = CODE_TEXT_DEF
    elif op == "push":
        code_str = f'stack.push("{word}")'
        color = CODE_TEXT_PUSH
    elif op == "pop":
        code_str = "stack.pop()"
        color = CODE_TEXT_POP
    elif op == "top":
        code_str = f'stack.top()  →  "{top_result}"'
        color = CODE_TEXT_TOP
    else:
        code_str = ""
        color = CODE_TEXT_DEF

    bbox = draw.textbbox((0, 0), code_str, font=f_code)
    tw = bbox[2] - bbox[0]
    draw.text((CODE_X + (CODE_W - tw) // 2, CODE_Y + 22),
              code_str, font=f_code, fill=color)

    # ── 멤버 이름 표시 ──
    if member:
        draw.text((CODE_X, CODE_Y + CODE_H + 12),
                  f"📌 {member}", font=f_info, fill=(100, 100, 180))

    # ── 하단 팀원 단어 (2줄로 나눠서 표시) ──
    all_words_unique = [
        "벚꽃","버터떡","두쫀쿠","중간고사","딸기라떼","카공","말차","꽃구경",
        "아아","핑크색","커피","개나리","케이크","공부","꽃",
    ]
    half = len(all_words_unique) // 2
    line1 = "팀원 단어: " + " · ".join(all_words_unique[:half])
    line2 = "            " + " · ".join(all_words_unique[half:])
    draw.text((40, HEIGHT - 58), line1, font=f_label, fill=INFO_COLOR)
    draw.text((40, HEIGHT - 34), line2, font=f_label, fill=INFO_COLOR)

    return img


# ── 보간 프레임 생성 (push 슬라이드 인 / pop 슬라이드 아웃) ───────────
def slide_in_frames(stack_before, stack_after, op, word, member, n=15):
    """push: 위에서 아래로 슬라이드 인"""
    frames = []
    top_idx = len(stack_after) - 1
    for t in range(n):
        frac = (t + 1) / n
        frac = frac ** 0.5  # ease-out
        img = draw_frame(stack_after, op, word, member, highlight_idx=top_idx)
        # 새 셀에 alpha 효과 (밝기 조절로 대체)
        cv_img = pil_to_cv2(img)
        frames.append(cv_img)
    return frames

def slide_out_frames(stack_before, stack_after, op, word, member, n=15):
    frames = []
    for _ in range(n):
        img = draw_frame(stack_before, op, word, member)
        cv_img = pil_to_cv2(img)
        frames.append(cv_img)
    return frames

def still_frames(stack, op, word, member, top_result=None, n=FPS * 2):
    frames = []
    for _ in range(n):
        img = draw_frame(stack, op, word, member, top_result=top_result)
        frames.append(pil_to_cv2(img))
    return frames

# ── 스택 선언 애니메이션 ───────────────────────────────────────────────
def declare_animation_frames():
    """
    1단계 (20f): 배경·제목만
    2단계 (30f): 스택 외곽 박스 위→아래로 그려 내림
    3단계 (22f): 격자선 한 줄씩 등장
    4단계 (~25f): 코드 패널 등장 + 타이핑 효과
    5단계 (45f): 완성 정지
    """
    frames = []
    f_title = load_font(34)
    f_label = load_font(20)
    f_code  = load_font(30)

    stack_bottom = STACK_TOP + CELL_H * MAX_VISIBLE + 10
    full_box = (STACK_LEFT - 8, STACK_TOP - 8,
                STACK_LEFT + STACK_W + 8, stack_bottom)
    code_str = "stack = Stack()  # 선언"

    def base_img():
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        d = ImageDraw.Draw(img)
        d.text((40, 30), "Stack Animation", font=f_title, fill=TITLE_COLOR)
        d.text((40, 70), "자료구조 스택 시각화", font=f_label, fill=INFO_COLOR)
        return img, d

    def draw_full_grid(d):
        d.rounded_rectangle(list(full_box), radius=12,
                             fill=STACK_BG, outline=STACK_BORDER, width=3)
        d.text((STACK_LEFT + STACK_W // 2 - 25, stack_bottom + 6),
               "Stack", font=f_label, fill=STACK_BORDER)
        for j in range(MAX_VISIBLE + 1):
            y = STACK_TOP + j * CELL_H
            d.line([(STACK_LEFT, y), (STACK_LEFT + STACK_W, y)],
                   fill=(200, 200, 210), width=1)

    # 1단계: 배경·제목만 (20프레임)
    for _ in range(20):
        img, _ = base_img()
        frames.append(pil_to_cv2(img))

    # 2단계: 외곽 박스 위→아래로 (30프레임)
    total_h = full_box[3] - full_box[1]
    for t in range(30):
        frac = (t + 1) / 30
        frac = frac * frac * (3 - 2 * frac)  # smoothstep
        cur_h = int(total_h * frac)
        img, d = base_img()
        x0, y0, x1 = full_box[0], full_box[1], full_box[2]
        y1_cur = y0 + max(cur_h, 20)
        d.rounded_rectangle([x0, y0, x1, y1_cur],
                             radius=12, fill=STACK_BG, outline=STACK_BORDER, width=3)
        frames.append(pil_to_cv2(img))

    # 3단계: 격자선 한 줄씩 (2프레임/줄)
    for i in range(MAX_VISIBLE + 1):
        for _ in range(2):
            img, d = base_img()
            d.rounded_rectangle(list(full_box), radius=12,
                                 fill=STACK_BG, outline=STACK_BORDER, width=3)
            d.text((STACK_LEFT + STACK_W // 2 - 25, stack_bottom + 6),
                   "Stack", font=f_label, fill=STACK_BORDER)
            for j in range(i + 1):
                y = STACK_TOP + j * CELL_H
                d.line([(STACK_LEFT, y), (STACK_LEFT + STACK_W, y)],
                       fill=(200, 200, 210), width=1)
            frames.append(pil_to_cv2(img))

    # 4단계: 코드 패널 등장 + 타이핑 (글자 1~2개씩)
    chars_per_frame = max(1, len(code_str) // 20)
    char_idx = 0
    while char_idx <= len(code_str):
        img, d = base_img()
        draw_full_grid(d)
        d.text((STACK_LEFT, stack_bottom + 28),
               f"size: 0 / {MAX_VISIBLE}", font=f_label, fill=INFO_COLOR)
        d.rounded_rectangle([CODE_X, CODE_Y, CODE_X + CODE_W, CODE_Y + CODE_H],
                             radius=10, fill=CODE_BG)
        partial = code_str[:char_idx]
        if partial:
            d.text((CODE_X + 20, CODE_Y + 22), partial, font=f_code, fill=CODE_TEXT_DEF)
        # 커서
        bbox = d.textbbox((0, 0), code_str[:char_idx], font=f_code)
        cur_x = CODE_X + 20 + (bbox[2] - bbox[0])
        d.rectangle([cur_x + 2, CODE_Y + 22, cur_x + 14, CODE_Y + 52],
                    fill=(180, 180, 180))
        frames.append(pil_to_cv2(img))
        char_idx += chars_per_frame

    # 5단계: 완성 정지 (45프레임)
    for _ in range(45):
        img, d = base_img()
        draw_full_grid(d)
        d.text((STACK_LEFT, stack_bottom + 28),
               f"size: 0 / {MAX_VISIBLE}", font=f_label, fill=INFO_COLOR)
        d.rounded_rectangle([CODE_X, CODE_Y, CODE_X + CODE_W, CODE_Y + CODE_H],
                             radius=10, fill=CODE_BG)
        d.text((CODE_X + 20, CODE_Y + 22), code_str, font=f_code, fill=CODE_TEXT_DEF)
        frames.append(pil_to_cv2(img))

    return frames

# ── 메인 렌더링 ───────────────────────────────────────────────────────
def render():
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))

    stack = []

    for op, word, member in OPERATIONS:
        stack_before = stack[:]

        if op == "declare":
            for f in declare_animation_frames():
                out.write(f)

        elif op == "push":
            stack.append(word)
            # 짧은 슬라이드
            for f in slide_in_frames(stack_before, stack, op, word, member, n=12):
                out.write(f)
            # 정지 구간
            for f in still_frames(stack, op, word, member, n=FPS + 10):
                out.write(f)

        elif op == "pop":
            popped = stack[-1] if stack else ""
            # 정지 후 pop
            for f in still_frames(stack, op, word, member, n=12):
                out.write(f)
            stack.pop()
            for f in still_frames(stack, op, word, member, n=FPS + 5):
                out.write(f)

        elif op == "top":
            top_val = stack[-1] if stack else ""
            for f in still_frames(stack, op, word, member, top_result=top_val, n=FPS * 2):
                out.write(f)

    # 마지막 정지
    for f in still_frames(stack, "top", "", "", top_result=stack[-1] if stack else "", n=FPS * 2):
        out.write(f)

    out.release()
    print(f"✅ 영상 저장 완료: {OUTPUT_PATH}")
    print(f"   총 프레임 수 ≈ {out.get(cv2.CAP_PROP_FRAME_COUNT) if False else '계산 중'}")

if __name__ == "__main__":
    render()
