import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

def diff_system(t, data, params):
    x, y, v_x, v_y = data
    mass, koef, g, koef_type = params

    dxdt = v_x
    dydt = v_y
    dv_xdt = -koef / mass * v_x if koef_type != "friction" else -koef / mass * v_x * v_x
    dv_ydt = -g - koef / mass * v_y if koef_type != "friction" else -g - koef / mass * v_y * v_y

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

def solver():
    mass = 1
    g = 9.8
    use_default = bool(input("Do you want to use default settings? Please print Y or N: ") == "Y")
    if use_default:
        start_velocity = 100.0
        angle = 45.0
        resistance_koefficient = 0.1
        resistance_type = "frontal"
    else:
        start_velocity = float(input("Start velocity: "))
        angle = float(input("Angle: "))
        resistance_koefficient = float(input("Resistance koefficient: "))
        resistance_type = "frontal" if int(input("Choose resistance type: \n1. Frontal resistance\n2. Viscous friction\nWrite a number: ")) == 1 else "friction"
    params = [mass, resistance_koefficient, g, resistance_type]

    t_span = [0, 100]
    rad_angle = np.radians(angle)
    initial_conditions = [0, 0, start_velocity * np.cos(rad_angle), start_velocity * np.sin(rad_angle)]
    t_eval = np.linspace(0, 100, 10000)

    solution = solve_ivp(diff_system, t_span=t_span, args=(params, ), method='DOP853', events=hit_ground, y0=initial_conditions, t_eval=t_eval, rtol=1e-6, atol=1e-8, max_step=0.01, dense_output=True)
    print("Time: " + str(solution.t[-1]))
    print("Length: " + str(solution.y[0][-1]))
    print("Height: " + str(max(solution.y[1])))

    vizualization([solution.y[0], list(solution.y[1]), solution.t])

if __name__ == "__main__":
    solver()






