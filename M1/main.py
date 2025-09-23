import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

def diff_system(t, data, params):
    x, y, v_x, v_y = data
    mass, frontal_koef, friction_koef, g = params

    dxdt = v_x
    dydt = v_y
    dv_xdt = -friction_koef / mass * v_x - frontal_koef / mass * v_x * np.sqrt(v_x ** 2 + v_y ** 2)
    dv_ydt = -g - friction_koef / mass * v_y - frontal_koef / mass * v_y * np.sqrt(v_x ** 2 + v_y ** 2)

    return [dxdt, dydt, dv_xdt, dv_ydt]


def hit_ground(t, data, params):
    y = data[1]
    return True if y > -1e-6 else False

hit_ground.terminal = True # Этот флаг означает, что когда функция вернет 0(т.е. камень упадет), программа, использующая эту функцию, должна прекратить свою итерацию(в нашем случае это интегрирование)
hit_ground.direction = -1  # Это нужно чтобы terminate сработал только при втором обнулении y(первый раз в начальный момент времени) 

def vizualization(dots):
    x_values = dots[0]
    y_values = list(dots[1])[:-1]
    y_values.append(0)
    times = dots[2]
    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values, 'g-', linewidth=2, alpha=0.7)

    # Если хочется видеть зависимость координаты от времени 
    # plt.scatter(x_values, y_values, c=times, cmap='viridis', s=100, alpha=0.8)
    # plt.colorbar(label='Время')

    plt.xlabel('X координата')
    plt.ylabel('Y координата')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.show()

def solver(data):
    mass, angle, start_velocity, g, frontal, friction = data
    t_span = [0, 100]
    rad_angle = np.radians(angle)
    initial_conditions = [0, 0, start_velocity * np.cos(rad_angle), start_velocity * np.sin(rad_angle)]
    t_eval = np.linspace(0, 100, 10000)
    params = [mass, frontal, friction, g]

    return solve_ivp(diff_system, t_span=t_span, args=(params, ), method='DOP853', events=hit_ground, y0=initial_conditions, t_eval=t_eval, rtol=1e-6, atol=1e-8, max_step=0.01, dense_output=True)

def find_angle(data):
    angle = 45
    angle_diff = angle / 2
    max_distance = 0
    epsilon = 1e-3

    while(angle_diff > epsilon):
        left_angle = angle - angle_diff
        right_angle = angle + angle_diff
        left_solution = solver([data[0]] + [left_angle] + data[1:])
        right_solution = solver([data[0]] + [right_angle] + data[1:])
        if (left_solution.y[0][-1] > right_solution.y[0][-1]):
            angle = left_angle
            max_distance = left_solution.y[0][-1]
        else:
            angle = right_angle
            max_distance = right_solution.y[0][-1]
        angle_diff /= 2

    return [angle, max_distance]


def main():
    mass = 1
    g = 9.8
    use_default = bool(input("Do you want to use default settings? Please print Y or N: ").lower() == "y")
    if use_default:
        start_velocity = 100.0
        angle = 45.0
        frontal_koefficient = 0.1
        friction_koefficient = 0
    else:
        start_velocity = float(input("Start velocity: "))
        angle = float(input("Angle: "))
        frontal_koefficient = float(input("Frontal koefficient: "))
        friction_koefficient = float(input("Friction koefficient: "))
    data = [mass, angle, start_velocity, g, frontal_koefficient, friction_koefficient]
    solution = solver(data)

    print("Time: " + str(solution.t[-1]))
    print("Length: " + str(solution.y[0][-1]))
    print("Height: " + str(max(solution.y[1])))

    optimal_data = find_angle([data[0]] + data[2:])
    print(f"Max distance: {optimal_data[1]}, then angle is {optimal_data[0]}")

    vizualization([solution.y[0], list(solution.y[1]), solution.t])

if __name__ == "__main__":
    main()






