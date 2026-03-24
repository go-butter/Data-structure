import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

plt.rcParams["animation.ffmpeg_path"] = r"C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

# 한글 출력 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

MAX_STACK_SIZE = 10


def load_words_from_csv():
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "words.csv"

    words = []

    if not csv_path.exists():
        return [
            "벚꽃", "라떼", "산책",
            "새싹", "케이크", "햇살",
            "꽃잎", "아메리카노", "피크닉",
            "공원"
        ]

    encodings = ["utf-8-sig", "cp949"]

    for enc in encodings:
        try:
            with open(csv_path, "r", encoding=enc, newline="") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 5:
                        words.extend(row[2:5])
            return words
        except UnicodeDecodeError:
            words = []
            continue

    raise UnicodeDecodeError(
        "words.csv", b"", 0, 1,
        "지원되지 않는 인코딩입니다. UTF-8 또는 CP949로 저장해 주세요."
    )


def generate_frames(words):
    frames = []
    stack = []

    frames.append((stack.copy(), "초기 상태: stack = []"))

    for i, word in enumerate(words):
        frames.append((stack.copy(), f'push 준비: "{word}"'))

        if len(stack) < MAX_STACK_SIZE:
            stack.append(word)
            frames.append((stack.copy(), f'push 실행: "{word}"'))
        else:
            frames.append((stack.copy(), f'overflow: "{word}" 추가 불가'))

        if stack and (i % 3 == 1):
            frames.append((stack.copy(), f'top 확인: "{stack[-1]}"'))

        if len(stack) >= 8:
            removed = stack.pop()
            frames.append((stack.copy(), f'pop 실행: "{removed}"'))

    if stack:
        frames.append((stack.copy(), f'마지막 top: "{stack[-1]}"'))

    while stack:
        removed = stack.pop()
        frames.append((stack.copy(), f'마무리 pop: "{removed}"'))

    frames.append((stack.copy(), "종료"))
    return frames


def draw_frame(frame):
    stack, message = frame

    ax = plt.gca()
    ax.clear()

    ax.set_title("Stack Animation", fontsize=16, pad=16)

    ax.text(-4.4, 11.2, f"현재 연산: {message}", fontsize=12)
    ax.text(-4.4, 10.4, "자료구조: Stack / LIFO (Last In, First Out)", fontsize=10)

    code_lines = [
        "stack = []",
        "stack.append(x)   # push",
        "stack.pop()       # pop",
        "stack[-1]         # top",
    ]
    y0 = 8.8
    for idx, line in enumerate(code_lines):
        ax.text(-4.4, y0 - idx * 0.7, line, fontsize=10, family="monospace")

    for i, item in enumerate(stack):
        is_top = (i == len(stack) - 1)

        box = Rectangle(
            (0, i), 3.2, 1.0,
            facecolor="#FDBA74" if is_top else "#BFDBFE",
            edgecolor="black",
            linewidth=1.5
        )
        ax.add_patch(box)
        ax.text(1.6, i + 0.5, item, ha="center", va="center", fontsize=11)

    if stack:
        ax.text(3.5, len(stack) - 0.5, "← TOP", fontsize=12, va="center")

    ax.set_xlim(-4.8, 6.5)
    ax.set_ylim(0, 12)
    ax.axis("off")


def main():
    ffmpeg_path = Path(plt.rcParams["animation.ffmpeg_path"])
    if not ffmpeg_path.exists():
        raise FileNotFoundError(f"ffmpeg.exe 경로를 찾을 수 없음: {ffmpeg_path}")

    words = load_words_from_csv()
    frames = generate_frames(words)

    fig = plt.figure(figsize=(9, 6))
    ani = animation.FuncAnimation(
        fig,
        draw_frame,
        frames=frames,
        interval=1000,
        repeat=False
    )

    base_dir = Path(__file__).resolve().parent
    output_path = base_dir / "stack_animation.mp4"

    writer = animation.FFMpegWriter(fps=1)
    ani.save(str(output_path), writer=writer)

    plt.close(fig)
    print(f"MP4 생성 완료: {output_path}")


if __name__ == "__main__":
    main()