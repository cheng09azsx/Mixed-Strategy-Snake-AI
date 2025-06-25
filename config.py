# config.py

# --- 窗口设置 ---
# 我们在右侧增加200像素的宽度用于显示监控面板
PANEL_WIDTH = 200
WINDOW_WIDTH = 640 + PANEL_WIDTH
WINDOW_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = 640 // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# --- 颜色 (使用RGB值) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100) # 用于面板背景
RED = (200, 0, 0)
GREEN1 = (0, 255, 0)
GREEN2 = (0, 200, 0)
BLUE = (0, 100, 255) # 用于路径
YELLOW = (255, 255, 0) # 用于高亮

# --- 游戏速度 ---
SPEED = 120 # 稍微提高速度，让AI表现更流畅

# --- 字体设置 ---
# FONT_TITLE_SIZE = 22
# FONT_NORMAL_SIZE = 18