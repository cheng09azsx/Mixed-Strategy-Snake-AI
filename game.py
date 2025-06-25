# game.py

import pygame
import random
from collections import namedtuple
from config import *

pygame.init() # 完整初始化pygame
Point = namedtuple('Point', 'x, y')

class SnakeGame:
    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('贪吃蛇AI')
        self.clock = pygame.time.Clock()
        
        # 初始化字体
        self.font_title = pygame.font.SysFont('arial', 22)
        self.font_normal = pygame.font.SysFont('arial', 18)
        
        self.reset()

    def reset(self):
        self.direction = 'RIGHT'
        start_x = (GRID_WIDTH * GRID_SIZE) / 2
        start_y = self.height / 2
        self.head = Point(start_x, start_y)
        self.snake = [self.head, 
                      Point(self.head.x - GRID_SIZE, self.head.y),
                      Point(self.head.x - (2 * GRID_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.food = Point(x, y)
            if self.food not in self.snake:
                break

    def play_step(self, action, path_to_draw=None, debug_info=None):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        self._move(action)
        self.snake.insert(0, self.head)
        
        reward = 0
        game_over = False
        if self._is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score
            
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.frame_iteration = 0
            self._place_food()
        else:
            self.snake.pop()
        
        self._update_ui(path_to_draw, debug_info)
        self.clock.tick(SPEED)
        
        return reward, game_over, self.score

    def _update_ui(self, path=None, debug_info=None):
        self.display.fill(BLACK)
        
        # --- 绘制游戏区域 ---
        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x, pt.y, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, GRID_SIZE, GRID_SIZE))
        if path:
            self._draw_path(path)

        # --- 绘制监控面板 ---
        self._draw_panel(debug_info)
        
        pygame.display.flip()

    def _draw_panel(self, info):
        panel_x = GRID_WIDTH * GRID_SIZE
        # 绘制面板背景
        pygame.draw.rect(self.display, GRAY, (panel_x, 0, PANEL_WIDTH, self.height))
        
        if not info: return

        y_pos = 20
        
        # 1. 绘制标题和得分
        self._draw_text("AI Monitor", self.font_title, WHITE, panel_x + PANEL_WIDTH / 2, y_pos)
        y_pos += 30
        self._draw_text(f"Score: {self.score}", self.font_normal, WHITE, panel_x + PANEL_WIDTH / 2, y_pos)
        y_pos += 40

        # 2. 绘制状态指标
        self._draw_text("--- Status ---", self.font_normal, YELLOW, panel_x + PANEL_WIDTH / 2, y_pos)
        y_pos += 25
        self._draw_text(f"Space: {info['available_space']}", self.font_normal, WHITE, panel_x + 10, y_pos, align="left")
        y_pos += 25
        self._draw_text(f"Length: {info['snake_length']}", self.font_normal, WHITE, panel_x + 10, y_pos, align="left")
        y_pos += 40

        # 3. 绘制算法决策
        self._draw_text("--- Decision ---", self.font_normal, YELLOW, panel_x + PANEL_WIDTH / 2, y_pos)
        y_pos += 25
        for algo, score in info['algorithm_scores'].items():
            color = WHITE
            if algo == info['chosen_algorithm']:
                color = YELLOW # 高亮显示选中的算法
            self._draw_text(f"{algo}: {score}", self.font_normal, color, panel_x + 10, y_pos, align="left")
            y_pos += 25
        y_pos += 15

        # 4. 绘制大脑权重
        self._draw_text("--- Brain Weights ---", self.font_normal, YELLOW, panel_x + PANEL_WIDTH / 2, y_pos)
        y_pos += 25
        for algo, weight in info['weights'].items():
            self._draw_text(f"{algo}: {weight:.2f}", self.font_normal, WHITE, panel_x + 10, y_pos, align="left")
            y_pos += 25

    def _draw_text(self, text, font, color, x, y, align="center"):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center":
            text_rect.center = (x, y)
        elif align == "left":
            text_rect.topleft = (x, y)
        self.display.blit(text_surface, text_rect)

    # (其他函数保持不变: _draw_path, _is_collision, _move, get_game_state, simulate_step)
    def _draw_path(self, path_directions):
        current_pos = self.head
        for direction in path_directions:
            start_center = (current_pos.x + GRID_SIZE // 2, current_pos.y + GRID_SIZE // 2)
            next_x, next_y = current_pos.x, current_pos.y
            if direction == 'UP': next_y -= GRID_SIZE
            elif direction == 'DOWN': next_y += GRID_SIZE
            elif direction == 'LEFT': next_x -= GRID_SIZE
            elif direction == 'RIGHT': next_x += GRID_SIZE
            end_center = (next_x + GRID_SIZE // 2, next_y + GRID_SIZE // 2)
            pygame.draw.line(self.display, BLUE, start_center, end_center, 2)
            current_pos = Point(next_x, next_y)

    def _is_collision(self):
        if self.head.x >= GRID_WIDTH * GRID_SIZE or self.head.x < 0 or self.head.y >= self.height or self.head.y < 0:
            return True
        if self.head in self.snake[1:]:
            return True
        return False
        
    def _move(self, action):
        if action is None: return # 防止AI在极端情况下返回None
        self.direction = action
        x = self.head.x
        y = self.head.y
        if self.direction == 'RIGHT': x += GRID_SIZE
        elif self.direction == 'LEFT': x -= GRID_SIZE
        elif self.direction == 'DOWN': y += GRID_SIZE
        elif self.direction == 'UP': y -= GRID_SIZE
        self.head = Point(x, y)

    def get_game_state(self):
        return {"snake": self.snake, "food": self.food, "direction": self.direction}

    def simulate_step(self, current_state, action):
        snake = list(current_state['snake'])
        food = current_state['food']
        head = snake[0]
        x, y = head.x, head.y
        if action == 'RIGHT': x += GRID_SIZE
        elif action == 'LEFT': x -= GRID_SIZE
        elif action == 'DOWN': y += GRID_SIZE
        elif action == 'UP': y -= GRID_SIZE
        new_head = Point(x, y)
        snake.insert(0, new_head)
        game_over = False
        reward = 0
        if new_head.x >= GRID_WIDTH * GRID_SIZE or new_head.x < 0 or new_head.y >= self.height or new_head.y < 0:
            game_over = True
            reward = -10
            return None, reward, game_over
        if new_head in snake[1:]:
            game_over = True
            reward = -10
            return None, reward, game_over
        if new_head == food:
            reward = 10
        else:
            snake.pop()
        next_state = {'snake': snake, 'food': food, 'direction': action}
        return next_state, reward, game_over
