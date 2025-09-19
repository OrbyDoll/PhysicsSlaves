import pygame as pg
from typing import List
import math

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
TABLE_COEF = 0.7
TABLE_WIDTH = SCREEN_WIDTH * TABLE_COEF 
TABLE_HEIGHT = SCREEN_HEIGHT * TABLE_COEF
CUE_LENGTH = 200
CUE_WIDTH = 5
MARGIN_TOP = (SCREEN_HEIGHT - TABLE_HEIGHT) / 2
MARGIN_LEFT = (SCREEN_WIDTH - TABLE_WIDTH) / 2
BORDER_RADIUS = 30
BORDER = 50
BORDER_WIDTH = TABLE_WIDTH + BORDER
BORDER_HEIGHT = TABLE_HEIGHT + BORDER
BORDER_MARGIN_TOP = MARGIN_TOP - BORDER / 2
BORDER_MARGIN_LEFT = MARGIN_LEFT - BORDER / 2
BORDER_BORDER_RADIUS = int(BORDER_RADIUS + BORDER / 2)
BALL_SIZE = 15
CUE_DEFAULT_POS = (SCREEN_WIDTH - (SCREEN_WIDTH - BORDER_WIDTH) / 4 - CUE_WIDTH / 2, (SCREEN_HEIGHT - BORDER_HEIGHT) / 4 + CUE_LENGTH / 2)
COLORS = {"GREEN" : (0, 100, 0), "BROWN": (101,67,33)}

class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float):
        return Vector(self.x * scalar, self.y * scalar)
    
    def module(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def dot(self):
        return (self.x, self.y)


class Ball:
    def __init__(self, table, position: Vector):
        self.table = table
        self.position = position
        self.velocity = Vector(0, 0)
        self.radius = BALL_SIZE
        self.color = "WHITE"

    def update(self, dt: float):
        self.position += self.velocity * dt
        if self.velocity.module() > 0:
            if self.check_wall_collision():
                print("Wall Collision")
                self.velocity = Vector(0,0)
            

    def draw(self):
        pg.draw.circle(self.table, self.color, self.position.dot(), self.radius)

    def check_dot(self, dot: Vector):
        if (dot.x - self.position.x) ** 2 + (dot.y - self.position.y) ** 2 < self.radius ** 2:
            return True
        return False
    
    def check_wall_collision(self):
        return (
            self.position.x - self.radius <= MARGIN_LEFT or
            self.position.x + self.radius >= SCREEN_WIDTH - MARGIN_LEFT or
            self.position.y + self.radius >= SCREEN_HEIGHT - MARGIN_TOP or
            self.position.y - self.radius <= MARGIN_TOP
        )
    
    def check_balls_collision(self, other: 'Ball'):
        return (self.position - other.position).module() < (self.radius + other.radius)

class Cue:
    def __init__(self, table):
        self.table = table

    def draw(self, position):
        pg.draw.circle(self.table, "RED", position, 10)

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.table = pg.draw.rect(self.screen, COLORS["GREEN"], (MARGIN_LEFT, MARGIN_TOP, TABLE_WIDTH, TABLE_HEIGHT), border_radius=BORDER_RADIUS)
        self.cue = Cue(self.screen)
        self.cue.draw(CUE_DEFAULT_POS)
        pg.draw.rect(self.screen, COLORS["BROWN"], (BORDER_MARGIN_LEFT, BORDER_MARGIN_TOP, BORDER_WIDTH, BORDER_HEIGHT), border_radius=BORDER_BORDER_RADIUS)
        self.balls: List[Ball] = []
        self.dt = pg.time.Clock().tick(60) / 1000.0
        self.cue_pos = Vector(0, 0)
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
            ball.draw()
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
                elif event.key == pg.K_q:
                    self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    cursor_pos = pg.mouse.get_pos()
                    if self.mode == "game":
                        current_ball: Ball = self.get_ball_by_coord(Vector(cursor_pos[0], cursor_pos[1]))
                        if current_ball != None:
                            current_ball.velocity = Vector(-5, 0)
                    else:
                        ball = Ball(self.screen, Vector(cursor_pos[0], cursor_pos[1]))
                        self.balls.append(ball)

    def get_ball_by_coord(self, position: Vector):
        for ball in self.balls:
            if ball.check_dot(position):
                return ball
        return None
    
if __name__ == "__main__":
    game = Game()
    game.run()