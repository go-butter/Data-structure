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

import time
import os

class Stack:
    def __init__(self):
        self.items = []

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display(self, action=""):
        self.clear_screen()
        print(f"\n=== {action} ===\n")

        print("STACK (위가 top)\n")
        for item in reversed(self.items):
            print(f"| {item} |")
            print("-------")

        if not self.items:
            print("(empty)")

        time.sleep(1)

    def push(self, item):
        self.items.append(item)
        self.display(f"PUSH → {item}")

    def pop(self):
        if self.items:
            item = self.items.pop()
            self.display(f"POP → {item}")
            return item
        else:
            self.display("POP 실패 (빈 스택)")

    def top(self):
        if self.items:
            self.display(f"TOP → {self.items[-1]}")
        else:
            self.display("TOP 없음")


stack = Stack()

words = ["벚꽃", "카페", "라떼", "봄바람", "튤립"]

for w in words:
    stack.push(w)

stack.top()

stack.pop()
stack.pop()

stack.push("피크닉")

stack.top()
