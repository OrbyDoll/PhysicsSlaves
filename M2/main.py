import pygame
import math
import sys
from typing import List, Optional, Tuple

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)
BROWN = (139, 69, 19)

# Настройки физики
FRICTION = 0.98  # Коэффициент трения
MIN_VELOCITY = 0.1  # Минимальная скорость для остановки

class Vector2:
    """Простой класс для работы с 2D векторами"""
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2()
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y
    
    def __repr__(self):
        return f"Vector2({self.x:.2f}, {self.y:.2f})"

class Ball:
    """Класс шара для бильярда"""
    def __init__(self, x: float, y: float, radius: float, color: Tuple[int, int, int], 
                 mass: float = 1.0, is_cue_ball: bool = False):
        self.position = Vector2(x, y)
        self.velocity = Vector2()
        self.radius = radius
        self.color = color
        self.mass = mass
        self.is_cue_ball = is_cue_ball
        self.in_pocket = False
    
    def update(self, dt: float):
        """Обновление позиции шара с учетом скорости и трения"""
        if self.in_pocket:
            return
            
        # Применяем трение
        self.velocity = self.velocity * FRICTION
        
        # Останавливаем шар, если скорость слишком мала
        if self.velocity.magnitude() < MIN_VELOCITY:
            self.velocity = Vector2()
            return
            
        # Обновляем позицию
        self.position = self.position + self.velocity * dt
    
    def apply_force(self, force: Vector2):
        """Применение силы к шару"""
        self.velocity = self.velocity + force / self.mass
    
    def draw(self, surface: pygame.Surface):
        """Отрисовка шара"""
        if self.in_pocket:
            return
            
        pygame.draw.circle(
            surface, 
            self.color, 
            (int(self.position.x), int(self.position.y)), 
            self.radius
        )
        
        # Если это биток, рисуем метку
        if self.is_cue_ball:
            pygame.draw.circle(
                surface, 
                BLACK, 
                (int(self.position.x), int(self.position.y)), 
                self.radius // 3
            )
    
    def check_pocket_collision(self, pockets: List['Pocket']) -> bool:
        """Проверка попадания шара в лузу"""
        for pocket in pockets:
            distance = (self.position - pocket.position).magnitude()
            if distance < pocket.radius:
                self.in_pocket = True
                return True
        return False

class Pocket:
    """Класс лузы"""
    def __init__(self, x: float, y: float, radius: float):
        self.position = Vector2(x, y)
        self.radius = radius
    
    def draw(self, surface: pygame.Surface):
        """Отрисовка лузы"""
        pygame.draw.circle(surface, BLACK, (int(self.position.x), int(self.position.y)), self.radius)

class Table:
    """Класс бильярдного стола"""
    def __init__(self, width: float, height: float, border_width: float):
        self.width = width
        self.height = height
        self.border_width = border_width
        self.pockets = self.create_pockets()
    
    def create_pockets(self) -> List[Pocket]:
        """Создание луз на столе"""
        pocket_radius = 20
        offset = self.border_width // 2
        
        pockets = [
            Pocket(offset, offset, pocket_radius),  # Верхний левый
            Pocket(self.width / 2, offset, pocket_radius),  # Верхний средний
            Pocket(self.width - offset, offset, pocket_radius),  # Верхний правый
            Pocket(offset, self.height - offset, pocket_radius),  # Нижний левый
            Pocket(self.width / 2, self.height - offset, pocket_radius),  # Нижний средний
            Pocket(self.width - offset, self.height - offset, pocket_radius),  # Нижний правый
        ]
        
        return pockets
    
    def check_wall_collision(self, ball: Ball):
        """Проверка столкновения шара со стенками стола"""
        if ball.in_pocket:
            return
            
        # Левая стенка
        if ball.position.x - ball.radius < self.border_width:
            ball.position.x = self.border_width + ball.radius
            ball.velocity.x = -ball.velocity.x * 0.9  # Немного поглощения энергии
        
        # Правая стенка
        if ball.position.x + ball.radius > self.width - self.border_width:
            ball.position.x = self.width - self.border_width - ball.radius
            ball.velocity.x = -ball.velocity.x * 0.9
        
        # Верхняя стенка
        if ball.position.y - ball.radius < self.border_width:
            ball.position.y = self.border_width + ball.radius
            ball.velocity.y = -ball.velocity.y * 0.9
        
        # Нижняя стенка
        if ball.position.y + ball.radius > self.height - self.border_width:
            ball.position.y = self.height - self.border_width - ball.radius
            ball.velocity.y = -ball.velocity.y * 0.9
    
    def draw(self, surface: pygame.Surface):
        """Отрисовка стола"""
        # Рисуем основу стола
        pygame.draw.rect(surface, BROWN, (0, 0, self.width, self.height))
        
        # Рисуем игровое поле
        pygame.draw.rect(
            surface, 
            GREEN, 
            (
                self.border_width, 
                self.border_width, 
                self.width - 2 * self.border_width, 
                self.height - 2 * self.border_width
            )
        )
        
        # Рисуем лузы
        for pocket in self.pockets:
            pocket.draw(surface)

