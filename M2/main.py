import pygame as pg
import numpy as np
from typing import List
import math
from enum import Enum

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
TABLE_COEF = 0.7
TABLE_WIDTH = SCREEN_WIDTH * TABLE_COEF 
TABLE_HEIGHT = SCREEN_HEIGHT * TABLE_COEF
CUE_LENGTH = 300
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
CUE_DEFAULT_POS = (SCREEN_WIDTH - (SCREEN_WIDTH - BORDER_WIDTH) / 4 - CUE_WIDTH / 2, SCREEN_HEIGHT / 2 - CUE_LENGTH / 2)
CUE_POLYGON = (*CUE_DEFAULT_POS, CUE_DEFAULT_POS[0], CUE_DEFAULT_POS[1] + CUE_LENGTH)
EPS = 1e-1
COLORS = {"GREEN" : (0, 100, 0), "BROWN": (101,67,33), "CUE": (100, 84, 82)}

class Sides(Enum):
    LEFT = 1
    BOTTOM = 2
    RIGHT = 3
    TOP = 4
    NONE = 0

class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector'):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector'):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        elif isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other)

    def  __eq__(self, other: 'Vector'):
        return self.x == other.x and self.y == other.y
    
    def module(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def dot(self):
        return (self.x, self.y)
    
    def get_normal(self):
        return Vector(-self.y, self.x)
    
    def get_projection(self, base: 'Vector'):
        bb = base * base       
        if bb == 0:
            return Vector(0, 0)
        k = (self * base) / bb
        return Vector(base.x * k, base.y * k)
    
    def normalize(self):
        if (self.module() > 0):
            return self * (1 / self.module())
        return Vector(0, 1)


class Ball:
    def __init__(self, table: pg.Surface, position: Vector, index):
        self.table = table
        self.position = position
        self.velocity = Vector(0, 0)
        self.radius = BALL_SIZE
        self.color = "WHITE"
        self.index = index
        
    def update(self, dt: float, others: List['Ball']):
        self.position += self.velocity * dt
        if (pg.time.get_ticks() % 20 == 0):
            self.velocity *= 0.99
        if self.velocity.module() > EPS:
            colision_value = self.check_wall_collision()
            if colision_value.value:
                if colision_value == Sides.LEFT:
                    self.velocity = Vector(-self.velocity.x, self.velocity.y)
                elif colision_value == Sides.BOTTOM:
                    self.velocity = Vector(self.velocity.x, -self.velocity.y)
                elif colision_value == Sides.RIGHT:
                    self.velocity = Vector(-self.velocity.x, self.velocity.y)
                elif colision_value == Sides.TOP:
                    self.velocity = Vector(self.velocity.x, -self.velocity.y)
            for ball in others:
                if ball.position != self.position:
                    if self.check_balls_collision(ball):
                        self.calculate_collision(ball)
                        break
        else:
            self.velocity = Vector(0, 0)

    def draw(self):
        pg.draw.circle(self.table, self.color, self.position.dot(), self.radius)

    def check_dot(self, dot: Vector):
        if (dot.x - self.position.x) ** 2 + (dot.y - self.position.y) ** 2 < self.radius ** 2:
            return True
        return False

    def check_wall_collision(self):
        if self.position.x - self.radius <= MARGIN_LEFT:
            return Sides.LEFT # Удар в левый бортик
        elif self.position.x + self.radius >= SCREEN_WIDTH - MARGIN_LEFT:
            return Sides.RIGHT # Удар в правый бортик
        elif self.position.y + self.radius >= SCREEN_HEIGHT - MARGIN_TOP:
            return Sides.BOTTOM # Удар в нижний бортик
        elif self.position.y - self.radius <= MARGIN_TOP:
            return Sides.TOP # Удар в верхний бортик
        else:
            return Sides.NONE
        
    def calculate_collision(self, other: 'Ball'):
        normal = self.position - other.position

        self_normal_part = self.velocity.get_projection(normal)
        self_tangent_part = self.velocity - self_normal_part 

        other_normal_part = other.velocity.get_projection(normal)
        other_tangent_part = other.velocity - other_normal_part

        self.velocity = self_tangent_part + other_normal_part
        other.velocity = other_tangent_part + self_normal_part
    
    def check_balls_collision(self, other: 'Ball'):
        return (self.position - other.position).module() < (self.radius + other.radius)

class Cue:
    def __init__(self, table):
        self.table = table
        self.is_aimed = False
        self.aimed_ball = None
        self.position = CUE_POLYGON

    def draw(self):
        start_vector = Vector(self.position[0], self.position[1])
        end_vector = Vector(self.position[2], self.position[3])

        normal_vector = (start_vector - end_vector).get_normal().normalize()
        vertexes = []

        vertexes.append((start_vector + normal_vector * (CUE_WIDTH / 2)).dot())
        vertexes.append((start_vector - normal_vector * (CUE_WIDTH / 2)).dot())
        vertexes.append((end_vector - normal_vector * (CUE_WIDTH / 2)).dot())
        vertexes.append((end_vector + normal_vector * (CUE_WIDTH / 2)).dot())

        pg.draw.polygon(self.table, COLORS["CUE"], vertexes)

    def update(self):
        if (self.is_aimed):
            self.follow_cursor()
        
    def aim_cue(self, aimed_ball: Ball):
        self.is_aimed = not self.is_aimed
        self.aimed_ball = aimed_ball 

    def follow_cursor(self):
        cursor_pos = pg.mouse.get_pos()
        cursor_vector = Vector(cursor_pos[0], cursor_pos[1])
        ball_vector = self.aimed_ball.position

        x_dist = cursor_vector.x - ball_vector.x
        y_dist = cursor_vector.y - ball_vector.y
        shift1 = 2 * self.aimed_ball.radius
        shift2 = shift1 + CUE_LENGTH
        if x_dist != 0:
            line_koef = y_dist / x_dist

            x1_shift = shift1 / np.sqrt(1 + line_koef ** 2)
            y1_shift = x1_shift * line_koef

            x2_shift = shift2 / np.sqrt(1 + line_koef ** 2)
            y2_shift = x2_shift * line_koef
            start_pos = ball_vector + Vector(x1_shift , y1_shift) * np.sign(x_dist)
            end_pos = ball_vector + Vector(x2_shift, y2_shift) * np.sign(x_dist)
        else:
            start_pos = ball_vector + Vector(0, shift1) * np.sign(y_dist)
            end_pos = ball_vector + Vector(0, shift2) * np.sign(y_dist)

        self.position = [*start_pos.dot(), *end_pos.dot()]

    def apply_force(self, force: int):
        if self.aimed_ball:
            aim_vector = Vector(self.position[0] - self.position[2], self.position[1] - self.position[3]).normalize() * force
            self.aimed_ball.velocity = aim_vector

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.table = pg.draw.rect(self.screen, COLORS["GREEN"], (MARGIN_LEFT, MARGIN_TOP, TABLE_WIDTH, TABLE_HEIGHT), border_radius=BORDER_RADIUS)
        self.cue = Cue(self.screen)
        self.border = pg.draw.rect(self.screen, COLORS["BROWN"], (BORDER_MARGIN_LEFT, BORDER_MARGIN_TOP, BORDER_WIDTH, BORDER_HEIGHT), border_radius=BORDER_BORDER_RADIUS)
        self.balls: List[Ball] = []
        self.dt = pg.time.Clock().tick(60) / 1000.0
        self.hit_power = ""
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
        self.screen.fill("BLACK")
        self.border = pg.draw.rect(self.screen, COLORS["BROWN"], (BORDER_MARGIN_LEFT, BORDER_MARGIN_TOP, BORDER_WIDTH, BORDER_HEIGHT), border_radius=BORDER_BORDER_RADIUS)
        self.table = pg.draw.rect(self.screen, COLORS["GREEN"], (MARGIN_LEFT, MARGIN_TOP, TABLE_WIDTH, TABLE_HEIGHT), border_radius=BORDER_RADIUS)
        for ball in self.balls:
            ball.draw()
        self.cue.draw()
        pg.display.flip()

    def update(self):
        for ball in self.balls:
            ball.update(self.dt, self.balls)
        self.cue.update()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LALT:
                    self.mode = "create" if self.mode == "game" else "game"
                elif event.key == pg.K_LCTRL:
                    self.mode = "velocity" if self.mode != "velocity" else "aimed" if self.cue.aimed_ball else "game"
                elif event.key == pg.K_q:
                    self.running = False
                elif self.mode == "velocity":
                    if event.key in range(48, 58):
                        self.hit_power += chr(int(event.key))
                        print(f"Current force is {self.hit_power}")
                    elif event.key == 8:
                        self.hit_power = self.hit_power[:-1]
                        print(f"Current force is {self.hit_power}")
                elif self.mode == "aimed" and event.key == pg.K_SPACE:
                    if len(self.hit_power) > 0:
                        self.cue.apply_force(int(self.hit_power))
                        self.mode = "game"
                        self.cue.aim_cue(None)
                        self.hit_power = ""
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    cursor_pos = pg.mouse.get_pos()
                    if self.mode == "game":
                        current_ball: Ball = self.get_ball_by_coord(Vector(cursor_pos[0], cursor_pos[1]))
                        if current_ball != None:
                            self.cue.aim_cue(current_ball)
                            self.mode = "aimed"
                    elif self.mode == "create":
                        ball = Ball(self.screen, Vector(cursor_pos[0], cursor_pos[1]), len(self.balls) + 1)
                        self.balls.append(ball)                

    def get_ball_by_coord(self, position: Vector):
        for ball in self.balls:
            if ball.check_dot(position):
                return ball
        return None
    
if __name__ == "__main__":
    game = Game()
    game.run()