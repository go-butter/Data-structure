import csv
import os
import matplotlib.pyplot as plt

# 한글 깨짐 방지
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# 스택 그리기 함수
def draw_stack(stack, message):
    plt.clf()
    plt.title("Stack Animation", fontsize=16)

    # 현재 연산 표시
    plt.text(-3.5, 11, message, fontsize=12)

    # 스택 박스 그리기
    for i, item in enumerate(stack):
        rect = plt.Rectangle((0, i), 3, 1, fill=False, linewidth=1.5)
        plt.gca().add_patch(rect)
        plt.text(1.5, i + 0.5, item, ha="center", va="center", fontsize=11)

    # TOP 표시
    if stack:
        plt.text(3.3, len(stack) - 0.5, "← TOP", fontsize=12)

    plt.xlim(-4, 6)
    plt.ylim(0, 12)
    plt.axis("off")
    plt.pause(1)


# CSV 파일에서 단어 10개만 읽기
def load_words_from_csv():
    words = []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "words.csv")

    with open(csv_path, "r", encoding="cp949") as f:
        reader = csv.reader(f)
        next(reader)  # 헤더 건너뛰기

        for row in reader:
            if len(row) >= 5:
                words.extend(row[2:5])  # word1, word2, word3 추가

    return words[:10]  # 앞에서부터 10개만 사용


def main():
    words = load_words_from_csv()

    stack = []
    plt.figure(figsize=(8, 6))

    # stack 선언
    draw_stack(stack, "stack = []")

    # 처음 6개 push
    for w in words[:6]:
        stack.append(w)
        draw_stack(stack, f'push: "{w}"')

    # top
    if stack:
        top_item = stack[-1]
        draw_stack(stack, f'top: "{top_item}"')

    # pop 2번
    for _ in range(2):
        if stack:
            removed = stack.pop()
            draw_stack(stack, f"pop: {removed}")

    # 남은 단어 push
    for w in words[6:]:
        stack.append(w)
        draw_stack(stack, f'push: "{w}"')

    # 마지막 top
    if stack:
        top_item = stack[-1]
        draw_stack(stack, f'top: "{top_item}"')

    plt.show()


if __name__ == "__main__":
    main()