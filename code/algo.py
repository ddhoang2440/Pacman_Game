# code/pathfinding.py
import pygame
from collections import deque
import time

def get_path_bfs(start, target, obstacles):
    # start, target là tọa độ ô (x, y) - ví dụ: (5, 10)
    # obstacles là danh sách các tọa độ ô có tường
    
    start_time = time.time()
    queue = deque([start])
    visited = {start: None} # Lưu node đã đi và node cha của nó
    nodes_expanded = 0

    while queue:
        current = queue.popleft()
        nodes_expanded += 1

        if current == target:
            break

        # Duyệt 4 hướng: Lên, Xuống, Trái, Phải
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if neighbor not in obstacles and neighbor not in visited:
                # Kiểm tra biên nếu cần (thường Tiled đã bao tường xung quanh)
                visited[neighbor] = current
                queue.append(neighbor)

    # Truy vết lại đường đi
    path = []
    if target in visited:
        curr = target
        while curr is not None:
            path.append(curr)
            curr = visited[curr]
        path.reverse()

    exec_time = (time.time() - start_time) * 1000 # Đổi sang ms
    return path, nodes_expanded, exec_time