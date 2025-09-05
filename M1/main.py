import sympy as sp

# Определение переменных
t = sp.symbols('t')
y = sp.Function('y')

# Определение уравнения: y'' + y = 0
diff_eq = sp.Eq(y(t).diff(t, t) + y(t), 0)

# Решение
solution = sp.dsolve(diff_eq, y(t))
print("Аналитическое решение:")
print(solution)

# Начальные условия: y(0)=1, y'(0)=0
ics = {y(0): 1, y(t).diff(t).subs(t, 0): 0}
solution_with_ics = sp.dsolve(diff_eq, y(t), ics=ics)
print("\nС начальными условиями:")
print(solution_with_ics)