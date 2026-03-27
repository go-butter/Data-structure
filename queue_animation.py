import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import matplotlib.patches as patches
import platform

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'

plt.rcParams['axes.unicode_minus'] = False

menu_data = [
    "카푸치노", "카페라떼", "피넛라떼", "말차라떼", "초코라떼", "레몬티",
    "자몽티", "카페모카", "매실티", "얼그레이티", "스콘", "레몬티",
    "레몬티", "카푸치노", "초코 스콘", "매실티", "페퍼민트티", "휘낭시에",
    "딸기라떼", "딸기에이드", "망고에이드", "스콘", "청포도에이드", "매실티",
    "카페라떼", "말차라떼", "카푸치노", "캐모마일티", "초코 스콘", "레몬티",
    "디카페인 아메리카노"
]

sim_history = []
main_queue = deque()

# 인트로 프레임 
for _ in range(3):
    sim_history.append(("INTRO", [], "큐 애니메이션 시작"))

# 2. Queue Operation 시뮬레이션 로직 수행
for i, item in enumerate(menu_data):
    # 특정 시점에서의 연속 Dequeue 테스트 
    if i == 10:
        for _ in range(5):
            if main_queue:
                main_queue.popleft()
                sim_history.append(("카페무솔트.dequeue()", list(main_queue), ""))

    # 큐 사이즈가 10을 초과할 경우 선입선출 적용
    if len(main_queue) >= 10:
        main_queue.popleft()
        sim_history.append(("카페무솔트.dequeue()", list(main_queue), ""))
    
    # Enqueue 연산 수행
    main_queue.append(item)
    sim_history.append((f"카페무솔트.enqueue(\"{item}\")", list(main_queue), ""))

    # 주요 ADT 메서드 호출 시뮬레이션
    if i == 5: 
        front_val = main_queue[0] if main_queue else "None"
        sim_history.append(("카페무솔트.front()", list(main_queue), f"결과: {front_val}"))
    
    if i == 15: 
        sim_history.append(("카페무솔트.isEmpty()", list(main_queue), "결과: False"))
    
    if i == 25: 
        main_queue.clear()
        sim_history.append(("카페무솔트.clear()", list(main_queue), ""))

# Matplotlib 시각화 및 애니메이션 설정
fig, ax = plt.subplots(figsize=(12, 8))

def update_frame(n):
    ax.clear()
    method_name, current_state, result_note = sim_history[n]
    
    # 캔버스 외곽 레이아웃 
    border = patches.Rectangle((0.01, 0.01), 0.98, 0.98, linewidth=4, edgecolor='#00AEEF', 
                               facecolor='none', transform=ax.transAxes, zorder=1)
    ax.add_patch(border)

    # 인트로 시퀀스 렌더링
    if method_name == "INTRO":
        ax.text(0.5, 0.5, result_note, ha='center', va='center', fontsize=35, 
                fontweight='bold', color='black', transform=ax.transAxes)
        ax.axis('off')
        return

    # 우측 상단 타이틀 
    header_box = patches.Rectangle((0.65, 0.915), 0.34, 0.075, linewidth=2, 
                                   edgecolor='black', facecolor='white', transform=ax.transAxes, zorder=2)
    ax.add_patch(header_box)
    ax.text(0.82, 0.95, "카페무솔트", ha='center', va='center', fontsize=20, 
            fontweight='bold', color='black', transform=ax.transAxes, zorder=3)
    
    # 메서드 호출 코드 출력 
    ax.text(0.06, 0.5, method_name, fontsize=20, fontweight='bold', color='black', 
            transform=ax.transAxes, ha='left', va='center')
    
    # 메서드 반환값 출력 
    if result_note:
        ax.text(0.06, 0.4, result_note, fontsize=22, fontweight='bold', color='black', 
                transform=ax.transAxes, ha='left', va='center')

    # Queue 데이터 요소 렌더링 
    el_w, el_h, el_gap = 0.35, 0.06, 0.015
    start_x, start_y = 0.62, 0.08
    
    for idx, element in enumerate(current_state):
        element_rect = patches.Rectangle((start_x, start_y + (idx * (el_h + el_gap))), el_w, el_h, 
                                         linewidth=1.5, edgecolor='black', facecolor='#F9F9F9', transform=ax.transAxes)
        ax.add_patch(element_rect)
        ax.text(start_x + el_w/2, start_y + (idx * (el_h + el_gap)) + el_h/2, element, 
                ha='center', va='center', fontsize=14, color='black', fontweight='medium', transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

# 애니메이션 생성 및 MP4 파일 내보내기
ani = animation.FuncAnimation(fig, update_frame, frames=len(sim_history), interval=800, repeat=False)

output_path = 'cafe_queue_simulation_v2.mp4'

try:
    print(f"Status: Exporting video to {output_path}...")
    video_writer = animation.FFMpegWriter(fps=1.2, bitrate=3000) 
    ani.save(output_path, writer=video_writer)
    print("Status: Video export completed successfully.")
except Exception as error:
    print(f"Status: Error occurred during export - {error}")

plt.show()