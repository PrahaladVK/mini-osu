import pygame
import random
import time
import math
import sys  # <-- Added import

WIDTH, HEIGHT = 800, 600
FPS = 60
CIRCLE_RADIUS = 60

# Difficulty settings, plus Exit as a special option
DIFFICULTIES = [
    {"name": "Easy", "lifetime": 2.2, "interval": 1.5},
    {"name": "Medium", "lifetime": 1.5, "interval": 1.0},
    {"name": "Hard", "lifetime": 1.0, "interval": 0.6},
    {"name": "Exit", "lifetime": None, "interval": None},  # Sentinel for quitting
]

# Colors
BG_COLOR = (30, 30, 30)
CIRCLE_COLOR = (0, 200, 255)
HIT_COLOR = (50, 255, 50)
MISS_COLOR = (255, 50, 50)
TEXT_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 220, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Osu!")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36)
big_font = pygame.font.SysFont('Arial', 60)

class Circle:
    def __init__(self, x, y, t_spawn, lifetime):
        self.x = x
        self.y = y
        self.t_spawn = t_spawn
        self.clicked = False
        self.hit = False
        self.radius = CIRCLE_RADIUS
        self.lifetime = lifetime

    def draw(self, surf, now):
        elapsed = now - self.t_spawn
        shrink = max(0, CIRCLE_RADIUS * (1 - elapsed / self.lifetime))
        color = HIT_COLOR if self.hit else (MISS_COLOR if self.clicked and not self.hit else CIRCLE_COLOR)
        if shrink > 0:
            pygame.draw.circle(surf, color, (self.x, self.y), int(shrink), 0)
        return shrink

    def check_hit(self, pos, now):
        if self.clicked: return False
        elapsed = now - self.t_spawn
        shrink = max(0, CIRCLE_RADIUS * (1 - elapsed / self.lifetime))
        dist = math.hypot(pos[0] - self.x, pos[1] - self.y)
        if dist <= shrink:
            self.hit = True
            self.clicked = True
            return True
        else:
            self.clicked = True
            return False

def show_difficulty_menu():
    selected = 1  # Medium by default
    choosing = True
    while choosing:
        screen.fill(BG_COLOR)
        title = big_font.render("Select Difficulty", True, SELECTED_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        for i, diff in enumerate(DIFFICULTIES):
            color = SELECTED_COLOR if i == selected else TEXT_COLOR
            text = font.render(diff["name"], True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 240 + 70 * i))
        info = font.render("Use ↑/↓ or W/S. Enter/Space to select.", True, TEXT_COLOR)
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 500))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()   # <-- Fixed here
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected = (selected - 1) % len(DIFFICULTIES)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected = (selected + 1) % len(DIFFICULTIES)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if DIFFICULTIES[selected]["name"] == "Exit":
                        pygame.quit()
                        sys.exit()  # <-- Fixed here
                    choosing = False
        clock.tick(20)
    return DIFFICULTIES[selected]

def game_loop(difficulty):
    score = 0
    circles = []
    last_spawn = 0
    start_time = time.time()
    running = True

    while running:
        now = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # <-- Fixed here
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to difficulty menu
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for c in circles:
                    if not c.clicked:
                        if c.check_hit(event.pos, now):
                            score += 100
                        else:
                            score -= 50

        # Spawn new circle
        if now - last_spawn > difficulty["interval"]:
            x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
            y = random.randint(CIRCLE_RADIUS, HEIGHT - CIRCLE_RADIUS)
            circles.append(Circle(x, y, now, difficulty["lifetime"]))
            last_spawn = now

        # Clear expired circles
        circles = [c for c in circles if now - c.t_spawn < c.lifetime or not c.clicked]

        # Draw
        screen.fill(BG_COLOR)
        for c in circles:
            c.draw(screen, now)
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        diff_text = font.render(f"Difficulty: {difficulty['name']}", True, TEXT_COLOR)
        screen.blit(diff_text, (WIDTH - diff_text.get_width() - 20, 20))
        info = font.render("Press ESC to change difficulty", True, TEXT_COLOR)
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT - 50))
        pygame.display.flip()
        clock.tick(FPS)

def main():
    while True:
        difficulty = show_difficulty_menu()
        game_loop(difficulty)

if __name__ == "__main__":
    main()
