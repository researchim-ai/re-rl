# re_rl/tasks/prompts.py

PROMPT_TEMPLATES = {
    "default": {
        "prompt": {
            "ru": "Задача: {problem}",
            "en": "Task: {problem}"
        },
        "no_solution": {
            "ru": "Нет решения",
            "en": "No solution"
        },
        "no_unique_solution": {
            "ru": "Нет единственного решения",
            "en": "No unique solution"
        },
        "error": {
            "ru": "Ошибка: {error}",
            "en": "Error: {error}"
        }
    },
    "linear": {
        "problem": {
            "ru": "Решите линейное уравнение: {equation}",
            "en": "Solve the linear equation: {equation}"
        },
        "step1": {
            "ru": "Шаг 1: Запишем уравнение: {equation_pretty}.",
            "en": "Step 1: Write the equation: {equation_pretty}."
        },
        "step2": {
            "ru": "Шаг 2: Вычисляем правую часть: {c} - {b} = {right_side}.",
            "en": "Step 2: Compute the right-hand side: {c} - {b} = {right_side}."
        },
        "step3": {
            "ru": "Шаг 3: Делим обе части на {a}: x = {right_side} / {a} = {solution}.",
            "en": "Step 3: Divide both sides by {a}: x = {right_side} / {a} = {solution}."
        },
        "linear_extra_partition": {
            "ru": "Дополнительный шаг: разложим разность {c} - {b} на {n} частей: {parts}.",
            "en": "Extra step: decompose {c} - {b} into {n} parts: {parts}."
        },
        "linear_extra_sum": {
            "ru": "Дополнительный шаг: суммируем части: получаем {sum_value}.",
            "en": "Extra step: sum the parts to get {sum_value}."
        }
    },
    "quadratic": {
        "problem": {
            "ru": "Решите квадратное уравнение: {equation_pretty} = 0",
            "en": "Solve the quadratic equation: {equation_pretty} = 0"
        },
        "step1": {
            "ru": "Шаг 1: Запишем уравнение: {equation_pretty}.",
            "en": "Step 1: Write the equation: {equation_pretty}."
        },
        "step2": {
            "ru": "Шаг 2: Вычисляем дискриминант: D = {b}² - 4*{a}*{c} = {discriminant}.",
            "en": "Step 2: Compute the discriminant: D = {b}² - 4*{a}*{c} = {discriminant}."
        },
        "step3": {
            "ru": "Шаг 3: Находим корни: x = {roots}.",
            "en": "Step 3: Find the roots: x = {roots}."
        }
    },
    "cubic": {
        "problem": {
            "ru": "Решите кубическое уравнение: {equation_pretty} = 0",
            "en": "Solve the cubic equation: {equation_pretty} = 0"
        },
        "step1": {
            "ru": "Шаг 1: Запишем уравнение: {equation_pretty}.",
            "en": "Step 1: Write the equation: {equation_pretty}."
        },
        "step2": {
            "ru": "Шаг 2: Находим корни: x = {roots}.",
            "en": "Step 2: Find the roots: x = {roots}."
        }
    },
    "exponential": {
        "problem": {
            "ru": "Решите экспоненциальное уравнение: {left} = {d}",
            "en": "Solve the exponential equation: {left} = {d}"
        },
        "step1": {
            "ru": "Шаг 1: Запишем уравнение: {equation_pretty}.",
            "en": "Step 1: Write the equation: {equation_pretty}."
        },
        "step2": {
            "ru": "Шаг 2: Переносим {c} на правую сторону: {left_side_statement}.",
            "en": "Step 2: Transfer {c} to the right side: {left_side_statement}."
        },
        "step3": {
            "ru": "Шаг 3: Делим обе части на {a}: exp({b}*x) = {right_side} / {a}.",
            "en": "Step 3: Divide both sides by {a}: exp({b}*x) = {right_side} / {a}."
        },
        "step4": {
            "ru": "Шаг 4: Применяем натуральный логарифм: x = log({ratio}) / {b} = {solution}.",
            "en": "Step 4: Apply the natural logarithm: x = log({ratio}) / {b} = {solution}."
        }
    },
    "logarithmic": {
        "problem": {
            "ru": "Решите логарифмическое уравнение: {left} = {d}",
            "en": "Solve the logarithmic equation: {left} = {d}"
        },
        "step1": {
            "ru": "Шаг 1: Запишем уравнение: {equation_pretty}.",
            "en": "Step 1: Write the equation: {equation_pretty}."
        },
        "step2": {
            "ru": "Шаг 2: Переносим {c} на правую сторону: {left_side_statement}.",
            "en": "Step 2: Transfer {c} to the right side: {left_side_statement}."
        },
        "step3": {
            "ru": "Шаг 3: Делим обе части на {a}: log({b}*x) = ({d} - {c}) / {a}.",
            "en": "Step 3: Divide both sides by {a}: log({b}*x) = ({d} - {c}) / {a}."
        },
        "step4": {
            "ru": "Шаг 4: Вычисляем x = exp(({d} - {c})/{a})/{b} = {solution}.",
            "en": "Step 4: Compute x = exp(({d} - {c})/{a})/{b} = {solution}."
        }
    },
    "calculus": {
        "problem": {
            "ru": "Найди {task_type} функции f(x) = {function_pretty}.",
            "en": "Find the {task_type} of the function f(x) = {function_pretty}."
        },
        "step1": {
            "ru": "Шаг 1: Запишем функцию: f(x) = {function_pretty}.",
            "en": "Step 1: Write the function: f(x) = {function_pretty}."
        },
        "step2": {
            "ru": "Шаг 2: Вычисляем {task_type}: {result}.",
            "en": "Step 2: Compute the {task_type}: {result}."
        }
    },
    "graph": {
        "problem": {
            "ru": "Найди {task_description}.",
            "en": "Find {task_description}."
        },
        "shortest_path_iter": {
            "ru": "Шаг {iter}: Выбран узел {u} с расстоянием {d}. Обновления: {updates}.",
            "en": "Step {iter}: Selected node {u} with distance {d}. Updates: {updates}."
        },
        "shortest_path_final": {
            "ru": "Итоговый путь: {path}.",
            "en": "Final path: {path}."
        },
        "mst_step": {
            "ru": "Шаг 2: Найдено минимальное остовное дерево: {edges}.",
            "en": "Step 2: Found the minimum spanning tree: {edges}."
        },
        "diameter_step": {
            "ru": "Шаг 2: Диаметр графа равен: {diameter}.",
            "en": "Step 2: The diameter of the graph is: {diameter}."
        },
        "clustering_step": {
            "ru": "Шаг 2: Средний коэффициент кластеризации равен: {avg_coeff}.",
            "en": "Step 2: The average clustering coefficient is: {avg_coeff}."
        },
    },
    "system_linear": {
        "problem": {
            "ru": "Решите систему уравнений:\n{equations}",
            "en": "Solve the following system of equations:\n{equations}"
        },
        "step": {
            "ru": "Шаг {step_num}: {message}",
            "en": "Step {step_num}: {message}"
        },
        "no_unique_solution": {
            "ru": "Нет единственного решения",
            "en": "No unique solution"
        }
    },
    "analogical": {
        "problem": {
            "ru": "Используя аналогию, решите задачу:\n{description}",
            "en": "Using analogy, solve the following problem:\n{description}"
        },
        "step1": {
            "ru": "Шаг 1: Определите соответствия между элементами аналогии и проблемой.",
            "en": "Step 1: Identify corresponding elements between the analogy and the problem."
        },
        "step2": {
            "ru": "Шаг 2: Проанализируйте ключевые аспекты аналогии и проблемы.",
            "en": "Step 2: Analyze the key aspects of the analogy and the problem."
        },
        "step3": {
            "ru": "Шаг 3: Примените аналогичные решения для переноса стратегии решения.",
            "en": "Step 3: Apply analogous solutions to transfer the problem-solving strategy."
        },
        "step4": {
            "ru": "Шаг 4: Проверьте и уточните решение, корректируя подход при необходимости.",
            "en": "Step 4: Test and refine the solution, adjusting the approach as needed."
        },
        "final_answer": {
            "ru": "Решение с использованием аналогии сгенерировано на основе вышеуказанных шагов.",
            "en": "An analogical solution has been generated based on the above steps."
        }
    }
}