class Cue:
    """Класс кия"""
    def __init__(self):
        self.angle = 0  # Угол в радианах
        self.power = 0  # Мощность удара (0-100)
        self.is_aiming = False
    
    def update(self, mouse_pos: Tuple[int, int], cue_ball: Ball):
        """Обновление позиции и угла кия"""
        if not self.is_aiming or cue_ball.velocity.magnitude() > 0:
            return
            
        dx = mouse_pos[0] - cue_ball.position.x
        dy = mouse_pos[1] - cue_ball.position.y
        self.angle = math.atan2(dy, dx)
    
    def draw(self, surface: pygame.Surface, cue_ball: Ball):
        """Отрисовка кия"""
        if not self.is_aiming or cue_ball.velocity.magnitude() > 0 or cue_ball.in_pocket:
            return
            
        # Длина кия зависит от мощности удара
        length = 150 + self.power
        
        # Вычисляем конечную точку кия
        end_x = cue_ball.position.x - math.cos(self.angle) * length
        end_y = cue_ball.position.y - math.sin(self.angle) * length
        
        # Рисуем кий
        pygame.draw.line(
            surface, 
            BROWN, 
            (cue_ball.position.x, cue_ball.position.y),
            (end_x, end_y),
            5
        )
    
    def strike(self, cue_ball: Ball):
        """Удар по битку"""
        if cue_ball.velocity.magnitude() > 0 or cue_ball.in_pocket:
            return
            
        # Преобразуем мощность в силу удара
        force = self.power * 10
        
        # Создаем вектор силы на основе угла
        force_vector = Vector2(
            -math.cos(self.angle) * force,
            -math.sin(self.angle) * force
        )
        
        # Применяем силу к битку
        cue_ball.apply_force(force_vector)
        
        # Сбрасываем состояние кия
        self.power = 0
        self.is_aiming = False

