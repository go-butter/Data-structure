import time

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        if len(self.items) >= 10:
            print("\n[ PUSH 실패 ] 스택이 가득 찼습니다")
            return
        print(f"\n[ PUSH ] {item}")
        self.items.append(item)
        self.display()

    def pop(self):
        if self.is_empty():
            print("\n[ POP 실패 ] 스택이 비어있습니다")
            return None
        item = self.items.pop()
        print(f"\n[ POP ] {item}")
        self.display()
        return item

    def top(self):
        if self.is_empty():
            print("\n[ TOP ] 스택이 비어있습니다")
            return None
        print(f"\n[ TOP ] {self.items[-1]}")
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def display(self):
        print("\n--- STACK 상태 ---")
        for item in reversed(self.items):
            print(f"| {item} |")
        print("-------------")
        time.sleep(0.8)


def main():
    stack = Stack()

    words = [
        "벚꽃", "말차라떼", "연꽃",   
        "봄바람", "아메리카노", "튤립",
        "피크닉", "카페", "라일락"
    ]

    print("\n===== PUSH 시작 =====")
    for w in words:
        stack.push(w)

    stack.top()

    print("\n===== POP 시작 =====")
    stack.pop()
    stack.pop()

    stack.push("추가단어")

    stack.top()


if __name__ == "__main__":
    main()
