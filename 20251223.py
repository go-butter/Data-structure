import csv
import urllib.request
import io
import os, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
 
# ── 설정 ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 30
if sys.platform == "win32":
    FONT_PATH = "C:/Windows/Fonts/malgun.ttf"   # Windows
else:
    FONT_PATH = "/usr/share/fonts/opentype/unifont/unifont.otf"  # Linux fallback
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "20251223.mp4")
 
# ── GitHub CSV 연동 ───────────────────────────────────────────────────
CSV_URL = "https://raw.githubusercontent.com/go-butter/Data-structure/20251223/words.csv"
 
FALLBACK_DATA = [
    {"id": "20251223", "name": "이유민", "word1": "벚꽃",    "word2": "버터떡",  "word3": "두쫀쿠"},
    {"id": "20251193", "name": "김효린", "word1": "중간고사", "word2": "딸기라떼","word3": "카공"},
    {"id": "20251213", "name": "이승주", "word1": "말차",    "word2": "꽃구경",  "word3": "아아"},
    {"id": "20251191", "name": "김태연", "word1": "벚꽃",    "word2": "핑크색",  "word3": "커피"},
    {"id": "20251221", "name": "이예지", "word1": "벚꽃",    "word2": "아아",    "word3": "두쫀쿠"},
    {"id": "20251209", "name": "유지민", "word1": "버터떡",  "word2": "말차",    "word3": "개나리"},
    {"id": "20251217", "name": "이시현", "word1": "벚꽃",    "word2": "두쫀쿠",  "word3": "케이크"},
    {"id": "20251201", "name": "서지윤", "word1": "공부",    "word2": "케이크",  "word3": "꽃"},
]
 
def load_csv(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            raw = resp.read()
        # UTF-8 먼저 시도, 실패하면 EUC-KR
        try:
            content = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            content = raw.decode("euc-kr")
        reader = csv.DictReader(io.StringIO(content))
        rows = [{k.strip(): v.strip() for k, v in row.items()} for row in reader]
        print(f"✅ CSV 로드 성공 ({url}): {len(rows)}명")
        return rows
    except Exception as e:
        print(f"⚠️  CSV 로드 실패 ({e}) → 하드코딩 데이터 사용")
        return FALLBACK_DATA
 
# ── 연산 시퀀스 자동 생성 (중복 제거 + size ≤ 10) ────────────────────
def build_operations(members):
    ops = [("declare", "", "")]
    stack_sim = []
    seen = set()
 
    # 고유 단어 순서대로 추출
    unique_words = []
    for m in members:
        for key in ["word1", "word2", "word3"]:
            w = m[key]
            if w not in seen:
                seen.add(w)
                unique_words.append((w, m["name"]))
 
    push_count = 0
    for word, member in unique_words:
        # size 10이면 pop으로 자리 확보
        while len(stack_sim) >= 10:
            ops.append(("pop", "", ""))
            stack_sim.pop()
        # 4개마다 top 삽입
        if push_count > 0 and push_count % 4 == 0 and stack_sim:
            ops.append(("top", "", ""))
        ops.append(("push", word, member))
        stack_sim.append(word)
        push_count += 1
 
    # 마지막 top
    if stack_sim:
        ops.append(("top", "", ""))
    # 마무리 pop 3회
    for _ in range(min(3, len(stack_sim))):
        ops.append(("pop", "", ""))
        stack_sim.pop()
 
    # 검증
    sim, max_s = [], 0
    for op, w, _ in ops:
        if op == "push": sim.append(w); max_s = max(max_s, len(sim))
        elif op == "pop" and sim: sim.pop()
    assert max_s <= 10, f"스택 크기 초과: {max_s}"
    print(f"   연산 수: {len(ops)}, 최대 스택 크기: {max_s}")
    return ops
 
MEMBERS    = load_csv(CSV_URL)
OPERATIONS = build_operations(MEMBERS)
 
# 하단에 표시할 고유 단어 목록 (CSV에서 추출)
def get_unique_words(members):
    seen, words = set(), []
    for m in members:
        for key in ["word1", "word2", "word3"]:
            w = m[key]
            if w not in seen:
                seen.add(w); words.append(w)
    return words
 
UNIQUE_WORDS = get_unique_words(MEMBERS)
 
# ── 색상 ──────────────────────────────────────────────────────────────
BG_COLOR       = (245, 245, 250)
STACK_BG       = (255, 255, 255)
STACK_BORDER   = (70, 130, 200)
CELL_COLORS = [
    (255, 220, 220), (220, 240, 255), (220, 255, 220), (255, 255, 200),
    (240, 220, 255), (255, 235, 210), (210, 255, 250), (255, 215, 215),
    (230, 230, 255), (215, 245, 215),
]
TOP_HIGHLIGHT  = (255, 160, 50)
CODE_BG        = (30, 30, 50)
CODE_TEXT_PUSH = (120, 220, 120)
CODE_TEXT_POP  = (255, 120, 120)
CODE_TEXT_TOP  = (120, 200, 255)
CODE_TEXT_DEF  = (230, 230, 230)
TITLE_COLOR    = (50, 80, 180)
INFO_COLOR     = (80, 80, 120)
 
# ── 레이아웃 ──────────────────────────────────────────────────────────
STACK_LEFT  = 620
STACK_TOP   = 65
STACK_W     = 260
CELL_H      = 46
MAX_VISIBLE = 10
CODE_X      = 40
CODE_Y      = 100
CODE_W      = 530
CODE_H      = 80
 
# ── 폰트 로드 ─────────────────────────────────────────────────────────
def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)
 
