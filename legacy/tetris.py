#!/usr/bin/env python3
"""
俄罗斯方块 (Tetris) - Python + Pygame
=============================
Controls:
  ← →  移动
  ↑    旋转
  ↓    加速下落
  空格  直接落底
  R    重新开始
  P    暂停
  ESC  退出
"""

import pygame
import random
import sys

# ============ 配置 ============
COLS = 10
ROWS = 20
CELL_SIZE = 30
PREVIEW_SIZE = 22

PANEL_WIDTH = 180
SCREEN_WIDTH = COLS * CELL_SIZE + PANEL_WIDTH
SCREEN_HEIGHT = ROWS * CELL_SIZE

# 颜色 (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
LIGHT_GRAY = (100, 100, 100)
DARK_GRAY = (20, 20, 20)
BORDER_COLOR = (60, 60, 60)

# 方块颜色（七种经典颜色）
COLORS = {
    'I': (0, 255, 255),    # 青色
    'O': (255, 255, 0),    # 黄色
    'T': (160, 0, 255),    # 紫色
    'S': (0, 255, 0),      # 绿色
    'Z': (255, 0, 0),      # 红色
    'J': (0, 0, 255),      # 蓝色
    'L': (255, 160, 0),    # 橙色
}

# 方块形状定义（4×4 矩阵）
SHAPES = {
    'I': [[0,0,0,0],
          [1,1,1,1],
          [0,0,0,0],
          [0,0,0,0]],
    'O': [[1,1],
          [1,1]],
    'T': [[0,1,0],
          [1,1,1],
          [0,0,0]],
    'S': [[0,1,1],
          [1,1,0],
          [0,0,0]],
    'Z': [[1,1,0],
          [0,1,1],
          [0,0,0]],
    'J': [[1,0,0],
          [1,1,1],
          [0,0,0]],
    'L': [[0,0,1],
          [1,1,1],
          [0,0,0]],
}

# 7-bag 随机生成器（保证公平性）
class BagRandomizer:
    def __init__(self):
        self.bag = []
        self.refill()

    def refill(self):
        self.bag = list(SHAPES.keys())
        random.shuffle(self.bag)

    def next(self):
        if not self.bag:
            self.refill()
        return self.bag.pop()