class Game:
    """Основной класс игры"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Бильярд")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
        # Создаем объекты игры
        self.table = Table(WIDTH, HEIGHT, 30)
        self.balls = self.create_balls()
        self.cue_ball = self.balls[0]  # Первый шар - биток
        self.cue = Cue()
    
    def create_balls(self) -> List[Ball]:
        """Создание шаров для игры"""
        balls = []
        ball_radius = 15
        
        # Создаем биток
        cue_ball = Ball(WIDTH // 4, HEIGHT // 2, ball_radius, WHITE, is_cue_ball=True)
        balls.append(cue_ball)
        
        # Создаем остальные шары в треугольнике
        colors = [
            (255, 0, 0),      # Красный
            (0, 0, 255),      # Синий
            (255, 165, 0),    # Оранжевый
            (0, 255, 0),      # Зеленый
            (128, 0, 128),    # Фиолетовый
            (255, 255, 0),    # Желтый
            (255, 192, 203),  # Розовый
            (128, 128, 128),  # Серый
            (165, 42, 42),    # Коричневый
            (0, 255, 255),    # Бирюзовый
            (255, 0, 255),    # Пурпурный
            (0, 128, 0),      # Темно-зеленый
            (0, 0, 128),      # Темно-синий
            (128, 0, 0),      # Темно-красный
            (128, 128, 0),    # Оливковый
        ]
        
        start_x = WIDTH * 3 // 4
        start_y = HEIGHT // 2
        row_balls = 5  # Количество шаров в первом ряду
        
        ball_idx = 0
        for row in range(row_balls):
            for col in range(row + 1):
                if ball_idx < len(colors):
                    x = start_x + row * (ball_radius * 2 - 1)
                    y = start_y - (row * ball_radius) + (col * ball_radius * 2)
                    ball = Ball(x, y, ball_radius, colors[ball_idx])
                    balls.append(ball)
                    ball_idx += 1
        
        return balls
    
    def handle_events(self):
        """Обработка событий игры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if self.all_balls_stopped():
                        self.cue.is_aiming = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    if self.cue.is_aiming:
                        self.cue.strike(self.cue_ball)
            
            elif event.type == pygame.MOUSEMOTION:
                if self.cue.is_aiming:
                    self.cue.update(event.pos, self.cue_ball)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.cue.is_aiming:
                    # Увеличиваем мощность удара при нажатии пробела
                    self.cue.power = min(self.cue.power + 10, 100)
                
                elif event.key == pygame.K_r:
                    # Перезапуск игры
                    self.__init__()
    
    def all_balls_stopped(self) -> bool:
        """Проверка, все ли шары остановились"""
        for ball in self.balls:
            if ball.velocity.magnitude() > 0 and not ball.in_pocket:
                return False
        return True
    
    def check_ball_collisions(self):
        """Проверка столкновений между шарами"""
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]
                
                if ball1.in_pocket or ball2.in_pocket:
                    continue
                
                # Вычисляем расстояние между центрами шаров
                distance = (ball1.position - ball2.position).magnitude()
                min_distance = ball1.radius + ball2.radius
                
                if distance < min_distance:
                    # Шары столкнулись - здесь нужно реализовать физику столкновения
                    self.resolve_ball_collision(ball1, ball2)
    
    def resolve_ball_collision(self, ball1: Ball, ball2: Ball):
        """
        Разрешение столкновения двух шаров.
        Здесь нужно реализовать физику упругого столкновения.
        """
        # Вектор от ball1 к ball2
        collision_vector = ball2.position - ball1.position
        distance = collision_vector.magnitude()
        
        # Нормализуем вектор столкновения
        if distance > 0:
            collision_normal = collision_vector / distance
        else:
            collision_normal = Vector2(1, 0)  # Запасной вариант
        
        # Отделяем шары, чтобы они не пересекались
        overlap = (ball1.radius + ball2.radius - distance) / 2.0
        ball1.position = ball1.position - collision_normal * overlap
        ball2.position = ball2.position + collision_normal * overlap
        
        # Вычисляем относительную скорость
        relative_velocity = ball1.velocity - ball2.velocity
        
        # Проекция относительной скорости на нормаль столкновения
        velocity_along_normal = relative_velocity.dot(collision_normal)
        
        # Если шары уже удаляются друг от друга, ничего не делаем
        if velocity_along_normal > 0:
            return
        
        # Коэффициент упругости (1 для абсолютно упругого столкновения)
        restitution = 0.95
        
        # Импульс столкновения
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= 1 / ball1.mass + 1 / ball2.mass
        
        # Применяем импульс к шарам
        impulse = collision_normal * impulse_scalar
        ball1.velocity = ball1.velocity + impulse / ball1.mass
        ball2.velocity = ball2.velocity - impulse / ball2.mass
    
    def update(self):
        """Обновление состояния игры"""
        # Обновляем позиции шаров
        for ball in self.balls:
            ball.update(self.dt)
        
        # Проверяем столкновения со стенками
        for ball in self.balls:
            self.table.check_wall_collision(ball)
        
        # Проверяем столкновения между шарами
        self.check_ball_collisions()
        
        # Проверяем попадание шаров в лузы
        for ball in self.balls:
            ball.check_pocket_collision(self.table.pockets)
        
        # Обновляем кий
        mouse_pos = pygame.mouse.get_pos()
        self.cue.update(mouse_pos, self.cue_ball)
    
    def draw(self):
        """Отрисовка игры"""
        self.screen.fill(BLACK)
        
        # Рисуем стол
        self.table.draw(self.screen)
        
        # Рисуем шары
        for ball in self.balls:
            ball.draw(self.screen)
        
        # Рисуем кий
        self.cue.draw(self.screen, self.cue_ball)
        
        # Отладочная информация
        font = pygame.font.Font(None, 24)
        fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        power_text = font.render(f"Мощность: {self.cue.power}", True, WHITE)
        self.screen.blit(fps_text, (10, 10))
        self.screen.blit(power_text, (10, 40))
        
        pygame.display.flip()
    
    def run(self):
        """Главный игровой цикл"""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0  # Время в секундах с последнего кадра
            
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()