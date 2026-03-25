import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
import imageio_ffmpeg

# ffmpeg 경로 설정
plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()

# 폰트
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 단어
all_words = [
    "벚꽃", "버터떡", "두쫀쿠", "중간고사", "딸기라떼", "카공",
    "말차", "꽃구경", "아아", "벚꽃", "핑크색", "커피", "벚꽃",
    "아아", "두쫀쿠", "버터떡", "말차", "개나리", "벚꽃",
    "두쫀쿠", "케이크", "공부", "케이크", "꽃"
]

# 스택 시나리오
steps = []
temp_stack = []

for i, word in enumerate(all_words):
    steps.append(("push", word))
    temp_stack.append(word)

    if i % 6 == 3 and len(temp_stack) >= 2:
        for _ in range(2):
            popped = temp_stack.pop()
            steps.append(("pop", popped))

    if i % 10 == 5 and len(temp_stack) >= 3:
        for _ in range(3):
            popped = temp_stack.pop()
            steps.append(("pop", popped))

    while len(temp_stack) > 5:
        popped = temp_stack.pop()
        steps.append(("pop", popped))

    if len(temp_stack) >= 2:
        steps.append(("top", ""))

while temp_stack:
    popped = temp_stack.pop()
    steps.append(("pop", popped))

# 그래프
fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')

def update(i):
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # 바깥 테두리 (파란색)
    border = plt.Rectangle((0.1, 0.5), 9.8, 11,
                           fill=False, edgecolor='#00B0F0', lw=4)
    ax.add_patch(border)

    temp_stack = []
    current_action = ""

    for j in range(i + 1):
        act, val = steps[j]

        if act == "push":
            temp_stack.append(val)
            current_action = f'stack.push("{val}")'

        elif act == "pop":
            if temp_stack:
                popped = temp_stack.pop()
            else:
                popped = "null"
            current_action = f'stack.pop("{popped}")'

        elif act == "top":
            val_top = temp_stack[-1] if temp_stack else "null"
            current_action = f'stack.top() -> "{val_top}"'

    # 코드 표시
    ax.text(0.5, 6, current_action,
            fontsize=26, fontweight='bold', color='black')

    # 스택 박스 (검정)
    box_x, box_width, box_height = 6.2, 3.0, 1.2

    for idx, item in enumerate(temp_stack):
        rect = plt.Rectangle(
            (box_x, 1.5 + idx * 1.3),
            box_width, box_height,
            fill=False, edgecolor='black', lw=2
        )
        ax.add_patch(rect)

        ax.text(
            box_x + box_width/2,
            1.5 + idx * 1.3 + box_height/2,
            item,
            ha='center', va='center',
            fontsize=16, color='black'
        )

# ⭐ 바닥선 코드 완전히 삭제됨

# 애니메이션
ani = animation.FuncAnimation(
    fig, update,
    frames=len(steps),
    interval=600,
    repeat=False
)

# mp4 저장
writer = FFMpegWriter(fps=2)
ani.save("stack_max5.mp4", writer=writer)

plt.tight_layout()
plt.show()