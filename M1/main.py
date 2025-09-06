import numpy as np
from scipy.integrate import solve_ivp

def diff_system(t, data, params):
    x, y, v_x, v_y = data
    mass, koef, g = params
    
    dxdt = v_x
    dydt = v_y
    dv_xdt = -koef / mass * v_x
    dv_ydt = -g - koef / mass * v_y

    return [dxdt, dydt, dv_xdt, dv_ydt]


def hit_ground(t, data, params):
    y = data[1]
    return y  # возвращаем высоту, событие сработает когда вернет 0

# Указываем, что событие должно прекратить интегрирование
hit_ground.terminal = True  # остановить при срабатывании
hit_ground.direction = -1   

def solver():
    mass = 1
    g = 9.8

    start_velocity = float(input("Start velocity: "))
    angle = float(input("Angle: "))
    resistance_koefficient = float(input("Resistance koefficient: "))
    params = [mass, resistance_koefficient, g]

    t_span = [0, 100]
    rad_angle = np.radians(angle)
    initial_conditions = [0, 0, start_velocity * np.cos(rad_angle), start_velocity * np.sin(rad_angle)]
    t_eval = np.linspace(0, 100, 1000)

    solution = solve_ivp(diff_system, t_span=t_span, args=(params, ), events=hit_ground, y0=initial_conditions, t_eval=t_eval)
    print("Time: " + str(solution.t))
    print("Length: " + str(solution.y[0]))
    print("Height: " + str(solution.y[1]))

if __name__ == "__main__":
    solver()






