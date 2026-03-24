#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <chrono>

using namespace std;

// 스택의 데이터를 담을 전역/멤버 변수 역할 (파이썬의 stack = [] 과 동일)
vector<string> stack_data;

// 한글 글자 수를 고려하여 여백을 맞추는 간단한 함수
int getPadSize(const string& str, int total_width) {
    int len = 0;
    for (char c : str) {
        if (c & 0x80) len += 2; // 한글 등 다바이트 문자는 2칸으로 계산
        else len += 1;          // 영어/공백/숫자는 1칸
    }
    // UTF-8 환경에 따라 계산 오차가 있을 수 있으므로 보정
    int pad = total_width - (len / 3 * 2); // 대략적인 한글 3바이트->2칸 비율 계산
    return pad > 0 ? pad : 0;
}

// 스택 그리기 함수 (파이썬의 draw_stack 역할)
void draw_stack() {
    cout << "\n=== Stack Animation ===\n";

    if (stack_data.empty()) {
        cout << "     (스택 비어있음)\n\n";
        return;
    }

    // Top에서 Bottom 순서로 출력 (인덱스 역순)
    for (int i = stack_data.size() - 1; i >= 0; i--) {
        cout << "     ┌──────────┐\n";

        // 글자 정렬을 위한 임시 패딩 (대략적인 가운데 정렬 흉내)
        cout << "     │  " << stack_data[i] << "  │";

        // Top, Bottom 표시
        if (i == stack_data.size() - 1 && stack_data.size() == 1) {
            cout << " ← top & bottom";
        }
        else if (i == stack_data.size() - 1) {
            cout << " ← top";
        }
        else if (i == 0) {
            cout << " ← bottom";
        }
        cout << "\n";
        cout << "     └──────────┘\n";
    }
    cout << "=======================\n\n";
}

int main() {
    // 파이썬 코드의 words 리스트
    vector<string> words = {
        "벚꽃", "버터떡", "두쫀쿠",
        "중간고사", "딸기라떼", "카공",
        "말차", "꽃구경", "아아"
    };

    // 애니메이션 단계 정의 (action, value)
    vector<pair<string, string>> steps;

    // 1. 처음 5개 push
    for (int i = 0; i < 5; i++) {
        steps.push_back({ "push", words[i] });
    }

    // 2. top 확인
    steps.push_back({ "top", "" });

    // 3. pop 2번
    steps.push_back({ "pop", "" });
    steps.push_back({ "pop", "" });

    // 4. 나머지 push
    for (size_t i = 5; i < words.size(); i++) {
        steps.push_back({ "push", words[i] });
    }

    // update 및 애니메이션 실행 로직
    for (size_t frame = 0; frame < steps.size(); frame++) {
        string action = steps[frame].first;
        string value = steps[frame].second;

        // 화면을 지우고 싶다면 아래 주석을 해제하세요. (Mac/Linux는 "clear")
        // system("cls"); 

        if (action == "push") {
            stack_data.push_back(value); // 파이썬의 stack.append()
            cout << "[Frame " << frame + 1 << "] push: " << value << endl;
        }
        else if (action == "pop") {
            if (!stack_data.empty()) {
                string removed = stack_data.back();
                stack_data.pop_back(); // 파이썬의 stack.pop()
                cout << "[Frame " << frame + 1 << "] pop: " << removed << endl;
            }
        }
        else if (action == "top") {
            if (!stack_data.empty()) {
                cout << "[Frame " << frame + 1 << "] top: " << stack_data.back() << endl;
            }
        }

        // 스택 상태 출력 (파이썬의 draw_stack())
        draw_stack();

        // 1초(1000ms) 대기 (파이썬의 interval=1000 역할)
        this_thread::sleep_for(chrono::milliseconds(1000));
    }

    return 0;
}
