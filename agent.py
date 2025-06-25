# agent.py
from algorithms import a_star_pathfinding, is_path_safe, hamiltonian_move, greedy_survival_move, _calculate_space_size
from mcts import mcts_search

class AIController:
    def __init__(self):
        self.weights = {
            'A_STAR': 1.0,
            'HAMILTONIAN': 1.0,
            'SURVIVAL': 1.0,
            'MCTS': 1.2
        }
        self.chosen_algorithm = None

    def get_action(self, game, game_state):
        snake = game_state['snake']
        
        # --- 1. 各算法提出自己的“方案”和“信心分数” ---
        scores = {
            'A_STAR': {'score': 0, 'path': None},
            'HAMILTONIAN': {'score': 0, 'path': None},
            'SURVIVAL': {'score': 0, 'path': None},
            'MCTS': {'score': 0, 'path': None}
        }

        path_to_food = a_star_pathfinding(snake, game_state['food'])
        if path_to_food:
            if is_path_safe(snake, game_state['food'], path_to_food):
                scores['A_STAR']['score'] = 100
                scores['A_STAR']['path'] = path_to_food
            else:
                scores['A_STAR']['score'] = -1

        available_space = _calculate_space_size(snake[0], snake)
        if available_space < len(snake) + 5:
            scores['HAMILTONIAN']['score'] = 80

        if scores['A_STAR']['score'] <= 0 and scores['HAMILTONIAN']['score'] == 0:
            scores['MCTS']['score'] = 90
        
        scores['SURVIVAL']['score'] = 20
        
        # --- 2. 结合“历史权重”进行最终决策 ---
        final_decision = 'SURVIVAL'
        max_score = -999
        for algo, result in scores.items():
            weighted_score = result['score'] * self.weights[algo]
            if weighted_score > max_score:
                max_score = weighted_score
                final_decision = algo
        
        self.chosen_algorithm = final_decision
        
        # --- 3. 执行最终选择的算法 ---
        action = None
        path = None
        if self.chosen_algorithm == 'A_STAR':
            path = scores['A_STAR']['path']
            action = path[0]
        elif self.chosen_algorithm == 'HAMILTONIAN':
            action = hamiltonian_move(snake)
        elif self.chosen_algorithm == 'MCTS':
            action = mcts_search(game, game_state, num_simulations=100)
        else: # SURVIVAL
            action = greedy_survival_move(snake, game_state['direction'])

        # --- 4. 打包所有思考过程并返回 ---
        debug_info = {
            "chosen_algorithm": self.chosen_algorithm,
            "algorithm_scores": {k: v['score'] for k, v in scores.items()},
            "weights": self.weights,
            "available_space": available_space,
            "snake_length": len(snake)
        }
        
        return action, path, debug_info

    def update_weights(self, success):
        if self.chosen_algorithm:
            if success:
                self.weights[self.chosen_algorithm] *= 1.02
            else:
                self.weights[self.chosen_algorithm] *= 0.98
