# code/pathfinding.py
import pygame
from collections import deque
import time
from settings import MAP_COLS, MAP_ROWS # Import kích thước map

def get_path_bfs(start, target, obstacles):
    # 1. Kiểm tra an toàn đầu vào
    if start == target: return [start], 0, 0
    if target in obstacles: 
        return [], 0, 0 # Nếu đích là tường, không tìm nữa

    start_time = time.time()
    queue = deque([start])
    visited = {start: None}
    nodes_expanded = 0
    max_nodes = 2000 # Lớp bảo vệ chống treo máy (Safety Break)

    while queue:
        current = queue.popleft()
        nodes_expanded += 1
        
        # Nếu duyệt quá nhiều ô mà không thấy đích (có thể map bị hở)
        if nodes_expanded > max_nodes:
            break

        if current == target:
            break

        # Duyệt 4 hướng
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            # KIỂM TRA BIÊN: Quan trọng nhất để không bị đơ
            if 0 <= neighbor[0] < MAP_COLS and 0 <= neighbor[1] < MAP_ROWS:
                if neighbor not in obstacles and neighbor not in visited:
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

    exec_time = (time.time() - start_time) * 1000
    return path, nodes_expanded, exec_time