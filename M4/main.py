import sys, math
import pygame


g = 9.8
R_m = 0.20
L_m = 10


theta = math.radians(int(input("Угол наклонной: ")))
mu = float(input("Коэффициент трения об поверхность: "))
v0 = float(input("Начальная скорость: "))
omega0 = float(input("Начальная угловая скорость: "))


pygame.init()
W, H = 1400, 880
SIDEBAR_W = 300
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
FPS = 120


pygame.font.init()
font = pygame.font.SysFont("Arial", 20)

scale = 80
R_px = int(R_m * scale)
L_px = L_m * scale


cos_t = math.cos(theta)
sin_t = math.sin(theta)

line_mid = ((W - SIDEBAR_W) / 2, H / 2)
line_start = (line_mid[0] - L_px / 2 * cos_t, line_mid[1] - L_px / 2 * sin_t)
line_end = (line_start[0] + L_px * cos_t, line_start[1] + L_px * sin_t)



s = L_m / 2
v = v0
w = omega0
phi = 0
eps = 1e-2
mu_min = (2/5 / (1.0 + 2/5)) * math.tan(theta)

def update(s, v, w, dt):
    vrel = v - w * R_m

    is_rolling = (abs(vrel) < eps) and (mu >= mu_min)

    if is_rolling:
        a = g * math.sin(theta) / (1.0 + 2/5)
        alpha = a / R_m
        mode = "Rolling"
        friction_dir = -1
    else:
        if abs(vrel) < eps:
            sgn = 1
        else:
            sgn = 1 if vrel > 0 else -1
        a = g * math.sin(theta) - sgn * mu * g * math.cos(theta)
        alpha = sgn * (mu * g * math.cos(theta)) / (2/5 * R_m)
        mode = "Sliding"
        friction_dir = -1 if sgn > 0 else 1

    v += a * dt
    w += alpha * dt
    s += v * dt
    return s, v, w, a, alpha, mode, vrel, mu_min, friction_dir

def s_to_screen(s):

    base_x = line_start[0] + s * scale * cos_t
    base_y = line_start[1] + s * scale * sin_t

    cx = base_x + R_px * sin_t
    cy = base_y + R_px * -cos_t
    return cx, cy


def draw_sidebar(screen, rect, state):
    pygame.draw.rect(screen, (0, 0, 0), rect)

    x0, y0 = rect.left + 14, rect.top + 14
    lh = 24

    def blit_line(label, value):
        nonlocal y0
        text = f"{label}: {value}"
        surf = font.render(text, True, (255, 255, 255))
        screen.blit(surf, (x0, y0))
        y0 += lh

    mode, s, v, w, a, mu, mu_min = state

    blit_line("Mode", mode)
    blit_line("s [m]", f"{s:5.2f}")
    blit_line("v [m/s]", f"{v:5.2f}")
    blit_line("omega [rad/s]", f"{w:5.2f}")
    blit_line("a [m/s²]", f"{a:5.2f}")
    y0 += 6

    blit_line("mu_k", mu)
    blit_line("mu_min", f"{mu_min:.3f}")
    blit_line("time [s]", f"{time:3.1f}")

time = 0
running = True
while running:
    dt = clock.tick(FPS) / 4000.0
    time += dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    s, v, w, a, alpha, mode, vrel, mu_min, fr_dir = update(s, v, w, dt)
    phi += w * dt

    if s < 0.0:
        s, v = 0.0, 0.0
    if s > L_m:
        s, v = L_m, 0.0

    screen.fill((0, 0, 0))

    pygame.draw.line(screen, (255, 255, 255), line_start, line_end, 3)

    s_x, s_y = s_to_screen(s)
    pygame.draw.circle(screen, (70, 130, 220), (int(s_x), int(s_y)), R_px, width=0)

    p1 = (s_x - 0.9 * R_px * math.cos(phi), s_y - 0.9 * R_px * math.sin(phi))
    p2 = (s_x + 0.9 * R_px * math.cos(phi), s_y + 0.9 * R_px * math.sin(phi))
    pygame.draw.line(screen, (0, 0, 0), p1, p2, 3)

    sidebar_rect = pygame.Rect(W - SIDEBAR_W, 0, SIDEBAR_W, H)
    state = (mode, s, v, w, a, mu, mu_min)
    draw_sidebar(screen, sidebar_rect, state)

    pygame.display.flip()

pygame.quit()
sys.exit()