def pil_to_cv2(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
 
def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                           outline=outline, width=width)
 
# ── 한 프레임 그리기 ──────────────────────────────────────────────────
def draw_frame(stack, op, word, member, top_result=None, highlight_idx=None):
    img  = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
 
    f_title = load_font(34)
    f_code  = load_font(30)
    f_cell  = load_font(26)
    f_label = load_font(20)
    f_info  = load_font(22)
 
    draw.text((40, 30), "Stack Animation",   font=f_title, fill=TITLE_COLOR)
    draw.text((40, 70), "자료구조 스택 시각화", font=f_label, fill=INFO_COLOR)
 
    stack_bottom = STACK_TOP + CELL_H * MAX_VISIBLE + 10
    draw_rounded_rect(draw,
        (STACK_LEFT-8, STACK_TOP-8, STACK_LEFT+STACK_W+8, stack_bottom),
        radius=12, fill=STACK_BG, outline=STACK_BORDER, width=3)
 
    draw.text((STACK_LEFT + STACK_W//2 - 25, stack_bottom + 6),
              "Stack", font=f_label, fill=STACK_BORDER)
 
    for i in range(MAX_VISIBLE + 1):
        y = STACK_TOP + i * CELL_H
        draw.line([(STACK_LEFT, y), (STACK_LEFT+STACK_W, y)], fill=(200,200,210), width=1)
 
    for i, item in enumerate(stack):
        row = MAX_VISIBLE - 1 - i
        x0  = STACK_LEFT
        y0  = STACK_TOP + row * CELL_H
        x1  = STACK_LEFT + STACK_W
        y1  = y0 + CELL_H
 
        cell_fill = CELL_COLORS[i % len(CELL_COLORS)]
        if i == highlight_idx:
            cell_fill = (255, 200, 80)
        draw.rectangle([x0+1, y0+1, x1-1, y1-1], fill=cell_fill)
 
        bbox = draw.textbbox((0,0), item, font=f_cell)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text((x0+(STACK_W-tw)//2, y0+(CELL_H-th)//2), item, font=f_cell, fill=(40,40,80))
 
        if i == len(stack) - 1:
            ax = STACK_LEFT + STACK_W + 15
            ay = y0 + CELL_H // 2
            draw.polygon([(ax, ay-10), (ax, ay+10), (ax+22, ay)], fill=TOP_HIGHLIGHT)
            draw.text((ax+28, ay-10), "← top", font=f_label, fill=TOP_HIGHLIGHT)
 
    draw.text((STACK_LEFT, stack_bottom+28),
              f"size: {len(stack)} / {MAX_VISIBLE}", font=f_label, fill=INFO_COLOR)
 
    draw_rounded_rect(draw,
        (CODE_X, CODE_Y, CODE_X+CODE_W, CODE_Y+CODE_H), radius=10, fill=CODE_BG)
 
    if   op == "declare": code_str, color = "stack = Stack()  # 선언", CODE_TEXT_DEF
    elif op == "push":    code_str, color = f'stack.push("{word}")',    CODE_TEXT_PUSH
    elif op == "pop":     code_str, color = "stack.pop()",              CODE_TEXT_POP
    elif op == "top":     code_str, color = f'stack.top()  →  "{top_result}"', CODE_TEXT_TOP
    else:                 code_str, color = "", CODE_TEXT_DEF
 
    bbox = draw.textbbox((0,0), code_str, font=f_code)
    tw   = bbox[2] - bbox[0]
    draw.text((CODE_X+(CODE_W-tw)//2, CODE_Y+22), code_str, font=f_code, fill=color)
 
    if member:
        draw.text((CODE_X, CODE_Y+CODE_H+12), f"📌 {member}", font=f_info, fill=(100,100,180))
 
    # ── 하단 팀원 단어 2줄 (CSV에서 자동 생성) ──
    half  = len(UNIQUE_WORDS) // 2
    line1 = "팀원 단어: " + " · ".join(UNIQUE_WORDS[:half])
    line2 = "            " + " · ".join(UNIQUE_WORDS[half:])
    draw.text((40, HEIGHT-58), line1, font=f_label, fill=INFO_COLOR)
    draw.text((40, HEIGHT-34), line2, font=f_label, fill=INFO_COLOR)
 
    return img
 
# ── 프레임 생성 헬퍼 ─────────────────────────────────────────────────
def slide_in_frames(stack_before, stack_after, op, word, member, n=12):
    top_idx = len(stack_after) - 1
    return [pil_to_cv2(draw_frame(stack_after, op, word, member, highlight_idx=top_idx))
            for _ in range(n)]
 
def still_frames(stack, op, word, member, top_result=None, n=FPS*2):
    return [pil_to_cv2(draw_frame(stack, op, word, member, top_result=top_result))
            for _ in range(n)]
 
# ── 스택 선언 애니메이션 ──────────────────────────────────────────────
def declare_animation_frames():
    frames = []
    f_title = load_font(34)
    f_label = load_font(20)
    f_code  = load_font(30)
 
    stack_bottom = STACK_TOP + CELL_H * MAX_VISIBLE + 10
    full_box = (STACK_LEFT-8, STACK_TOP-8, STACK_LEFT+STACK_W+8, stack_bottom)
    code_str = "stack = Stack()  # 선언"
 
    def base_img():
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        d   = ImageDraw.Draw(img)
        d.text((40, 30), "Stack Animation",   font=f_title, fill=TITLE_COLOR)
        d.text((40, 70), "자료구조 스택 시각화", font=f_label, fill=INFO_COLOR)
        return img, d
 
    def draw_full_grid(d):
        d.rounded_rectangle(list(full_box), radius=12, fill=STACK_BG, outline=STACK_BORDER, width=3)
        d.text((STACK_LEFT+STACK_W//2-25, stack_bottom+6), "Stack", font=f_label, fill=STACK_BORDER)
        for j in range(MAX_VISIBLE+1):
            y = STACK_TOP + j * CELL_H
            d.line([(STACK_LEFT, y), (STACK_LEFT+STACK_W, y)], fill=(200,200,210), width=1)
 
    # 1단계: 배경·제목 (20f)
    for _ in range(20):
        img, _ = base_img(); frames.append(pil_to_cv2(img))
 
    # 2단계: 박스 위→아래 (30f)
    total_h = full_box[3] - full_box[1]
    for t in range(30):
        frac = (t+1)/30; frac = frac*frac*(3-2*frac)
        img, d = base_img()
        x0, y0, x1 = full_box[0], full_box[1], full_box[2]
        d.rounded_rectangle([x0, y0, x1, y0+max(int(total_h*frac),20)],
                             radius=12, fill=STACK_BG, outline=STACK_BORDER, width=3)
        frames.append(pil_to_cv2(img))
 
    # 3단계: 격자선 한 줄씩 (2f/줄)
    for i in range(MAX_VISIBLE+1):
        for _ in range(2):
            img, d = base_img()
            d.rounded_rectangle(list(full_box), radius=12, fill=STACK_BG, outline=STACK_BORDER, width=3)
            d.text((STACK_LEFT+STACK_W//2-25, stack_bottom+6), "Stack", font=f_label, fill=STACK_BORDER)
            for j in range(i+1):
                y = STACK_TOP + j * CELL_H
                d.line([(STACK_LEFT,y),(STACK_LEFT+STACK_W,y)], fill=(200,200,210), width=1)
            frames.append(pil_to_cv2(img))
 
    # 4단계: 타이핑 효과
    chars_per_frame = max(1, len(code_str)//20)
    char_idx = 0
    while char_idx <= len(code_str):
        img, d = base_img(); draw_full_grid(d)
        d.text((STACK_LEFT, stack_bottom+28), f"size: 0 / {MAX_VISIBLE}", font=f_label, fill=INFO_COLOR)
        d.rounded_rectangle([CODE_X,CODE_Y,CODE_X+CODE_W,CODE_Y+CODE_H], radius=10, fill=CODE_BG)
        if char_idx: d.text((CODE_X+20, CODE_Y+22), code_str[:char_idx], font=f_code, fill=CODE_TEXT_DEF)
        bbox  = d.textbbox((0,0), code_str[:char_idx], font=f_code)
        cur_x = CODE_X + 20 + (bbox[2]-bbox[0])
        d.rectangle([cur_x+2, CODE_Y+22, cur_x+14, CODE_Y+52], fill=(180,180,180))
        frames.append(pil_to_cv2(img))
        char_idx += chars_per_frame
 
    # 5단계: 완성 정지 (45f)
    for _ in range(45):
        img, d = base_img(); draw_full_grid(d)
        d.text((STACK_LEFT, stack_bottom+28), f"size: 0 / {MAX_VISIBLE}", font=f_label, fill=INFO_COLOR)
        d.rounded_rectangle([CODE_X,CODE_Y,CODE_X+CODE_W,CODE_Y+CODE_H], radius=10, fill=CODE_BG)
        d.text((CODE_X+20, CODE_Y+22), code_str, font=f_code, fill=CODE_TEXT_DEF)
        frames.append(pil_to_cv2(img))
 
    return frames
 
# ── 메인 렌더링 ───────────────────────────────────────────────────────
def render():
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out    = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))
    stack  = []
 
    for op, word, member in OPERATIONS:
        stack_before = stack[:]
 
        if op == "declare":
            for f in declare_animation_frames(): out.write(f)
 
        elif op == "push":
            stack.append(word)
            for f in slide_in_frames(stack_before, stack, op, word, member): out.write(f)
            for f in still_frames(stack, op, word, member, n=FPS+10):        out.write(f)
 
        elif op == "pop":
            for f in still_frames(stack, op, word, member, n=12): out.write(f)
            stack.pop()
            for f in still_frames(stack, op, word, member, n=FPS+5): out.write(f)
 
        elif op == "top":
            top_val = stack[-1] if stack else ""
            for f in still_frames(stack, op, word, member, top_result=top_val, n=FPS*2): out.write(f)
 
    # 마지막 정지
    for f in still_frames(stack, "top", "", "", top_result=stack[-1] if stack else "", n=FPS*2):
        out.write(f)
 
    out.release()
    abs_path = os.path.abspath(OUTPUT_PATH)
    print(f"✅ 영상 저장 완료: {abs_path}")
 
    # 저장된 폴더를 탐색기에서 열고 영상 재생
    if sys.platform == "win32":
        os.startfile(abs_path)                          # 기본 플레이어로 영상 재생
        import subprocess
        subprocess.Popen(f'explorer /select,"{abs_path}"')  # 탐색기에서 파일 선택
 
if __name__ == "__main__":
    render()