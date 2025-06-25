# algorithms.py

import heapq # A*算法需要用到优先队列(堆)
from collections import deque, namedtuple
from config import GRID_WIDTH, GRID_HEIGHT, GRID_SIZE

Point = namedtuple('Point', 'x, y')

# --- 算法1: A* 智能寻路 ---
def a_star_pathfinding(snake, food):
    """
    A* 算法，寻找从蛇头到食物的最高效路径。
    它结合了已走路径的成本和到目标的预估成本。
    """
    start_node = (int(snake[0].x / GRID_SIZE), int(snake[0].y / GRID_SIZE))
    end_node = (int(food.x / GRID_SIZE), int(food.y / GRID_SIZE))
    
    # 优先队列，存储 (优先级, 当前位置, 路径)
    # 优先级 = 已走步数 + 曼哈顿距离 (启发函数)
    queue = [(0, start_node, [])]
    visited = {start_node}

    # 蛇的身体是障碍物
    obstacles = {(int(p.x / GRID_SIZE), int(p.y / GRID_SIZE)) for p in snake}

    while queue:
        priority, current_pos, path = heapq.heappop(queue)

        if current_pos == end_node:
            return path # 找到路径

        (x, y) = current_pos
        neighbors = [((x, y - 1), 'UP'), ((x, y + 1), 'DOWN'), 
                     ((x - 1, y), 'LEFT'), ((x + 1, y), 'RIGHT')]

        for next_pos, direction in neighbors:
            if (0 <= next_pos[0] < GRID_WIDTH and
                0 <= next_pos[1] < GRID_HEIGHT and
                next_pos not in obstacles and
                next_pos not in visited):
                
                visited.add(next_pos)
                new_path = path + [direction]
                # g = len(new_path) # 已走成本
                # h = abs(next_pos[0] - end_node[0]) + abs(next_pos[1] - end_node[1]) # 预估成本
                # new_priority = g + h
                new_priority = len(new_path) + abs(next_pos[0] - end_node[0]) + abs(next_pos[1] - end_node[1])
                heapq.heappush(queue, (new_priority, next_pos, new_path))
    
    return None # 找不到路径

# --- 路径安全评估 ---
def is_path_safe(snake, food, path):
    """
    在“脑中”模拟走完这条路，判断吃掉食物后是否会陷入危险。
    """
    # 1. 模拟吃掉食物后的蛇
    future_snake_body = list(snake) # 复制当前蛇
    current_head = snake[0]

    for move in path:
        if move == 'UP': current_head = Point(current_head.x, current_head.y - GRID_SIZE)
        elif move == 'DOWN': current_head = Point(current_head.x, current_head.y + GRID_SIZE)
        elif move == 'LEFT': current_head = Point(current_head.x - GRID_SIZE, current_head.y)
        elif move == 'RIGHT': current_head = Point(current_head.x + GRID_SIZE, current_head.y)
        future_snake_body.insert(0, current_head)
    
    # 因为吃到了食物，所以不用pop尾巴，蛇变长了
    
    # 2. 计算吃完食物后，新蛇头的可用空间
    # 注意：此时的蛇头就是食物的位置
    future_head = food
    space = _calculate_space_size(future_head, future_snake_body)
    
    # 3. 判断：如果吃完后可用空间小于蛇长，说明很可能被困住，不安全！
    if space < len(future_snake_body):
        return False
        
    return True

# --- 算法2: 哈密顿循环 (无变化) ---
_hamiltonian_path = None
def get_hamiltonian_path():
    global _hamiltonian_path
    if _hamiltonian_path: return _hamiltonian_path
    path = {}
    for y in range(GRID_HEIGHT):
        if y % 2 == 0:
            for x in range(GRID_WIDTH - 1): path[(x, y)] = 'RIGHT'
            path[(GRID_WIDTH - 1, y)] = 'DOWN' if y < GRID_HEIGHT - 1 else 'LEFT'
        else:
            for x in range(GRID_WIDTH - 1, 0, -1): path[(x, y)] = 'LEFT'
            path[(0, y)] = 'DOWN' if y < GRID_HEIGHT - 1 else 'RIGHT'
    _hamiltonian_path = path
    return path

def hamiltonian_move(snake):
    path = get_hamiltonian_path()
    head_pos = (int(snake[0].x / GRID_SIZE), int(snake[0].y / GRID_SIZE))
    return path.get(head_pos, 'UP')

# --- 算法3: 贪心生存算法 (无变化) ---
def greedy_survival_move(snake, current_direction):
    head = snake[0]
    best_move = current_direction
    max_space = -1
    possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    if current_direction == 'UP': possible_moves.remove('DOWN')
    elif current_direction == 'DOWN': possible_moves.remove('UP')
    elif current_direction == 'LEFT': possible_moves.remove('RIGHT')
    elif current_direction == 'RIGHT': possible_moves.remove('LEFT')

    for move in possible_moves:
        next_head_tuple = _get_next_head(head, move)
        if _is_move_deadly(next_head_tuple, snake): continue
        
        next_head_point = Point(next_head_tuple[0], next_head_tuple[1])
        simulated_snake = [next_head_point] + snake[:-1]
        space = _calculate_space_size(next_head_point, simulated_snake)

        if space > max_space:
            max_space = space
            best_move = move
    
    if max_space == -1: return current_direction
    return best_move

# --- 辅助函数 ---
def _get_next_head(head, direction):
    x, y = head.x, head.y
    if direction == 'UP': y -= GRID_SIZE
    elif direction == 'DOWN': y += GRID_SIZE
    elif direction == 'LEFT': x -= GRID_SIZE
    elif direction == 'RIGHT': x += GRID_SIZE
    return (x, y)

def _is_move_deadly(head_pos, snake):
    x, y = head_pos
    if not (0 <= x < GRID_WIDTH * GRID_SIZE and 0 <= y < GRID_HEIGHT * GRID_SIZE): return True
    # 检查是否会撞到蛇的身体（不包括即将消失的尾巴）
    if Point(x, y) in snake[:-1]: return True
    return False

def _calculate_space_size(start_pos, snake_body):
    start_x = start_pos.x if hasattr(start_pos, 'x') else start_pos[0]
    start_y = start_pos.y if hasattr(start_pos, 'y') else start_pos[1]
    
    start_node = (int(start_x / GRID_SIZE), int(start_y / GRID_SIZE))
    q = deque([start_node])
    
    # 正确：只把蛇的身体(不包括头)当作障碍物
    obstacles = {(int(p.x / GRID_SIZE), int(p.y / GRID_SIZE)) for p in snake_body[1:]}
    
    visited = {start_node} # 把起点加入已访问，避免重复计算
    count = 0
    
    while q:
        pos = q.popleft()
        count += 1 # 只要能从队列里出来，就是一个可达的空间

        (x, y) = pos
        neighbors = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
        for nx, ny in neighbors:
            next_node = (nx, ny)
            if (0 <= nx < GRID_WIDTH and 
                0 <= ny < GRID_HEIGHT and 
                next_node not in visited and 
                next_node not in obstacles): # 检查是否是障碍物
                
                visited.add(next_node)
                q.append(next_node)
    return count

