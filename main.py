# main.py

import pygame
from game import SnakeGame
from agent import AIController

def run_game():
    game = SnakeGame()
    agent = AIController()
    total_score = 0
    game_count = 0
    
    while True:
        game.reset()
        game_over = False
        
        while not game_over:
            current_state = game.get_game_state()
            action, path, debug_info = agent.get_action(game, current_state)
            reward, game_over, score = game.play_step(action, path, debug_info)

            if reward != 0:
                agent.update_weights(success=(reward > 0))

        game_count += 1
        total_score += score
        print(f"游戏结束! 局数: {game_count}, 本局得分: {score}, 平均分: {total_score / game_count:.2f}")

if __name__ == '__main__':
    run_game()
