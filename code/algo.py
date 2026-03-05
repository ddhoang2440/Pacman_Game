# code/pathfinding.py
# code/pathfinding.py
import pygame
from collections import deque
import time
import heapq # Dùng cho A*
from settings import MAP_COLS, MAP_ROWS

def get_neighbors(pos, obstacles):
    neighbors = []
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        neighbor = (pos[0] + dx, pos[1] + dy)
        if 0 <= neighbor[0] < MAP_COLS and 0 <= neighbor[1] < MAP_ROWS:
            if neighbor not in obstacles:
                neighbors.append(neighbor)
    return neighbors

# --- 1. BFS (Giữ nguyên của bạn) ---
def get_path_bfs(start, target, obstacles):
    if start == target: return [start], 0, 0
    start_time = time.time()
    queue = deque([start])
    visited = {start: None}
    nodes = 0
    while queue:
        current = queue.popleft()
        nodes += 1
        if nodes > 2000 or current == target: break
        for nxt in get_neighbors(current, obstacles):
            if nxt not in visited:
                visited[nxt] = current
                queue.append(nxt)
    return reconstruct_path(visited, start, target, start_time, nodes)

# --- 2. DFS (Tìm kiếm theo chiều sâu) ---
def get_path_dfs(start, target, obstacles):
    start_time = time.time()
    stack = [start]
    visited = {start: None}
    nodes = 0
    while stack:
        current = stack.pop() # LIFO
        nodes += 1
        if nodes > 2000 or current == target: break
        for nxt in get_neighbors(current, obstacles):
            if nxt not in visited:
                visited[nxt] = current
                stack.append(nxt)
    return reconstruct_path(visited, start, target, start_time, nodes)

# --- 3. A* (Thông minh nhất - BFS + Heuristic) ---
def get_path_astar(start, target, obstacles):
    start_time = time.time()
    def heuristic(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1]) # Manhattan
    
    pq = [(0, start)] # (priority, node)
    visited = {start: None}
    g_score = {start: 0}
    nodes = 0
    
    while pq:
        _, current = heapq.heappop(pq)
        nodes += 1
        if nodes > 2000 or current == target: break
        
        for nxt in get_neighbors(current, obstacles):
            new_g = g_score[current] + 1
            if nxt not in g_score or new_g < g_score[nxt]:
                g_score[nxt] = new_g
                priority = new_g + heuristic(nxt, target)
                visited[nxt] = current
                heapq.heappush(pq, (priority, nxt))
                
    return reconstruct_path(visited, start, target, start_time, nodes)

# --- 4. Minimax (Rút gọn cho Ghost) ---
def get_path_minimax(start, target, obstacles):
    # Với Ghost, Minimax chọn hướng đi mà khoảng cách Manhattan là nhỏ nhất
    # sau khi giả định Pacman sẽ chạy ra xa nhất có thể.
    start_time = time.time()
    best_move = start
    min_eval = float('inf')
    
    for move in get_neighbors(start, obstacles):
        # Giả lập 1 bước: Ghost tiến tới 'move'
        # Tính khoảng cách tới Pacman
        d = abs(move[0] - target[0]) + abs(move[1] - target[1])
        if d < min_eval:
            min_eval = d
            best_move = move
            
    return [start, best_move], 4, (time.time() - start_time) * 1000

def reconstruct_path(visited, start, target, start_time, nodes):
    path = []
    if target in visited:
        curr = target
        while curr is not None:
            path.append(curr)
            curr = visited[curr]
        path.reverse()
    return path, nodes, (time.time() - start_time) * 1000