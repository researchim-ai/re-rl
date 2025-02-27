# re_rl/tasks/prompts.py

PROMPT_TEMPLATES = {
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
            "ru": "Шаг 2: Переносим {b} на правую сторону: {a}x = {c} - {b} = {right_side}.",
            "en": "Step 2: Transfer {b} to the right side: {a}x = {c} - {b} = {right_side}."
        },
        "step3": {
            "ru": "Шаг 3: Делим обе части на {a}: x = {right_side} / {a} = {solution}.",
            "en": "Step 3: Divide both sides by {a}: x = {right_side} / {a} = {solution}."
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
            "ru": "Шаг 3: Находим корни уравнения: x = {roots}.",
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
            "ru": "Шаг 2: Находим корни уравнения: x = {roots}.",
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
        "step1": {
            "ru": "Шаг 1: Запишем условия задачи: {details}.",
            "en": "Step 1: Write the problem details: {details}."
        },
        "step2": {
            "ru": "Шаг 2: Решаем задачу: {solution_step}.",
            "en": "Step 2: Solve the problem: {solution_step}."
        }
    }
}
