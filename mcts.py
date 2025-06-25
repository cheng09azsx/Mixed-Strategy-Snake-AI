# mcts.py

import math
import random
from collections import namedtuple

Point = namedtuple('Point', 'x, y')

class MCTSNode:
    """
    蒙特卡洛树上的一个节点，代表一个游戏状态
    """
    def __init__(self, state, parent=None, move=None):
        self.state = state  # 当前节点的游戏状态 (蛇、食物等)
        self.parent = parent  # 父节点
        self.move = move  # 从父节点到此节点的移动
        self.children = []  # 子节点列表
        self.wins = 0  # 在这个节点下模拟获胜的次数
        self.visits = 0  # 这个节点被访问的总次数
        self.untried_moves = self.get_legal_moves() # 获取所有合法的、未尝试的移动

    def get_legal_moves(self):
        """获取当前状态下所有合法的移动"""
        snake = self.state['snake']
        head = snake[0]
        possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        
        # 移除会导致立即死亡的移动
        safe_moves = []
        for move in possible_moves:
            next_head = self._get_next_head_tuple(head, move)
            if not self._is_move_deadly(next_head, snake):
                safe_moves.append(move)
        
        # 如果没有安全移动，就随便返回一个（反正要死了）
        return safe_moves if safe_moves else [possible_moves[0]]

    def _get_next_head_tuple(self, head, direction):
        GRID_SIZE = 20 # 假设GRID_SIZE为20
        x, y = head.x, head.y
        if direction == 'UP': y -= GRID_SIZE
        elif direction == 'DOWN': y += GRID_SIZE
        elif direction == 'LEFT': x -= GRID_SIZE
        elif direction == 'RIGHT': x += GRID_SIZE
        return (x, y)

    def _is_move_deadly(self, head_pos, snake):
        GRID_SIZE = 20
        WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
        x, y = head_pos
        if not (0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT): return True
        if Point(x, y) in snake: return True
        return False

    def select_child(self):
        """
        选择最优的子节点 (UCT算法)
        平衡“利用”（选择赢的多的）和“探索”（选择试的少的）
        """
        log_total_visits = math.log(self.visits)
        s = sorted(self.children, key=lambda c: c.wins / c.visits + 1.41 * math.sqrt(log_total_visits / c.visits))[-1]
        return s

    def expand(self, move, next_state):
        """扩展一个新的子节点"""
        child = MCTSNode(next_state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result):
        """反向传播，更新从当前节点到根节点的统计信息"""
        self.visits += 1
        self.wins += result

def mcts_search(game, initial_state, num_simulations=50):
    """
    MCTS主函数
    """
    root = MCTSNode(state=initial_state)

    for _ in range(num_simulations):
        node = root
        # 每次模拟都从根节点的真实状态开始复制
        simulation_state = {
            'snake': list(initial_state['snake']),
            'food': initial_state['food'],
            'direction': initial_state['direction']
        }

        # 1. 选择 (Selection)
        while not node.untried_moves and node.children:
            node = node.select_child()
            simulation_state, _, _ = game.simulate_step(simulation_state, node.move)

        # 2. 扩展 (Expansion)
        simulation_reward = 0
        is_simulation_over = False
        if node.untried_moves:
            move = random.choice(node.untried_moves)
            next_state, reward, game_over = game.simulate_step(simulation_state, move)
            
            if not game_over:
                node = node.expand(move, next_state)
                simulation_state = next_state
            else:
                # 如果扩展一步就结束了，记录结果，并标记模拟已结束
                simulation_reward = reward
                is_simulation_over = True

        # 3. 模拟 (Simulation / Rollout)
        if not is_simulation_over:
            # 从当前扩展出的新节点开始，随机走棋直到游戏结束
            rollout_state = simulation_state.copy()
            for _ in range(100): # 最多模拟100步
                moves = MCTSNode(rollout_state).get_legal_moves()
                if not moves: 
                    simulation_reward = -1 # 困死了，给个惩罚
                    break
                
                move = random.choice(moves)
                rollout_state, reward, game_over = game.simulate_step(rollout_state, move)
                if game_over:
                    simulation_reward = reward
                    break
        
        # 4. 反向传播 (Backpropagation)
        # 根据模拟结果更新路径上的所有节点
        while node is not None:
            node.update(simulation_reward)
            node = node.parent

    # 所有模拟结束后，选择访问次数最多的子节点的移动作为最佳移动
    if not root.children:
        # 如果没有任何可选的子节点（比如开局就被困死），随便走一步
        return root.get_legal_moves()[0]
        
    best_child = sorted(root.children, key=lambda c: c.visits)[-1]
    return best_child.move
