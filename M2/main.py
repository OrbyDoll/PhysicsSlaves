import pygame as pg
from typing import List

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
TABLE_WIDTH = 800
TABLE_HEIGHT = 600
MARGIN_TOP = (SCREEN_HEIGHT - TABLE_HEIGHT) / 2
MARGIN_LEFT = (SCREEN_WIDTH - TABLE_WIDTH) / 2
BORDER_RADIUS = 30
BALL_SIZE = 15
COLORS = {"GREEN" : (0, 100, 0)}

class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar: float):
        return Vector(self.x * scalar, self.y * scalar)
    
    def dot(self):
        return (self.x, self.y)


class Ball:
    def __init__(self, position: Vector):
        self.position = position
        self.velocity = Vector(0, 0)
        self.radius = BALL_SIZE
        self.color = "WHITE"

    def update(self, dt: float):
        self.position += self.velocity * dt

    def draw(self, table):
        pg.draw.circle(table, self.color, self.position.dot(), self.radius)

    def check_dot(self, dot: Vector):
        if (dot.x - self.position.x) ** 2 + (dot.y - self.position.y) ** 2 < self.radius ** 2:
            return True
        return False

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.table = pg.draw.rect(self.screen, COLORS["GREEN"], (MARGIN_LEFT, MARGIN_TOP, TABLE_WIDTH, TABLE_HEIGHT), border_radius=BORDER_RADIUS)
        self.balls: List[Ball] = []
        self.dt = pg.time.Clock().tick(60) / 1000.0
        self.running = True
        self.mode = "game"

    def run(self):
        pg.init()
        pg.display.flip()
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            
    def draw(self):
        self.table = pg.draw.rect(self.screen, COLORS["GREEN"], (MARGIN_LEFT, MARGIN_TOP, TABLE_WIDTH, TABLE_HEIGHT), border_radius=BORDER_RADIUS)
        for ball in self.balls:
            ball.draw(self.screen)

        pg.display.flip()

    def update(self):
        for ball in self.balls:
            ball.update(self.dt)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LALT:
                    self.mode = "create" if self.mode == "game" else "game"
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    cursor_pos = pg.mouse.get_pos()
                    if self.mode == "game":
                        print("Play")
                        current_ball: Ball = self.get_ball_by_coord(Vector(cursor_pos[0], cursor_pos[1]))
                        current_ball.velocity = Vector(2, 1)
                    else:
                        print("Create")
                        ball = Ball(Vector(cursor_pos[0], cursor_pos[1]))
                        self.balls.append(ball)

    def get_ball_by_coord(self, position: Vector):
        for ball in self.balls:
            if ball.check_dot(position):
                return ball
if __name__ == "__main__":
    game = Game()
    game.run()