# ============ 核心逻辑 ============
class Tetris:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.rand = BagRandomizer()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.drop_timer = 0
        self.drop_interval = 500  # 毫秒

        self.current_piece = self.spawn_piece()
        self.next_piece = self.spawn_piece()
        self.hold_piece = None
        self.hold_used = False

    def spawn_piece(self):
        shape_type = self.rand.next()
        shape = [row[:] for row in SHAPES[shape_type]]
        return {
            'type': shape_type,
            'shape': shape,
            'x': COLS // 2 - len(shape[0]) // 2,
            'y': 0,
        }

    def _rotate_shape(self, shape):
        """顺时针旋转 90°"""
        return [list(row) for row in zip(*shape[::-1])]

    def _check_collision(self, shape, x, y):
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    if (board_x < 0 or board_x >= COLS or
                        board_y >= ROWS or board_y < 0):
                        return True
                    if board_y >= 0 and self.board[board_y][board_x]:
                        return True
        return False

    def _lock_piece(self):
        piece = self.current_piece
        for row_idx, row in enumerate(piece['shape']):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_y = piece['y'] + row_idx
                    board_x = piece['x'] + col_idx
                    if board_y >= 0:
                        self.board[board_y][board_x] = piece['type']

    def _clear_lines(self):
        lines = []
        for row_idx in range(ROWS):
            if all(self.board[row_idx]):
                lines.append(row_idx)

        if lines:
            for row_idx in reversed(lines):
                del self.board[row_idx]
                self.board.insert(0, [0] * COLS)

            cleared = len(lines)
            self.lines_cleared += cleared
            # 计分规则（NES 风格）
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(cleared, 0) * self.level
            self.level = self.lines_cleared // 10 + 1
            self.drop_interval = max(100, 500 - (self.level - 1) * 30)

    def move_left(self):
        if self.game_over or self.paused:
            return
        piece = self.current_piece
        if not self._check_collision(piece['shape'], piece['x'] - 1, piece['y']):
            piece['x'] -= 1

    def move_right(self):
        if self.game_over or self.paused:
            return
        piece = self.current_piece
        if not self._check_collision(piece['shape'], piece['x'] + 1, piece['y']):
            piece['x'] += 1

    def move_down(self):
        if self.game_over or self.paused:
            return
        piece = self.current_piece
        if not self._check_collision(piece['shape'], piece['x'], piece['y'] + 1):
            piece['y'] += 1
            return True
        else:
            self._lock_piece()
            self._clear_lines()
            self.current_piece = self.next_piece
            self.next_piece = self.spawn_piece()
            self.hold_used = False
            if self._check_collision(self.current_piece['shape'],
                                      self.current_piece['x'],
                                      self.current_piece['y']):
                self.game_over = True
            return False

    def rotate(self):
        if self.game_over or self.paused:
            return
        piece = self.current_piece
        rotated = self._rotate_shape(piece['shape'])
        # 墙踢 (Wall Kick) - 简单实现
        kicks = [0, -1, 1, -2, 2]
        for kick in kicks:
            if not self._check_collision(rotated, piece['x'] + kick, piece['y']):
                piece['shape'] = rotated
                piece['x'] += kick
                return

    def hard_drop(self):
        if self.game_over or self.paused:
            return
        piece = self.current_piece
        while not self._check_collision(piece['shape'], piece['x'], piece['y'] + 1):
            piece['y'] += 1
            self.score += 2
        self._lock_piece()
        self._clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.spawn_piece()
        self.hold_used = False
        if self._check_collision(self.current_piece['shape'],
                                  self.current_piece['x'],
                                  self.current_piece['y']):
            self.game_over = True

    def hold(self):
        if self.game_over or self.paused or self.hold_used:
            return
        self.hold_used = True
        if self.hold_piece is None:
            self.hold_piece = self.current_piece
            self.current_piece = self.next_piece
            self.next_piece = self.spawn_piece()
        else:
            old_type = self.hold_piece['type']
            self.hold_piece = self.current_piece
            self.current_piece = {
                'type': old_type,
                'shape': [row[:] for row in SHAPES[old_type]],
                'x': COLS // 2 - len(SHAPES[old_type][0]) // 2,
                'y': 0,
            }

    def update(self, dt):
        if self.game_over or self.paused:
            return
        self.drop_timer += dt
        if self.drop_timer >= self.drop_interval:
            self.drop_timer = 0
            self.move_down()

    def get_ghost_y(self):
        """获取影子方块的位置（硬降后的 y 坐标）"""
        piece = self.current_piece
        y = piece['y']
        while not self._check_collision(piece['shape'], piece['x'], y + 1):
            y += 1
        return y

# ============ 渲染 ============
def draw_block(screen, x, y, color, size=CELL_SIZE):
    pygame.draw.rect(screen, color, (x + 1, y + 1, size - 2, size - 2))
    # 高光效果
    highlight = tuple(min(c + 60, 255) for c in color)
    pygame.draw.line(screen, highlight, (x + 1, y + 1), (x + size - 2, y + 1), 2)
    pygame.draw.line(screen, highlight, (x + 1, y + 1), (x + 1, y + size - 2), 2)
    # 阴影效果
    shadow = tuple(max(c - 60, 0) for c in color)
    pygame.draw.line(screen, shadow, (x + size - 2, y + 1), (x + size - 2, y + size - 2), 2)
    pygame.draw.line(screen, shadow, (x + 1, y + size - 2), (x + size - 2, y + size - 2), 2)

def draw_board(screen, tetris, font):
    # 游戏区域背景
    board_rect = pygame.Rect(0, 0, COLS * CELL_SIZE, ROWS * CELL_SIZE)
    screen.fill(DARK_GRAY, board_rect)

    # 绘制网格线
    for x in range(0, COLS * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, ROWS * CELL_SIZE), 1)
    for y in range(0, ROWS * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (COLS * CELL_SIZE, y), 1)

    # 绘制已锁定的方块
    for row_idx in range(ROWS):
        for col_idx in range(COLS):
            cell = tetris.board[row_idx][col_idx]
            if cell:
                color = COLORS[cell]
                draw_block(screen, col_idx * CELL_SIZE, row_idx * CELL_SIZE, color)

    # 绘制影子方块
    piece = tetris.current_piece
    if piece and not tetris.game_over:
        ghost_y = tetris.get_ghost_y()
        for row_idx, row in enumerate(piece['shape']):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = (piece['x'] + col_idx) * CELL_SIZE
                    y = (ghost_y + row_idx) * CELL_SIZE
                    color = COLORS[piece['type']]
                    ghost_color = (color[0] // 4, color[1] // 4, color[2] // 4)
                    pygame.draw.rect(screen, ghost_color, (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))

    # 绘制当前方块
    if piece and not tetris.game_over:
        for row_idx, row in enumerate(piece['shape']):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = (piece['x'] + col_idx) * CELL_SIZE
                    y = (piece['y'] + row_idx) * CELL_SIZE
                    draw_block(screen, x, y, COLORS[piece['type']])

    # 游戏结束遮罩
    if tetris.game_over:
        overlay = pygame.Surface((COLS * CELL_SIZE, ROWS * CELL_SIZE))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        text = font.render("GAME OVER", True, WHITE)
        text_rect = text.get_rect(center=(COLS * CELL_SIZE // 2, ROWS * CELL_SIZE // 2))
        screen.blit(text, text_rect)
        text2 = font.render("Press R to restart", True, WHITE)
        text2_rect = text2.get_rect(center=(COLS * CELL_SIZE // 2, ROWS * CELL_SIZE // 2 + 40))
        screen.blit(text2, text2_rect)

def draw_panel(screen, tetris, font, small_font):
    panel_x = COLS * CELL_SIZE + 10
    y_offset = 20

    # 分数
    texts = [
        ("SCORE", str(tetris.score)),
        ("LEVEL", str(tetris.level)),
        ("LINES", str(tetris.lines_cleared)),
    ]
    for label, value in texts:
        lbl = small_font.render(label, True, LIGHT_GRAY)
        val = font.render(value, True, WHITE)
        screen.blit(lbl, (panel_x, y_offset))
        screen.blit(val, (panel_x, y_offset + 20))
        y_offset += 55

    # 下一个方块预览
    y_offset += 10
    next_label = small_font.render("NEXT", True, LIGHT_GRAY)
    screen.blit(next_label, (panel_x, y_offset))
    y_offset += 25

    if tetris.next_piece:
        next_shape = tetris.next_piece['shape']
        color = COLORS[tetris.next_piece['type']]
        for row_idx, row in enumerate(next_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = panel_x + col_idx * PREVIEW_SIZE
                    y = y_offset + row_idx * PREVIEW_SIZE
                    draw_block(screen, x, y, color, PREVIEW_SIZE)

    # 暂存方块预览
    y_offset += len(next_shape) * PREVIEW_SIZE + 30
    hold_label = small_font.render("HOLD", True, LIGHT_GRAY)
    screen.blit(hold_label, (panel_x, y_offset))
    y_offset += 25

    if tetris.hold_piece:
        hold_shape = SHAPES[tetris.hold_piece['type']]
        color = COLORS[tetris.hold_piece['type']]
        if tetris.hold_used:
            color = tuple(c // 2 for c in color)
        for row_idx, row in enumerate(hold_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = panel_x + col_idx * PREVIEW_SIZE
                    y = y_offset + row_idx * PREVIEW_SIZE
                    draw_block(screen, x, y, color, PREVIEW_SIZE)

    # 操作提示
    y_offset = SCREEN_HEIGHT - 170
    controls = [
        "← →  Move",
        "↑    Rotate",
        "↓    Soft Drop",
        "Space  Hard Drop",
        "C   Hold",
        "P   Pause",
        "R   Restart",
        "ESC  Exit",
    ]
    for ctrl in controls:
        ctrl_text = small_font.render(ctrl, True, LIGHT_GRAY)
        screen.blit(ctrl_text, (panel_x, y_offset))
        y_offset += 18

def draw_pause(screen, font):
    text = font.render("PAUSED", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

# ============ 主循环 ============
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("俄罗斯方块 Tetris")
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    tetris = Tetris()
    running = True

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    if tetris.game_over:
                        tetris.reset()
                    else:
                        tetris.reset()
                elif event.key == pygame.K_p:
                    if not tetris.game_over:
                        tetris.paused = not tetris.paused
                elif event.key == pygame.K_LEFT:
                    tetris.move_left()
                elif event.key == pygame.K_RIGHT:
                    tetris.move_right()
                elif event.key == pygame.K_DOWN:
                    tetris.move_down()
                elif event.key == pygame.K_UP:
                    tetris.rotate()
                elif event.key == pygame.K_SPACE:
                    tetris.hard_drop()
                elif event.key == pygame.K_c:
                    tetris.hold()

        if not tetris.game_over and not tetris.paused:
            tetris.update(dt)

        # 渲染
        screen.fill(BLACK)
        draw_board(screen, tetris, font)
        draw_panel(screen, tetris, font, small_font)

        if tetris.paused and not tetris.game_over:
            draw_pause(screen, font)

        # 边框
        pygame.draw.rect(screen, BORDER_COLOR,
                        (0, 0, COLS * CELL_SIZE, ROWS * CELL_SIZE), 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
