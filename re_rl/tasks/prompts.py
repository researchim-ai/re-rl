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

    #----------------------------------------------------------------------------
    # 1) LINEAR
    #----------------------------------------------------------------------------
    "linear": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите линейное уравнение и выведите результат.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Шаги решения, можно по пунктам)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговое значение x)\n"
                "  </answer>\n"
                "Пример:\n"
                "<reasoning>\n"
                "  Шаг 1: Привели уравнение к виду ...\n"
                "  Шаг 2: Нашли x=2\n"
                "</reasoning>\n"
                "<answer>\n"
                "  2\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the linear equation.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step derivation)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (The final value of x)\n"
                "  </answer>\n"
                "Example:\n"
                "<reasoning>\n"
                "  Step 1: We rearranged the equation...\n"
                "  Step 2: Found x=2\n"
                "</reasoning>\n"
                "<answer>\n"
                "  2\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": "Решите линейное уравнение: {equation}",
            "en": "Solve the linear equation: {equation}"
        },
        "step1": {
            "ru": "Шаг 1: Записываем уравнение в стандартной форме:\n{equation_pretty}",
            "en": "Step 1: Write the equation in standard form:\n{equation_pretty}"
        },
        "step2_analysis": {
            "ru": "Шаг 2: Анализируем уравнение:\n- Коэффициент при x: {a}\n- Свободный член: {b}\n- Правая часть: {c}",
            "en": "Step 2: Analyze the equation:\n- Coefficient of x: {a}\n- Constant term: {b}\n- Right side: {c}"
        },
        "step3_terms": {
            "ru": "Шаг 3: Выделяем слагаемые:\n- Слагаемое с x: {a}x\n- Свободное слагаемое: {b}\n- Правая часть: {c}",
            "en": "Step 3: Identify terms:\n- Term with x: {a}x\n- Constant term: {b}\n- Right side: {c}"
        },
        "step4_transfer": {
            "ru": "Шаг 4: Переносим свободное слагаемое в правую часть:\n{c} - {b} = {right_side}",
            "en": "Step 4: Move the constant term to the right side:\n{c} - {b} = {right_side}"
        },
        "step5_coef": {
            "ru": "Шаг 5: Проверяем коэффициент при x:\nКоэффициент {a} не равен нулю, поэтому можно разделить обе части уравнения на {a}",
            "en": "Step 5: Check the coefficient of x:\nCoefficient {a} is not zero, so we can divide both sides by {a}"
        },
        "step6_division": {
            "ru": "Шаг 6: Делим обе части уравнения на {a}:\n{right_side} / {a} = {solution}",
            "en": "Step 6: Divide both sides by {a}:\n{right_side} / {a} = {solution}"
        },
        "step7_check": {
            "ru": "Шаг 7: Проверяем решение, подставляя x = {solution} в исходное уравнение:\n{equation}",
            "en": "Step 7: Verify the solution by substituting x = {solution} into the original equation:\n{equation}"
        },
        "step8_geom": {
            "ru": "Шаг 8: Геометрическая интерпретация:\nУравнение {a}x + {b} = {c} представляет собой прямую линию, которая пересекает ось x в точке x = {solution}",
            "en": "Step 8: Geometric interpretation:\nThe equation {a}x + {b} = {c} represents a straight line that intersects the x-axis at x = {solution}"
        },
        "step9_alt": {
            "ru": "Шаг 9: Альтернативный метод решения:\nМожно решить уравнение графически, построив графики функций y = {a}x + {b} и y = {c}. Точка их пересечения даст решение x = {solution}",
            "en": "Step 9: Alternative solution method:\nWe can solve the equation graphically by plotting the functions y = {a}x + {b} and y = {c}. Their intersection point gives the solution x = {solution}"
        },
        "linear_extra_partition": {
            "ru": "Шаг {n}: Разбиваем {c} - {b} на {n} равных частей:\n{parts}",
            "en": "Step {n}: Partition {c} - {b} into {n} equal parts:\n{parts}"
        },
        "linear_extra_sum": {
            "ru": "Шаг {n+1}: Проверяем сумму частей:\n{sum_value}",
            "en": "Step {n+1}: Verify the sum of parts:\n{sum_value}"
        },
        "explanation": {
            "ru": {
                "step1": "Записываем уравнение в стандартной форме для дальнейшего решения",
                "step2_analysis": "Анализируем структуру уравнения, определяя все его компоненты",
                "step3_terms": "Выделяем и называем каждое слагаемое в уравнении",
                "step4_transfer": "Переносим свободное слагаемое в правую часть для изоляции x",
                "step5_coef": "Проверяем возможность деления на коэффициент при x",
                "step6_division": "Делим обе части уравнения на коэффициент при x для получения решения",
                "step7_check": "Проверяем корректность решения подстановкой",
                "step8_geom": "Рассматриваем геометрический смысл уравнения",
                "step9_alt": "Рассматриваем альтернативный метод решения"
            },
            "en": {
                "step1": "Write the equation in standard form for further solution",
                "step2_analysis": "Analyze the structure of the equation, identifying all its components",
                "step3_terms": "Identify and name each term in the equation",
                "step4_transfer": "Move the constant term to the right side to isolate x",
                "step5_coef": "Check if we can divide by the coefficient of x",
                "step6_division": "Divide both sides by the coefficient of x to get the solution",
                "step7_check": "Verify the solution by substitution",
                "step8_geom": "Consider the geometric meaning of the equation",
                "step9_alt": "Consider an alternative solution method"
            }
        },
        "validation": {
            "ru": {
                "step1": "Уравнение записано корректно в стандартной форме",
                "step2_analysis": "Анализ уравнения выполнен правильно",
                "step3_terms": "Слагаемые выделены корректно",
                "step4_transfer": "Перенос слагаемых выполнен правильно",
                "step5_coef": "Проверка коэффициента выполнена корректно",
                "step6_division": "Деление на коэффициент выполнено правильно",
                "step7_check": "Проверка решения подтверждает его корректность",
                "step8_geom": "Геометрическая интерпретация верна",
                "step9_alt": "Альтернативный метод решения применим"
            },
            "en": {
                "step1": "The equation is correctly written in standard form",
                "step2_analysis": "Equation analysis is correct",
                "step3_terms": "Terms are correctly identified",
                "step4_transfer": "Term transfer is performed correctly",
                "step5_coef": "Coefficient check is correct",
                "step6_division": "Division by coefficient is performed correctly",
                "step7_check": "Solution verification confirms its correctness",
                "step8_geom": "Geometric interpretation is correct",
                "step9_alt": "Alternative solution method is applicable"
            }
        }
    },

    #----------------------------------------------------------------------------
    # 2) QUADRATIC
    #----------------------------------------------------------------------------
    "quadratic": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите квадратное уравнение и выведите результат.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Шаги решения, можно по пунктам)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Корни уравнения)\n"
                "  </answer>\n"
                "Пример:\n"
                "<reasoning>\n"
                "  Шаг 1: Привели уравнение к виду ...\n"
                "  Шаг 2: Нашли x=2\n"
                "</reasoning>\n"
                "<answer>\n"
                "  2\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the quadratic equation.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step derivation)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (The roots)\n"
                "  </answer>\n"
                "Example:\n"
                "<reasoning>\n"
                "  Step 1: We rearranged the equation...\n"
                "  Step 2: Found x=2\n"
                "</reasoning>\n"
                "<answer>\n"
                "  2\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": "Решите квадратное уравнение: {equation_pretty} = 0",
            "en": "Solve the quadratic equation: {equation_pretty} = 0"
        },
        "step1": {
            "ru": "Шаг 1: Записываем уравнение в стандартной форме:\n{equation_pretty} = 0",
            "en": "Step 1: Write the equation in standard form:\n{equation_pretty} = 0"
        },
        "step2": {
            "ru": "Шаг 2: Анализируем уравнение:\n- Коэффициент при x²: {a}\n- Коэффициент при x: {b}\n- Свободный член: {c}",
            "en": "Step 2: Analyze the equation:\n- Coefficient of x²: {a}\n- Coefficient of x: {b}\n- Constant term: {c}"
        },
        "step3": {
            "ru": "Шаг 3: Находим корни уравнения: {roots}",
            "en": "Step 3: Find the roots of the equation: {roots}"
        },
        "step2_analysis": {
            "ru": "Шаг 2: Анализируем уравнение:\n- Коэффициент при x²: {a}\n- Коэффициент при x: {b}\n- Свободный член: {c}",
            "en": "Step 2: Analyze the equation:\n- Coefficient of x²: {a}\n- Coefficient of x: {b}\n- Constant term: {c}"
        },
        "step3_discriminant": {
            "ru": "Шаг 3: Вычисляем дискриминант:\nD = b² - 4ac = {b}² - 4·{a}·{c} = {discriminant}",
            "en": "Step 3: Calculate the discriminant:\nD = b² - 4ac = {b}² - 4·{a}·{c} = {discriminant}"
        },
        "step4_roots": {
            "ru": "Шаг 4: Находим корни по формуле:\nx = (-b ± √D) / (2a)\nx = (-{b} ± √{discriminant}) / (2·{a})",
            "en": "Step 4: Find roots using the formula:\nx = (-b ± √D) / (2a)\nx = (-{b} ± √{discriminant}) / (2·{a})"
        },
        "step5_verify": {
            "ru": "Шаг 5: Проверяем корни, подставляя их в исходное уравнение:\n{equation_pretty} = 0",
            "en": "Step 5: Verify the roots by substituting them into the original equation:\n{equation_pretty} = 0"
        },
        "step6_geom": {
            "ru": "Шаг 6: Геометрическая интерпретация:\nУравнение {a}x² + {b}x + {c} = 0 представляет собой параболу, которая пересекает ось x в точках x = {roots}",
            "en": "Step 6: Geometric interpretation:\nThe equation {a}x² + {b}x + {c} = 0 represents a parabola that intersects the x-axis at points x = {roots}"
        },
        "step7_alt": {
            "ru": "Шаг 7: Альтернативный метод решения:\nМожно решить уравнение графически, построив график функции y = {a}x² + {b}x + {c}. Точки пересечения с осью x дадут корни x = {roots}",
            "en": "Step 7: Alternative solution method:\nWe can solve the equation graphically by plotting the function y = {a}x² + {b}x + {c}. The x-intercepts give the roots x = {roots}"
        },
        "explanation": {
            "ru": {
                "step1": "Записываем уравнение в стандартной форме для дальнейшего решения",
                "step2_analysis": "Анализируем структуру уравнения, определяя все его компоненты",
                "step3_discriminant": "Вычисляем дискриминант для определения количества и типа корней",
                "step4_roots": "Находим корни уравнения по формуле корней квадратного уравнения",
                "step5_verify": "Проверяем корректность найденных корней подстановкой",
                "step6_geom": "Рассматриваем геометрический смысл уравнения",
                "step7_alt": "Рассматриваем альтернативный метод решения"
            },
            "en": {
                "step1": "Write the equation in standard form for further solution",
                "step2_analysis": "Analyze the structure of the equation, identifying all its components",
                "step3_discriminant": "Calculate the discriminant to determine the number and type of roots",
                "step4_roots": "Find the roots using the quadratic formula",
                "step5_verify": "Verify the found roots by substitution",
                "step6_geom": "Consider the geometric meaning of the equation",
                "step7_alt": "Consider an alternative solution method"
            }
        },
        "validation": {
            "ru": {
                "step1": "Уравнение записано корректно в стандартной форме",
                "step2_analysis": "Анализ уравнения выполнен правильно",
                "step3_discriminant": "Дискриминант вычислен верно",
                "step4_roots": "Корни найдены по правильной формуле",
                "step5_verify": "Проверка корней подтверждает их корректность",
                "step6_geom": "Геометрическая интерпретация верна",
                "step7_alt": "Альтернативный метод решения применим"
            },
            "en": {
                "step1": "The equation is correctly written in standard form",
                "step2_analysis": "Equation analysis is correct",
                "step3_discriminant": "Discriminant is calculated correctly",
                "step4_roots": "Roots are found using the correct formula",
                "step5_verify": "Root verification confirms their correctness",
                "step6_geom": "Geometric interpretation is correct",
                "step7_alt": "Alternative solution method is applicable"
            }
        }
    },

    #----------------------------------------------------------------------------
    # 3) CUBIC
    #----------------------------------------------------------------------------
    "cubic": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите кубическое уравнение.\n"
                "Пример ответа:\n"
                "<reasoning>\n"
                "  (Объяснение решения)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (Корни)\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the cubic equation.\n"
                "Example:\n"
                "<reasoning>\n"
                "  (Explain how you found the roots)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  x1=..., x2=..., x3=...\n"
                "</answer>"
            )
        },
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

    #----------------------------------------------------------------------------
    # 4) EXPONENTIAL
    #----------------------------------------------------------------------------
    "exponential": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите показательное уравнение и выведите результат.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Шаги решения, можно по пунктам)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Значение x)\n"
                "  </answer>\n"
                "Пример:\n"
                "<reasoning>\n"
                "  Шаг 1: Привели уравнение к виду ...\n"
                "  Шаг 2: Нашли x=2\n"
                "</reasoning>\n"
                "<answer>\n"
                "  2\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the exponential equation.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step derivation)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (The value of x)\n"
                "  </answer>\n"
                "Example:\n"
                "<reasoning>\n"
                "  Step 1: We rearranged the equation...\n"
                "  Step 2: Found x=2\n"
                "</reasoning>\n"
                "<answer>\n"
                "  2\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": "Решите показательное уравнение: {left} = {d}",
            "en": "Solve the exponential equation: {left} = {d}"
        },
        "step1": {
            "ru": "Шаг 1: Записываем уравнение в стандартной форме:\n{equation_pretty}",
            "en": "Step 1: Write the equation in standard form:\n{equation_pretty}"
        },
        "step2": {
            "ru": "Шаг 2: Переносим свободный член {c} в правую часть:\n{left_side_statement}",
            "en": "Step 2: Move the constant term {c} to the right side:\n{left_side_statement}"
        },
        "step3": {
            "ru": "Шаг 3: Делим обе части уравнения на {a}:\n{right_side} / {a} = {ratio}",
            "en": "Step 3: Divide both sides by {a}:\n{right_side} / {a} = {ratio}"
        },
        "step4": {
            "ru": "Шаг 4: Применяем логарифм к обеим частям:\nlog({ratio}) / {b} = {solution}",
            "en": "Step 4: Apply logarithm to both sides:\nlog({ratio}) / {b} = {solution}"
        },
        "step5_exp": {
            "ru": "Шаг 5: Применяем экспоненту к обеим частям:\n{equation}",
            "en": "Step 5: Apply exponential function to both sides:\n{equation}"
        },
        "step6_solve": {
            "ru": "Шаг 6: Решаем уравнение относительно x:\nx = e^{(d - c) / a} / b = {solution}",
            "en": "Step 6: Solve for x:\nx = e^{(d - c) / a} / b = {solution}"
        },
        "step7_verify": {
            "ru": "Шаг 7: Проверяем решение, подставляя x = {solution} в исходное уравнение:\n{equation_pretty}",
            "en": "Step 7: Verify the solution by substituting x = {solution} into the original equation:\n{equation_pretty}"
        },
        "step8_geom": {
            "ru": "Шаг 8: Геометрическая интерпретация:\nУравнение {a}*log({b}*x) + {c} = {d} представляет собой пересечение логарифмической и линейной функций",
            "en": "Step 8: Geometric interpretation:\nThe equation {a}*log({b}*x) + {c} = {d} represents the intersection of logarithmic and linear functions"
        },
        "step9_domain": {
            "ru": "Шаг 9: Проверяем область определения:\nАргумент логарифма {b}*x = {solution} должен быть положительным",
            "en": "Step 9: Check the domain:\nThe logarithm argument {b}*x = {solution} must be positive"
        },
        "explanation": {
            "ru": {
                "step1": "Записываем уравнение в стандартной форме для дальнейшего решения",
                "step2_analysis": "Анализируем структуру уравнения, определяя все его компоненты",
                "step3_discriminant": "Вычисляем дискриминант для определения количества и типа корней",
                "step4_roots": "Находим корни уравнения по формуле корней квадратного уравнения",
                "step5_verify": "Проверяем корректность найденных корней подстановкой",
                "step6_geom": "Рассматриваем геометрический смысл уравнения",
                "step7_verify": "Проверяем корректность решения подстановкой",
                "step8_geom": "Рассматриваем геометрический смысл уравнения",
                "step9_domain": "Проверяем область определения логарифма"
            },
            "en": {
                "step1": "Write the equation in standard form for further solution",
                "step2_analysis": "Analyze the structure of the equation, identifying all its components",
                "step3_discriminant": "Calculate the discriminant to determine the number and type of roots",
                "step4_roots": "Find the roots using the quadratic formula",
                "step5_verify": "Verify the found roots by substitution",
                "step6_geom": "Consider the geometric meaning of the equation",
                "step7_verify": "Verify the solution by substitution",
                "step8_geom": "Consider the geometric meaning of the equation",
                "step9_domain": "Check the domain of the logarithm"
            }
        },
        "validation": {
            "ru": {
                "step1": "Уравнение записано корректно в стандартной форме",
                "step2_analysis": "Анализ уравнения выполнен правильно",
                "step3_discriminant": "Дискриминант вычислен верно",
                "step4_roots": "Корни найдены по правильной формуле",
                "step5_verify": "Проверка корней подтверждает их корректность",
                "step6_geom": "Геометрическая интерпретация верна",
                "step7_verify": "Проверка решения подтверждает его корректность",
                "step8_geom": "Геометрическая интерпретация верна",
                "step9_domain": "Проверка области определения выполнена корректно"
            },
            "en": {
                "step1": "The equation is correctly written in standard form",
                "step2_analysis": "Equation analysis is correct",
                "step3_discriminant": "Discriminant is calculated correctly",
                "step4_roots": "Roots are found using the correct formula",
                "step5_verify": "Root verification confirms their correctness",
                "step6_geom": "Geometric interpretation is correct",
                "step7_verify": "Solution verification confirms its correctness",
                "step8_geom": "Geometric interpretation is correct",
                "step9_domain": "Domain check is performed correctly"
            }
        }
    },

    #----------------------------------------------------------------------------
    # 5) LOGARITHMIC
    #----------------------------------------------------------------------------
    "logarithmic": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите логарифмическое уравнение и выведите результат.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Шаги решения, можно по пунктам)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговое значение x)\n"
                "  </answer>\n"
                "Пример:\n"
                "<reasoning>\n"
                "  Шаг 1: Привели уравнение к виду ...\n"
                "  Шаг 2: Нашли x=2\n"
                "</reasoning>\n"
                "<answer>\n"
                "  2\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the logarithmic equation.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step derivation)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (The final value of x)\n"
                "  </answer>\n"
                "Example:\n"
                "<reasoning>\n"
                "  Step 1: We rearranged the equation...\n"
                "  Step 2: Found x=2\n"
                "</reasoning>\n"
                "<answer>\n"
                "  2\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": "Решите логарифмическое уравнение: {left} = {d}",
            "en": "Solve the logarithmic equation: {left} = {d}"
        },
        "step1": {
            "ru": "Шаг 1: Записываем уравнение в стандартной форме:\n{equation_pretty}",
            "en": "Step 1: Write the equation in standard form:\n{equation_pretty}"
        },
        "step2_analysis": {
            "ru": "Шаг 2: Анализируем уравнение:\n- Коэффициент при логарифме: {a}\n- Коэффициент при x в аргументе логарифма: {b}\n- Свободный член: {c}\n- Правая часть: {d}",
            "en": "Step 2: Analyze the equation:\n- Coefficient of logarithm: {a}\n- Coefficient of x in logarithm argument: {b}\n- Constant term: {c}\n- Right side: {d}"
        },
        "step3_transfer": {
            "ru": "Шаг 3: Переносим свободный член в правую часть:\n{left_side_statement}",
            "en": "Step 3: Move the constant term to the right side:\n{left_side_statement}"
        },
        "step4_division": {
            "ru": "Шаг 4: Делим на коэффициент при логарифме:\n{equation}",
            "en": "Step 4: Divide by the coefficient of logarithm:\n{equation}"
        },
        "step5_exp": {
            "ru": "Шаг 5: Применяем экспоненту к обеим частям:\n{equation}",
            "en": "Step 5: Apply exponential function to both sides:\n{equation}"
        },
        "step6_solve": {
            "ru": "Шаг 6: Решаем уравнение относительно x:\nx = e^{(d - c) / a} / b = {solution}",
            "en": "Step 6: Solve for x:\nx = e^{(d - c) / a} / b = {solution}"
        },
        "step7_verify": {
            "ru": "Шаг 7: Проверяем решение, подставляя x = {solution} в исходное уравнение:\n{equation_pretty}",
            "en": "Step 7: Verify the solution by substituting x = {solution} into the original equation:\n{equation_pretty}"
        },
        "step8_geom": {
            "ru": "Шаг 8: Геометрическая интерпретация:\nУравнение {a}*log({b}*x) + {c} = {d} представляет собой пересечение логарифмической и линейной функций",
            "en": "Step 8: Geometric interpretation:\nThe equation {a}*log({b}*x) + {c} = {d} represents the intersection of logarithmic and linear functions"
        },
        "step9_domain": {
            "ru": "Шаг 9: Проверяем область определения:\nАргумент логарифма {b}*x = {solution} должен быть положительным",
            "en": "Step 9: Check the domain:\nThe logarithm argument {b}*x = {solution} must be positive"
        },
        "explanation": {
            "ru": {
                "step1": "Записываем уравнение в стандартной форме для дальнейшего решения",
                "step2_analysis": "Анализируем структуру уравнения, определяя все его компоненты",
                "step3_transfer": "Переносим свободный член в правую часть для изоляции логарифма",
                "step4_division": "Делим обе части уравнения на коэффициент при логарифме",
                "step5_exp": "Применяем экспоненту для избавления от логарифма",
                "step6_solve": "Решаем уравнение относительно x",
                "step7_verify": "Проверяем корректность решения подстановкой",
                "step8_geom": "Рассматриваем геометрический смысл уравнения",
                "step9_domain": "Проверяем область определения логарифма"
            },
            "en": {
                "step1": "Write the equation in standard form for further solution",
                "step2_analysis": "Analyze the structure of the equation, identifying all its components",
                "step3_transfer": "Move the constant term to the right side to isolate the logarithm",
                "step4_division": "Divide both sides by the coefficient of logarithm",
                "step5_exp": "Apply exponential function to eliminate the logarithm",
                "step6_solve": "Solve the equation for x",
                "step7_verify": "Verify the solution by substitution",
                "step8_geom": "Consider the geometric meaning of the equation",
                "step9_domain": "Check the domain of the logarithm"
            }
        },
        "validation": {
            "ru": {
                "step1": "Уравнение записано корректно в стандартной форме",
                "step2_analysis": "Анализ уравнения выполнен правильно",
                "step3_transfer": "Перенос слагаемых выполнен правильно",
                "step4_division": "Деление на коэффициент выполнено правильно",
                "step5_exp": "Применение экспоненты выполнено корректно",
                "step6_solve": "Решение уравнения выполнено правильно",
                "step7_verify": "Проверка решения подтверждает его корректность",
                "step8_geom": "Геометрическая интерпретация верна",
                "step9_domain": "Проверка области определения выполнена корректно"
            },
            "en": {
                "step1": "The equation is correctly written in standard form",
                "step2_analysis": "Equation analysis is correct",
                "step3_transfer": "Term transfer is performed correctly",
                "step4_division": "Division by coefficient is performed correctly",
                "step5_exp": "Exponential application is correct",
                "step6_solve": "Equation solving is performed correctly",
                "step7_verify": "Solution verification confirms its correctness",
                "step8_geom": "Geometric interpretation is correct",
                "step9_domain": "Domain check is performed correctly"
            }
        }
    },

    #----------------------------------------------------------------------------
    # 6) CALCULUS
    #----------------------------------------------------------------------------
    "calculus": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по анализу (дифференцирование/интегрирование).\n"
                "Формат:\n"
                "<reasoning>\n"
                "  (Ваши шаги)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (Результат)\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the calculus task (differentiation/integration).\n"
                "Format:\n"
                "<reasoning>\n"
                "  (Steps)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (The final expression)\n"
                "</answer>"
            )
        },
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

    #----------------------------------------------------------------------------
    # 7) GRAPH
    #----------------------------------------------------------------------------
    "graph": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Задача на граф (кратчайший путь, MST и т.д.).\n"
                "Пример ответа:\n"
                "<reasoning>\n"
                "  (Шаги работы алгоритма)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (Итог: маршрут, дерево, диаметр)\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: A graph problem (shortest path, MST, etc.).\n"
                "Example:\n"
                "<reasoning>\n"
                "  (Algorithm steps)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (Final path, tree, diameter, etc.)\n"
                "</answer>"
            )
        },
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
            "ru": "Шаг 2: Минимальное остовное дерево: {edges}.",
            "en": "Step 2: The minimum spanning tree: {edges}."
        },
        "diameter_step": {
            "ru": "Шаг 2: Диаметр графа: {diameter}.",
            "en": "Step 2: The diameter of the graph is {diameter}."
        },
        "clustering_step": {
            "ru": "Шаг 2: Средний коэффициент кластеризации: {avg_coeff}.",
            "en": "Step 2: The average clustering coefficient is {avg_coeff}."
        }
    },

    #----------------------------------------------------------------------------
    # 8) SYSTEM_LINEAR
    #----------------------------------------------------------------------------
    "system_linear": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите систему линейных уравнений.\n"
                "Пример ответа:\n"
                "<reasoning>\n"
                "  (шаги по Крамеру)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  x1=..., x2=...\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve a system of linear equations.\n"
                "Example:\n"
                "<reasoning>\n"
                "  (Cramer's rule steps)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  x1=..., x2=...\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": "Решите систему уравнений:\n{equations}",
            "en": "Solve the following system of equations:\n{equations}"
        },
        "steps": {
            "compute_det": {
                "ru": "Шаг 1: Вычисляем главный определитель системы: det(A) = {det}",
                "en": "Step 1: Compute main determinant: det(A) = {det}"
            },
            "replace_column": {
                "ru": "Шаг {step_num}: Заменяем {col}-й столбец и вычисляем det(A_{col}) = {det}",
                "en": "Step {step_num}: Replace column {col} and compute det(A_{col}) = {det}"
            },
            "compute_variable": {
                "ru": "Шаг {step_num}: x{var} = det(A_{var}) / det(A) = {value}",
                "en": "Step {step_num}: x{var} = det(A_{var}) / det(A) = {value}"
            }
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

    #----------------------------------------------------------------------------
    # 9) ANALOGICAL
    #----------------------------------------------------------------------------
    "analogical": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Задача на аналогию. \n"
                "Пример:\n"
                "<reasoning>\n"
                "  (Сравнение исходного примера и новой ситуации)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (Итоговое решение)\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: An analogy-based puzzle.\n"
                "Example:\n"
                "<reasoning>\n"
                "  (Map the analogy to the new problem)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (Conclusions)\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": "Используя аналогию, решите задачу:\n{description}",
            "en": "Using analogy, solve the following problem:\n{description}"
        },
        "step1": {
            "ru": "Шаг 1: Определите соответствия...",
            "en": "Step 1: Identify analogous elements..."
        },
        "step2": {
            "ru": "Шаг 2: Проанализируйте ключевые аспекты...",
            "en": "Step 2: Analyze the key aspects..."
        },
        "step3": {
            "ru": "Шаг 3: Примените аналогию...",
            "en": "Step 3: Apply analogy..."
        },
        "step4": {
            "ru": "Шаг 4: Проверьте решение...",
            "en": "Step 4: Test and refine..."
        },
        "final_answer": {
            "ru": "Решение с использованием аналогии...",
            "en": "An analogical solution has been generated..."
        }
    },

    #----------------------------------------------------------------------------
    # 10) CONTRADICTION
    #----------------------------------------------------------------------------
    "contradiction": {
        "problem": {
            "ru": "Среди следующих утверждений одно является ложным. Найдите его:\n\n{statements}",
            "en": "Among the following statements, one is false. Find it:\n\n{statements}"
        },
        "instructions": {
            "ru": """Для решения этой задачи следуйте следующим шагам:
1. Внимательно прочитайте каждое утверждение
2. Проанализируйте каждое утверждение на предмет его истинности
3. Найдите утверждение, которое противоречит общеизвестным фактам
4. Объясните, почему выбранное утверждение является ложным

Стратегия решения:
- Разделите утверждения на логические группы
- Сравните утверждения между собой
- Используйте свои знания для проверки каждого утверждения
- Обратите внимание на детали и формулировки""",
            "en": """To solve this task, follow these steps:
1. Read each statement carefully
2. Analyze each statement for truthfulness
3. Find the statement that contradicts common knowledge
4. Explain why the chosen statement is false

Solution strategy:
- Divide statements into logical groups
- Compare statements with each other
- Use your knowledge to verify each statement
- Pay attention to details and wording"""
        },
        "example": {
            "ru": """Пример рассуждений:
- Вода закипает при температуре 100 градусов Цельсия
- Солнце восходит на востоке
- Земля вращается вокруг своей оси
- Луна светит своим собственным светом

Анализ:
1. Первые три утверждения являются общеизвестными фактами
2. Четвертое утверждение противоречит научным знаниям - Луна отражает солнечный свет
3. Следовательно, четвертое утверждение является ложным""",
            "en": """Example reasoning:
- Water boils at 100 degrees Celsius
- The sun rises in the east
- The Earth rotates on its axis
- The Moon shines with its own light

Analysis:
1. The first three statements are common knowledge
2. The fourth statement contradicts scientific knowledge - the Moon reflects sunlight
3. Therefore, the fourth statement is false"""
        },
        "step1": {
            "ru": "Начнем с общего анализа всех утверждений. Разделим их на логические группы для более эффективного поиска.",
            "en": "Let's start with a general analysis of all statements. We'll divide them into logical groups for more efficient search."
        },
        "final_answer": {
            "ru": "Ложное утверждение: {false_statement}",
            "en": "False statement: {false_statement}"
        },
        "explanation": {
            "ru": "Это утверждение является ложным, так как противоречит общеизвестным фактам и научным знаниям.",
            "en": "This statement is false as it contradicts common knowledge and scientific facts."
        }
    },

    "contradiction_facts": {
        "ru": {
            "true": [
                "Вода закипает при температуре 100 градусов Цельсия",
                "Солнце восходит на востоке",
                "Земля вращается вокруг своей оси",
                "В году 365 дней",
                "Кислород необходим для дыхания",
                "Металлы проводят электричество",
                "Растения производят кислород",
                "Лед плавится при температуре 0 градусов Цельсия",
                "Гравитация притягивает объекты к центру Земли",
                "Свет распространяется быстрее звука",
                "Вода состоит из водорода и кислорода",
                "Человек имеет 206 костей",
                "Солнце является звездой",
                "Воздух состоит из смеси газов",
                "Растения нуждаются в солнечном свете",
                "Вода может существовать в трех состояниях",
                "Земля имеет один естественный спутник",
                "Кислород является газом",
                "Металлы имеют высокую теплопроводность",
                "Растения размножаются семенами",
                "Вода является универсальным растворителем",
                "Человек имеет пять основных чувств",
                "Солнце является источником энергии",
                "Воздух имеет массу",
                "Растения поглощают углекислый газ",
                "Вода имеет наибольшую плотность при 4°C",
                "Земля имеет магнитное поле",
                "Кислород поддерживает горение",
                "Металлы имеют металлический блеск",
                "Растения имеют корневую систему",
                "Вода может испаряться при любой температуре",
                "Человек имеет 32 зуба",
                "Солнце находится в центре Солнечной системы",
                "Воздух оказывает давление",
                "Растения имеют листья",
                "Вода может растворять соли",
                "Земля имеет атмосферу",
                "Кислород необходим для горения",
                "Металлы могут быть жидкими",
                "Растения имеют стебель",
                "Вода может замерзать",
                "Человек имеет сердце",
                "Солнце излучает свет",
                "Воздух содержит азот",
                "Растения имеют цветы",
                "Вода может течь",
                "Земля имеет океаны",
                "Кислород является элементом",
                "Металлы могут ржаветь"
            ],
            "false": [
                "Вода закипает при температуре 50 градусов Цельсия",
                "Солнце восходит на западе",
                "Земля плоская",
                "В году 400 дней",
                "Кислород не нужен для дыхания",
                "Металлы не проводят электричество",
                "Растения не производят кислород",
                "Лед плавится при температуре 100 градусов Цельсия",
                "Гравитация отталкивает объекты от Земли",
                "Звук распространяется быстрее света",
                "Вода состоит из углерода и азота",
                "Человек имеет 100 костей",
                "Солнце является планетой",
                "Воздух состоит из одного газа",
                "Растения не нуждаются в солнечном свете",
                "Вода может существовать только в жидком состоянии",
                "Земля имеет два естественных спутника",
                "Кислород является жидкостью",
                "Металлы не проводят тепло",
                "Растения не размножаются",
                "Вода не растворяет соли",
                "Человек имеет три чувства",
                "Солнце не излучает энергию",
                "Воздух не имеет массы",
                "Растения не поглощают углекислый газ",
                "Вода имеет наибольшую плотность при 100°C",
                "Земля не имеет магнитного поля",
                "Кислород не поддерживает горение",
                "Металлы не имеют блеска",
                "Растения не имеют корней",
                "Вода не может испаряться",
                "Человек имеет 20 зубов",
                "Солнце вращается вокруг Земли",
                "Воздух не оказывает давления",
                "Растения не имеют листьев",
                "Вода не растворяет соли",
                "Земля не имеет атмосферы",
                "Кислород не нужен для горения",
                "Металлы не могут быть жидкими",
                "Растения не имеют стебля",
                "Вода не может замерзать",
                "Человек не имеет сердца",
                "Солнце не излучает свет",
                "Воздух не содержит азота",
                "Растения не имеют цветов",
                "Вода не может течь",
                "Земля не имеет океанов",
                "Кислород не является элементом",
                "Металлы не могут ржаветь"
            ]
        },
        "en": {
            "true": [
                "Water boils at 100 degrees Celsius",
                "The sun rises in the east",
                "Earth rotates on its axis",
                "There are 365 days in a year",
                "Oxygen is necessary for breathing",
                "Metals conduct electricity",
                "Plants produce oxygen",
                "Ice melts at 0 degrees Celsius",
                "Gravity pulls objects toward Earth's center",
                "Light travels faster than sound",
                "Water consists of hydrogen and oxygen",
                "Humans have 206 bones",
                "The sun is a star",
                "Air is a mixture of gases",
                "Plants need sunlight",
                "Water can exist in three states",
                "Earth has one natural satellite",
                "Oxygen is a gas",
                "Metals have high thermal conductivity",
                "Plants reproduce through seeds",
                "Water is a universal solvent",
                "Humans have five main senses",
                "The sun is a source of energy",
                "Air has mass",
                "Plants absorb carbon dioxide",
                "Water has maximum density at 4°C",
                "Earth has a magnetic field",
                "Oxygen supports combustion",
                "Metals have metallic luster",
                "Plants have root systems",
                "Water can evaporate at any temperature",
                "Humans have 32 teeth",
                "The sun is at the center of the solar system",
                "Air exerts pressure",
                "Plants have leaves",
                "Water can dissolve salts",
                "Earth has an atmosphere",
                "Oxygen is necessary for burning",
                "Metals can be liquid",
                "Plants have stems",
                "Water can freeze",
                "Humans have a heart",
                "The sun emits light",
                "Air contains nitrogen",
                "Plants have flowers",
                "Water can flow",
                "Earth has oceans",
                "Oxygen is an element",
                "Metals can rust"
            ],
            "false": [
                "Water boils at 50 degrees Celsius",
                "The sun rises in the west",
                "Earth is flat",
                "There are 400 days in a year",
                "Oxygen is not needed for breathing",
                "Metals do not conduct electricity",
                "Plants do not produce oxygen",
                "Ice melts at 100 degrees Celsius",
                "Gravity pushes objects away from Earth",
                "Sound travels faster than light",
                "Water consists of carbon and nitrogen",
                "Humans have 100 bones",
                "The sun is a planet",
                "Air is a single gas",
                "Plants do not need sunlight",
                "Water can only exist as a liquid",
                "Earth has two natural satellites",
                "Oxygen is a liquid",
                "Metals do not conduct heat",
                "Plants do not reproduce",
                "Water does not dissolve salts",
                "Humans have three senses",
                "The sun does not emit energy",
                "Air has no mass",
                "Plants do not absorb carbon dioxide",
                "Water has maximum density at 100°C",
                "Earth has no magnetic field",
                "Oxygen does not support combustion",
                "Metals have no luster",
                "Plants have no roots",
                "Water cannot evaporate",
                "Humans have 20 teeth",
                "The sun orbits around Earth",
                "Air does not exert pressure",
                "Plants have no leaves",
                "Water does not dissolve salts",
                "Earth has no atmosphere",
                "Oxygen is not needed for burning",
                "Metals cannot be liquid",
                "Plants have no stems",
                "Water cannot freeze",
                "Humans have no heart",
                "The sun does not emit light",
                "Air contains no nitrogen",
                "Plants have no flowers",
                "Water cannot flow",
                "Earth has no oceans",
                "Oxygen is not an element",
                "Metals cannot rust"
            ]
        }
    },

    #----------------------------------------------------------------------------
    # 11) FUTOSHIKI
    #----------------------------------------------------------------------------
    "futoshiki": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Futoshiki-задача. Заполните поле или укажите, если решения нет.\n"
                "Пример:\n"
                "<reasoning>\n"
                "  (Проверка строк/столбцов и неравенств)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (Матрица решения)\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Futoshiki puzzle. Provide the final grid or no solution.\n"
                "Example:\n"
                "<reasoning>\n"
                "  (Check row constraints, inequalities, etc.)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  (Matrix of the solution)\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": (
                "Задача Futoshiki на поле {size}×{size}. "
                "В каждой строке и каждом столбце нужно расставить числа от 1 до {size} без повторений. "
                "Также даны неравенства:\n"
                "{inequalities}"
            ),
            "en": (
                "Futoshiki puzzle on a {size}×{size} grid. "
                "Each row and column must contain the numbers 1..{size} with no repeats. "
                "Some inequalities are given:\n"
                "{inequalities}"
            )
        },
        "step_explanations": {
            "ru": [
                "Шаг 1: Проверяем ограничения в строке {row}.",
                "Шаг 2: Учитывая ({r1},{c1})<({r2},{c2}), сужаем варианты.",
                "Шаг 3: Убираем повторения в столбце {col}.",
                "Шаг 4: Правило уникальности в строке {row}.",
                "Шаг 5: Уточняем значения."
            ],
            "en": [
                "Step 1: Check constraints in row {row}.",
                "Step 2: Given ({r1},{c1})<({r2},{c2}), reduce possibilities.",
                "Step 3: Remove duplicates in column {col}.",
                "Step 4: Enforce uniqueness in row {row}.",
                "Step 5: Refine values further."
            ]
        },
        "final_answer": {
            "ru": "Итоговое решение Futoshiki:\n{grid_repr}",
            "en": "Final Futoshiki solution:\n{grid_repr}"
        }
    },

    #----------------------------------------------------------------------------
    # 12) URN_PROBABILITY
    #----------------------------------------------------------------------------
    "urn_probability": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Рассчитать вероятность события при выборе ящика и извлечении предметов.\n"
                "Пример:\n"
                "<reasoning>\n"
                "  (Формула, суммирование вероятностей)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  0.3333\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Probability puzzle with multiple containers.\n"
                "Example:\n"
                "<reasoning>\n"
                "  (Derive formula, sum weighted probabilities)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  0.3333\n"
                "</answer>"
            )
        },
        "synonyms": {
            "ru": {
                "containers": ["коробка", "мешок", "ящик", "контейнер"],
                "items": ["шар", "камушек", "предмет"],
                "colors": ["красный", "синий", "зелёный", "белый", "чёрный"]
            },
            "en": {
                "containers": ["box", "bag", "container", "bin"],
                "items": ["ball", "marble", "object", "token"],
                "colors": ["red", "blue", "green", "white", "black"]
            }
        },
        "problem": {
            "ru": (
                "У нас есть {count_containers} {container_syn}. В каждом {container_syn} лежат {item_syn} разных цветов:\n"
                "{details}\n"
                "Выбираем один {container_syn} случайно (равновероятно), затем извлекаем {draws} {item_syn_2} (без возвращения). "
                "Вопрос: {question}"
            ),
            "en": (
                "We have {count_containers} {container_syn}. Each {container_syn} contains {item_syn} of different colors:\n"
                "{details}\n"
                "We pick one {container_syn} at random (equal probability) and then draw {draws} {item_syn_2} (without replacement). "
                "Question: {question}"
            )
        },
        "steps": {
            "ru": [
                "Шаг 1: Вероятность выбора каждого {container_syn} = 1/{count_containers}.",
                "Шаг 2: Для {container_syn} №{idx} вычислим вероятность события.",
                "Шаг 3: Суммируем взвешенные вероятности.",
                "Шаг 4: Упрощаем выражение."
            ],
            "en": [
                "Step 1: Probability of picking each {container_syn} is 1/{count_containers}.",
                "Step 2: For {container_syn} #{idx}, compute event probability.",
                "Step 3: Sum weighted probabilities.",
                "Step 4: Simplify the expression."
            ]
        },
        "final_answer": {
            "ru": "Итоговая вероятность события: {prob_value}",
            "en": "The final probability of the event is: {prob_value}"
        },
        "questions_pool": {
            "ru": [
                "все {draws} {item_syn} окажутся {color}",
                "хотя бы один {item_syn} будет {color}",
                "ровно {x} из {draws} {item_syn} будут {color}"
            ],
            "en": [
                "all {draws} {item_syn} drawn are {color}",
                "at least one {item_syn} is {color}",
                "exactly {x} out of {draws} {item_syn} are {color}"
            ]
        }
    },

    #----------------------------------------------------------------------------
    # 13) KNIGHTS_KNAVES
    #----------------------------------------------------------------------------
    "knights_knaves": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Определите, кто из жителей острова рыцарь (всегда говорит правду), а кто лжец (всегда лжёт).\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Логические рассуждения по шагам)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Роль каждого жителя: рыцарь/лжец)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Determine which inhabitants are knights (always tell truth) and which are knaves (always lie).\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step logical reasoning)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Role of each inhabitant: knight/knave)\n"
                "  </answer>"
            )
        },
        "intro": {
            "ru": "У нас есть три персонажей: {names}.",
            "en": "We have three characters: {names}."
        },
        "names_pool": {
            "ru": ["Алекс", "Борис", "Виктор", "Григорий", "Дмитрий", 
                  "Елена", "Жанна", "Зоя", "Ирина", "Карина",
                  "Леонид", "Мария", "Николай", "Ольга", "Павел",
                  "Роман", "Светлана", "Тимофей", "Ульяна", "Федор",
                  "Харитон", "Цветана", "Чеслав", "Шарлотта", "Эдуард",
                  "Юрий", "Ярослав", "Анна", "Богдан", "Валентина",
                  "Галина", "Даниил", "Евгений", "Жорж", "Зинаида",
                  "Игорь", "Ксения", "Лев", "Маргарита", "Наталья",
                  "Олег", "Петр", "Раиса", "Сергей", "Татьяна",
                  "Устин", "Фаина", "Христина", "Цезарь", "Чарльз"],
            "en": ["Alex", "Bob", "Charlie", "David", "Eve",
                  "Frank", "George", "Helen", "Ivan", "Jack",
                  "Kevin", "Lily", "Mike", "Nina", "Oliver",
                  "Peter", "Quinn", "Rachel", "Sam", "Tom",
                  "Uma", "Victor", "Wendy", "Xavier", "Yara",
                  "Zack", "Alice", "Ben", "Clara", "Dan",
                  "Emma", "Fred", "Gina", "Henry", "Iris",
                  "James", "Kate", "Leo", "Maya", "Nate",
                  "Oscar", "Penny", "Quinn", "Rose", "Steve",
                  "Tina", "Uri", "Vera", "Wade", "Xena"]
        },
        "problem": {
            "ru": "Известно, что {statements}. Определите, кто из них рыцарь, а кто — лжец",
            "en": "It is known that {statements}. Determine who is a knight and who is a knave"
        },
        "forms": {
            "ru": {
                "statement": "{name} говорит: \"{text}\"",
                "about_self": "Я {role}",
                "about_other": "{name} - {role}",
                "and": "{name} и {other_name} оба {role}",
                "or": "{name} или {other_name} - {role}",
                "same": "{name} и {other_name} одного типа",
                "different": "{name} и {other_name} разных типов",
                "at_least_one": "Хотя бы один из нас - {role}",
                "exactly_one": "Ровно один из нас - {role}"
            },
            "en": {
                "statement": "{name} says: \"{text}\"",
                "about_self": "I am a {role}",
                "about_other": "{name} is a {role}",
                "and": "Both {name} and {other_name} are {role}s",
                "or": "Either {name} or {other_name} is a {role}",
                "same": "{name} and {other_name} are of the same type",
                "different": "{name} and {other_name} are of different types",
                "at_least_one": "At least one of us is a {role}",
                "exactly_one": "Exactly one of us is a {role}"
            }
        },
        "step1": {
            "ru": "Шаг 1: Проанализируем высказывания каждого жителя, учитывая, что рыцари всегда говорят правду, а лжецы всегда лгут.",
            "en": "Step 1: Let's analyze each inhabitant's statement, considering that knights always tell the truth and knaves always lie."
        },
        "final_step": {
            "ru": "На основе анализа высказываний и их логических следствий, мы можем определить роль каждого жителя.",
            "en": "Based on the analysis of statements and their logical implications, we can determine each inhabitant's role."
        },
        "final_answer": {
            "ru": "Роли жителей:\n{roles}",
            "en": "Inhabitants' roles:\n{roles}"
        },
        "explanation": {
            "ru": "Это решение основано на том, что рыцари всегда говорят правду, а лжецы всегда лгут.",
            "en": "This solution is based on the fact that knights always tell the truth and knaves always lie."
        }
    },

    #----------------------------------------------------------------------------
    # 15) TEXT_STATS
    #----------------------------------------------------------------------------
    "text_stats": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Подсчитать, сколько раз подстрока встречается в тексте.\n"
                "Пример:\n"
                "<reasoning>\n"
                "  (Проверяем все вхождения, учитывая пересечения)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  4\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Count how many times a substring appears in the text.\n"
                "Example:\n"
                "<reasoning>\n"
                "  (Checking all occurrences, possibly overlapping)\n"
                "</reasoning>\n"
                "<answer>\n"
                "  4\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": "Определите, сколько раз подстрока «{substring}» встречается в тексте:\n{text}",
            "en": "Determine how many times the substring \"{substring}\" appears in the following text:\n{text}"
        },
        "steps": {
            "ru": [
                "Шаг 1: Перебираем все вхождения (учитывая {allow_overlapping}).",
                "Шаг 2: Подсчитываем число вхождений «{substring}».",
                "Шаг 3: Если allow_overlapping=True, учитываем пересечения."
            ],
            "en": [
                "Step 1: Traverse text for all occurrences (considering {allow_overlapping}).",
                "Step 2: Count how many times \"{substring}\" appears.",
                "Step 3: If allow_overlapping=True, handle overlaps."
            ]
        },
        "final_answer": {
            "ru": "Итоговый ответ: {count_value} вхождений.",
            "en": "Final answer: {count_value} occurrences."
        },
        "vocab": {
            "ru": [
                "стол", "стул", "магазин", "программирование", "мир",
                "книга", "пес", "автомобиль", "улица", "abc", "zzz"
            ],
            "en": [
                "chair", "table", "store", "programming", "world",
                "book", "dog", "car", "street", "abc", "zzz"
            ]
        },
        "alphabet": {
            "ru": "абвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789",
            "en": "abcdefghijklmnopqrstuvwxyz0123456789"
        }
    },

    #----------------------------------------------------------------------------
    # 16) ARITHMETIC
    #----------------------------------------------------------------------------
    "arithmetic": {
        "misc": {
            "step_calculate_expr": {
                "ru": "Шаг 1: Вычисляем выражение {expression}",
                "en": "Step 1: Calculate the expression {expression}"
            },
            "step_result": {
                "ru": "Шаг 2: Результат = {result}",
                "en": "Step 2: Result = {result}"
            },
            "step_sqrt": {
                "ru": "Шаг {step}: Вычисляем √({value}) = {result}",
                "en": "Step {step}: Calculate sqrt({value}) = {result}"
            },
            "step_operation": {
                "ru": "Шаг {step}: {operation} {left} {op} {right} = {result}",
                "en": "Step {step}: {operation} {left} {op} {right} = {result}"
            }
        },
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Вычислите арифметическое выражение.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговые вычисления)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый результат)\n"
                "  </answer>\n"
                "Пример:\n"
                "<reasoning>\n"
                "  Шаг 1: Вычисляем выражение в скобках: (3 + 5) = 8\n"
                "  Шаг 2: Умножаем: 8 × 2 = 16\n"
                "</reasoning>\n"
                "<answer>\n"
                "  16\n"
                "</answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Calculate the arithmetic expression.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step calculations)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final result)\n"
                "  </answer>\n"
                "Example:\n"
                "<reasoning>\n"
                "  Step 1: Calculate the expression in parentheses: (3 + 5) = 8\n"
                "  Step 2: Multiply: 8 * 2 = 16\n"
                "</reasoning>\n"
                "<answer>\n"
                "  16\n"
                "</answer>"
            )
        },
        "problem": {
            "ru": "Вычислите: {expression}",
            "en": "Calculate: {expression}"
        },
        "step_evaluate": {
            "ru": "Шаг {step}: Вычисляем {operation}: {left} {op} {right} = {result}",
            "en": "Step {step}: Calculate {operation}: {left} {op} {right} = {result}"
        },
        "step_parentheses": {
            "ru": "Шаг {step}: Вычисляем выражение в скобках: {expr} = {result}",
            "en": "Step {step}: Calculate the expression in parentheses: {expr} = {result}"
        },
        "step_sqrt": {
            "ru": "Шаг {step}: Вычисляем квадратный корень: √({value}) = {result}",
            "en": "Step {step}: Calculate square root: sqrt({value}) = {result}"
        },
        "step_power": {
            "ru": "Шаг {step}: Возводим в степень: {base}^{exp} = {result}",
            "en": "Step {step}: Raise to power: {base}^{exp} = {result}"
        },
        "step_percentage": {
            "ru": "Шаг {step}: Вычисляем процент: {percent}% от {value} = {result}",
            "en": "Step {step}: Calculate percentage: {percent}% of {value} = {result}"
        },
        "final_answer": {
            "ru": "Итоговый ответ: {result}",
            "en": "Final answer: {result}"
        },
        "operations": {
            "ru": {
                "+": "сложение",
                "-": "вычитание",
                "*": "умножение",
                "/": "деление",
                "^": "возведение в степень",
                "sqrt": "извлечение корня"
            },
            "en": {
                "+": "addition",
                "-": "subtraction",
                "*": "multiplication",
                "/": "division",
                "^": "exponentiation",
                "sqrt": "square root"
            }
        }
    },

    #----------------------------------------------------------------------------
    # 17) NUMBER_THEORY - Теория чисел
    #----------------------------------------------------------------------------
    "number_theory": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по теории чисел.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the number theory problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "gcd_lcm": {
                "ru": "Найдите НОД и НОК чисел {a} и {b}.",
                "en": "Find the GCD and LCM of {a} and {b}."
            },
            "prime_factorization": {
                "ru": "Разложите число {n} на простые множители.",
                "en": "Find the prime factorization of {n}."
            },
            "modular_arithmetic": {
                "ru": "Вычислите {a}^{b} mod {m}.",
                "en": "Calculate {a}^{b} mod {m}."
            },
            "chinese_remainder": {
                "ru": "Решите систему сравнений:\n{equations}\nНайдите x.",
                "en": "Solve the system of congruences:\n{equations}\nFind x."
            },
            "divisibility": {
                "ru": "Определите, делится ли число {n} на {d}. Объясните ответ.",
                "en": "Determine whether {n} is divisible by {d}. Explain your answer."
            },
            "diophantine": {
                "ru": "Найдите все целые решения уравнения {a}x + {b}y = {c}.",
                "en": "Find all integer solutions to the equation {a}x + {b}y = {c}."
            },
            "euler_totient": {
                "ru": "Вычислите функцию Эйлера φ({n}).",
                "en": "Calculate Euler's totient function φ({n})."
            }
        },
        "steps": {
            "gcd_euclidean": {
                "ru": "Шаг {step}: Применяем алгоритм Евклида: {a} = {b} × {q} + {r}",
                "en": "Step {step}: Apply Euclidean algorithm: {a} = {b} × {q} + {r}"
            },
            "gcd_found": {
                "ru": "НОД({a}, {b}) = {gcd}",
                "en": "GCD({a}, {b}) = {gcd}"
            },
            "lcm_formula": {
                "ru": "НОК({a}, {b}) = {a} × {b} / НОД({a}, {b}) = {lcm}",
                "en": "LCM({a}, {b}) = {a} × {b} / GCD({a}, {b}) = {lcm}"
            },
            "factor_found": {
                "ru": "Шаг {step}: {n} = {factor} × {quotient}",
                "en": "Step {step}: {n} = {factor} × {quotient}"
            },
            "factorization_result": {
                "ru": "Разложение: {n} = {factorization}",
                "en": "Factorization: {n} = {factorization}"
            },
            "mod_exp_step": {
                "ru": "Шаг {step}: {base}^{exp} ≡ {result} (mod {m})",
                "en": "Step {step}: {base}^{exp} ≡ {result} (mod {m})"
            },
            "crt_step": {
                "ru": "Шаг {step}: x ≡ {a} (mod {m}), M_{i} = {M_i}, y_{i} = {y_i}",
                "en": "Step {step}: x ≡ {a} (mod {m}), M_i = {M_i}, y_i = {y_i}"
            },
            "diophantine_gcd": {
                "ru": "Шаг 1: НОД({a}, {b}) = {gcd}. Уравнение имеет решения, т.к. {gcd} | {c}.",
                "en": "Step 1: GCD({a}, {b}) = {gcd}. The equation has solutions since {gcd} | {c}."
            },
            "diophantine_particular": {
                "ru": "Шаг 2: Частное решение: x₀ = {x0}, y₀ = {y0}",
                "en": "Step 2: Particular solution: x₀ = {x0}, y₀ = {y0}"
            },
            "diophantine_general": {
                "ru": "Шаг 3: Общее решение: x = {x0} + {b_div}t, y = {y0} - {a_div}t, где t ∈ ℤ",
                "en": "Step 3: General solution: x = {x0} + {b_div}t, y = {y0} - {a_div}t, where t ∈ ℤ"
            },
            "euler_factorize": {
                "ru": "Шаг 1: Разложение {n} = {factorization}",
                "en": "Step 1: Factorization {n} = {factorization}"
            },
            "euler_formula": {
                "ru": "Шаг 2: φ({n}) = {n} × {product_terms} = {result}",
                "en": "Step 2: φ({n}) = {n} × {product_terms} = {result}"
            },
            "divisibility_divide": {
                "ru": "Шаг 1: Делим {n} на {d}: {n} ÷ {d} = {quotient}",
                "en": "Step 1: Divide {n} by {d}: {n} ÷ {d} = {quotient}"
            },
            "divisibility_remainder": {
                "ru": "Шаг 1: Делим {n} на {d}: {n} = {d} × {quotient} + {remainder}",
                "en": "Step 1: Divide {n} by {d}: {n} = {d} × {quotient} + {remainder}"
            },
            "divisibility_yes": {
                "ru": "Шаг 2: Остаток равен 0, следовательно {n} делится на {d}.",
                "en": "Step 2: Remainder is 0, therefore {n} is divisible by {d}."
            },
            "divisibility_no": {
                "ru": "Шаг 2: Остаток равен {remainder} ≠ 0, следовательно {n} не делится на {d}.",
                "en": "Step 2: Remainder is {remainder} ≠ 0, therefore {n} is not divisible by {d}."
            }
        },
        "answers": {
            "divisible_yes": {
                "ru": "Да, {n} делится на {d}",
                "en": "Yes, {n} is divisible by {d}"
            },
            "divisible_no": {
                "ru": "Нет, остаток = {remainder}",
                "en": "No, remainder = {remainder}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 18) COMBINATORICS - Комбинаторика
    #----------------------------------------------------------------------------
    "combinatorics": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите комбинаторную задачу.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение с формулами)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Числовой ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the combinatorics problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution with formulas)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Numerical answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "permutations": {
                "ru": "Сколькими способами можно расположить {n} различных предметов в ряд?",
                "en": "In how many ways can {n} distinct objects be arranged in a row?"
            },
            "permutations_k": {
                "ru": "Сколькими способами можно выбрать и расположить {k} предметов из {n} различных?",
                "en": "In how many ways can we select and arrange {k} objects from {n} distinct objects?"
            },
            "combinations": {
                "ru": "Сколькими способами можно выбрать {k} предметов из {n} различных (порядок не важен)?",
                "en": "In how many ways can we choose {k} objects from {n} distinct objects (order doesn't matter)?"
            },
            "combinations_repetition": {
                "ru": "Сколькими способами можно выбрать {k} предметов из {n} видов с повторениями?",
                "en": "In how many ways can we choose {k} objects from {n} types with repetition allowed?"
            },
            "binomial": {
                "ru": "Вычислите биномиальный коэффициент C({n}, {k}).",
                "en": "Calculate the binomial coefficient C({n}, {k})."
            },
            "multinomial": {
                "ru": "Сколькими способами можно разбить {n} предметов на группы размеров {groups}?",
                "en": "In how many ways can {n} objects be divided into groups of sizes {groups}?"
            },
            "pigeonhole": {
                "ru": "В ящике {n} носков {k} разных цветов. Какое минимальное число носков нужно достать, чтобы гарантированно получить {m} носков одного цвета?",
                "en": "A drawer contains {n} socks of {k} different colors. What is the minimum number of socks to pick to guarantee {m} socks of the same color?"
            },
            "inclusion_exclusion": {
                "ru": "Используя формулу включения-исключения, найдите количество целых чисел от 1 до {n}, которые делятся хотя бы на одно из чисел: {divisors}.",
                "en": "Using inclusion-exclusion, find the count of integers from 1 to {n} divisible by at least one of: {divisors}."
            },
            "derangements": {
                "ru": "Сколько существует беспорядков (перестановок без неподвижных точек) для {n} элементов?",
                "en": "How many derangements (permutations with no fixed points) exist for {n} elements?"
            },
            "stars_and_bars": {
                "ru": "Сколькими способами можно разложить {n} одинаковых шаров по {k} различным ящикам?",
                "en": "In how many ways can {n} identical balls be distributed into {k} distinct boxes?"
            },
            "circular_permutation": {
                "ru": "Сколькими способами можно рассадить {n} человек за круглый стол?",
                "en": "In how many ways can {n} people be seated around a circular table?"
            }
        },
        "steps": {
            "factorial": {
                "ru": "Шаг {step}: {n}! = {result}",
                "en": "Step {step}: {n}! = {result}"
            },
            "permutation_formula": {
                "ru": "Шаг {step}: P({n}, {k}) = {n}! / ({n}-{k})! = {result}",
                "en": "Step {step}: P({n}, {k}) = {n}! / ({n}-{k})! = {result}"
            },
            "combination_formula": {
                "ru": "Шаг {step}: C({n}, {k}) = {n}! / ({k}! × ({n}-{k})!) = {result}",
                "en": "Step {step}: C({n}, {k}) = {n}! / ({k}! × ({n}-{k})!) = {result}"
            },
            "combination_rep_formula": {
                "ru": "Шаг {step}: C({n}+{k}-1, {k}) = C({n_plus_k_minus_1}, {k}) = {result}",
                "en": "Step {step}: C({n}+{k}-1, {k}) = C({n_plus_k_minus_1}, {k}) = {result}"
            },
            "multinomial_formula": {
                "ru": "Шаг {step}: Мультиномиальный коэффициент = {n}! / ({factorials}) = {result}",
                "en": "Step {step}: Multinomial coefficient = {n}! / ({factorials}) = {result}"
            },
            "pigeonhole_formula": {
                "ru": "Шаг {step}: По принципу Дирихле: ({m}-1) × {k} + 1 = {result}",
                "en": "Step {step}: By pigeonhole principle: ({m}-1) × {k} + 1 = {result}"
            },
            "inclusion_exclusion_step": {
                "ru": "Шаг {step}: |A_{sets}| = {count}",
                "en": "Step {step}: |A_{sets}| = {count}"
            },
            "derangement_formula": {
                "ru": "Шаг {step}: D({n}) = {n}! × Σ((-1)^k / k!) = {result}",
                "en": "Step {step}: D({n}) = {n}! × Σ((-1)^k / k!) = {result}"
            },
            "circular_formula": {
                "ru": "Шаг {step}: Круговые перестановки = ({n}-1)! = {result}",
                "en": "Step {step}: Circular permutations = ({n}-1)! = {result}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 19) SEQUENCE - Последовательности
    #----------------------------------------------------------------------------
    "sequence": {
        "misc": {
            "sum_arithmetic": {
                "ru": "Шаг 1: Сумма 1 + 2 + ... + n = n(n+1)/2 = {n}×{n_plus_1}/2 = {result}",
                "en": "Step 1: Sum 1 + 2 + ... + n = n(n+1)/2 = {n}×{n_plus_1}/2 = {result}"
            },
            "sum_squares": {
                "ru": "Шаг 1: Сумма квадратов = n(n+1)(2n+1)/6 = {result}",
                "en": "Step 1: Sum of squares = n(n+1)(2n+1)/6 = {result}"
            }
        },
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу на последовательности.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Анализ закономерности и вычисления)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the sequence problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Pattern analysis and calculations)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "arithmetic_nth": {
                "ru": "Найдите {n}-й член арифметической прогрессии с первым членом {a1} и разностью {d}.",
                "en": "Find the {n}th term of an arithmetic sequence with first term {a1} and common difference {d}."
            },
            "arithmetic_sum": {
                "ru": "Найдите сумму первых {n} членов арифметической прогрессии с первым членом {a1} и разностью {d}.",
                "en": "Find the sum of the first {n} terms of an arithmetic sequence with first term {a1} and common difference {d}."
            },
            "geometric_nth": {
                "ru": "Найдите {n}-й член геометрической прогрессии с первым членом {a1} и знаменателем {r}.",
                "en": "Find the {n}th term of a geometric sequence with first term {a1} and common ratio {r}."
            },
            "geometric_sum": {
                "ru": "Найдите сумму первых {n} членов геометрической прогрессии с первым членом {a1} и знаменателем {r}.",
                "en": "Find the sum of the first {n} terms of a geometric sequence with first term {a1} and common ratio {r}."
            },
            "fibonacci_nth": {
                "ru": "Найдите {n}-е число Фибоначчи (F₁ = 1, F₂ = 1).",
                "en": "Find the {n}th Fibonacci number (F₁ = 1, F₂ = 1)."
            },
            "recurrence": {
                "ru": "Дана рекуррентная формула: a_{n} = {formula}, a₁ = {a1}. Найдите a_{target}.",
                "en": "Given the recurrence: a_n = {formula}, a₁ = {a1}. Find a_{target}."
            },
            "pattern": {
                "ru": "Найдите закономерность и следующий член последовательности: {sequence}, ?",
                "en": "Find the pattern and the next term of the sequence: {sequence}, ?"
            },
            "series_sum": {
                "ru": "Найдите сумму ряда: {series}",
                "en": "Find the sum of the series: {series}"
            }
        },
        "steps": {
            "arithmetic_formula": {
                "ru": "Шаг {step}: a_n = a₁ + (n-1)d = {a1} + ({n}-1)×{d} = {result}",
                "en": "Step {step}: a_n = a₁ + (n-1)d = {a1} + ({n}-1)×{d} = {result}"
            },
            "arithmetic_sum_formula": {
                "ru": "Шаг {step}: S_n = n(a₁ + a_n)/2 = {n}×({a1} + {an})/2 = {result}",
                "en": "Step {step}: S_n = n(a₁ + a_n)/2 = {n}×({a1} + {an})/2 = {result}"
            },
            "geometric_formula": {
                "ru": "Шаг {step}: a_n = a₁ × r^(n-1) = {a1} × {r}^({n}-1) = {result}",
                "en": "Step {step}: a_n = a₁ × r^(n-1) = {a1} × {r}^({n}-1) = {result}"
            },
            "geometric_sum_formula": {
                "ru": "Шаг {step}: S_n = a₁(r^n - 1)/(r - 1) = {result}",
                "en": "Step {step}: S_n = a₁(r^n - 1)/(r - 1) = {result}"
            },
            "fibonacci_step": {
                "ru": "Шаг {step}: F_{n} = F_{n_minus_1} + F_{n_minus_2} = {f1} + {f2} = {result}",
                "en": "Step {step}: F_{n} = F_{n_minus_1} + F_{n_minus_2} = {f1} + {f2} = {result}"
            },
            "recurrence_step": {
                "ru": "Шаг {step}: a_{n} = {formula_applied} = {result}",
                "en": "Step {step}: a_{n} = {formula_applied} = {result}"
            },
            "pattern_identified": {
                "ru": "Шаг {step}: Обнаружена закономерность: {pattern_description}",
                "en": "Step {step}: Pattern identified: {pattern_description}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 20) GEOMETRY - Геометрия
    #----------------------------------------------------------------------------
    "geometry": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите геометрическую задачу.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение с формулами)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the geometry problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution with formulas)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "triangle_area_coords": {
                "ru": "Найдите площадь треугольника с вершинами A({x1}, {y1}), B({x2}, {y2}), C({x3}, {y3}).",
                "en": "Find the area of the triangle with vertices A({x1}, {y1}), B({x2}, {y2}), C({x3}, {y3})."
            },
            "triangle_area_sides": {
                "ru": "Найдите площадь треугольника со сторонами a = {a}, b = {b}, c = {c}.",
                "en": "Find the area of the triangle with sides a = {a}, b = {b}, c = {c}."
            },
            "distance_2d": {
                "ru": "Найдите расстояние между точками A({x1}, {y1}) и B({x2}, {y2}).",
                "en": "Find the distance between points A({x1}, {y1}) and B({x2}, {y2})."
            },
            "distance_3d": {
                "ru": "Найдите расстояние между точками A({x1}, {y1}, {z1}) и B({x2}, {y2}, {z2}).",
                "en": "Find the distance between points A({x1}, {y1}, {z1}) and B({x2}, {y2}, {z2})."
            },
            "circle_area": {
                "ru": "Найдите площадь круга с радиусом {r}.",
                "en": "Find the area of a circle with radius {r}."
            },
            "circle_circumference": {
                "ru": "Найдите длину окружности с радиусом {r}.",
                "en": "Find the circumference of a circle with radius {r}."
            },
            "rectangle_area": {
                "ru": "Найдите площадь прямоугольника со сторонами {a} и {b}.",
                "en": "Find the area of a rectangle with sides {a} and {b}."
            },
            "sphere_volume": {
                "ru": "Найдите объём шара с радиусом {r}.",
                "en": "Find the volume of a sphere with radius {r}."
            },
            "cylinder_volume": {
                "ru": "Найдите объём цилиндра с радиусом основания {r} и высотой {h}.",
                "en": "Find the volume of a cylinder with base radius {r} and height {h}."
            },
            "cone_volume": {
                "ru": "Найдите объём конуса с радиусом основания {r} и высотой {h}.",
                "en": "Find the volume of a cone with base radius {r} and height {h}."
            },
            "angle_between_vectors": {
                "ru": "Найдите угол между векторами a = ({ax}, {ay}) и b = ({bx}, {by}).",
                "en": "Find the angle between vectors a = ({ax}, {ay}) and b = ({bx}, {by})."
            },
            "dot_product": {
                "ru": "Найдите скалярное произведение векторов a = ({ax}, {ay}, {az}) и b = ({bx}, {by}, {bz}).",
                "en": "Find the dot product of vectors a = ({ax}, {ay}, {az}) and b = ({bx}, {by}, {bz})."
            },
            "cross_product": {
                "ru": "Найдите векторное произведение векторов a = ({ax}, {ay}, {az}) и b = ({bx}, {by}, {bz}).",
                "en": "Find the cross product of vectors a = ({ax}, {ay}, {az}) and b = ({bx}, {by}, {bz})."
            },
            "line_equation": {
                "ru": "Напишите уравнение прямой, проходящей через точки A({x1}, {y1}) и B({x2}, {y2}).",
                "en": "Write the equation of the line passing through points A({x1}, {y1}) and B({x2}, {y2})."
            },
            "midpoint": {
                "ru": "Найдите координаты середины отрезка AB, где A({x1}, {y1}) и B({x2}, {y2}).",
                "en": "Find the coordinates of the midpoint of segment AB, where A({x1}, {y1}) and B({x2}, {y2})."
            }
        },
        "steps": {
            "triangle_area_formula": {
                "ru": "Шаг {step}: S = ½|x₁(y₂-y₃) + x₂(y₃-y₁) + x₃(y₁-y₂)| = {result}",
                "en": "Step {step}: S = ½|x₁(y₂-y₃) + x₂(y₃-y₁) + x₃(y₁-y₂)| = {result}"
            },
            "heron_formula": {
                "ru": "Шаг {step}: Полупериметр p = (a+b+c)/2 = {p}. S = √(p(p-a)(p-b)(p-c)) = {result}",
                "en": "Step {step}: Semi-perimeter p = (a+b+c)/2 = {p}. S = √(p(p-a)(p-b)(p-c)) = {result}"
            },
            "distance_formula_2d": {
                "ru": "Шаг {step}: d = √((x₂-x₁)² + (y₂-y₁)²) = √(({dx})² + ({dy})²) = {result}",
                "en": "Step {step}: d = √((x₂-x₁)² + (y₂-y₁)²) = √(({dx})² + ({dy})²) = {result}"
            },
            "distance_formula_3d": {
                "ru": "Шаг {step}: d = √((x₂-x₁)² + (y₂-y₁)² + (z₂-z₁)²) = {result}",
                "en": "Step {step}: d = √((x₂-x₁)² + (y₂-y₁)² + (z₂-z₁)²) = {result}"
            },
            "circle_area_formula": {
                "ru": "Шаг {step}: S = πr² = π × {r}² = {result}",
                "en": "Step {step}: S = πr² = π × {r}² = {result}"
            },
            "circumference_formula": {
                "ru": "Шаг {step}: C = 2πr = 2π × {r} = {result}",
                "en": "Step {step}: C = 2πr = 2π × {r} = {result}"
            },
            "sphere_volume_formula": {
                "ru": "Шаг {step}: V = (4/3)πr³ = (4/3)π × {r}³ = {result}",
                "en": "Step {step}: V = (4/3)πr³ = (4/3)π × {r}³ = {result}"
            },
            "cylinder_volume_formula": {
                "ru": "Шаг {step}: V = πr²h = π × {r}² × {h} = {result}",
                "en": "Step {step}: V = πr²h = π × {r}² × {h} = {result}"
            },
            "cone_volume_formula": {
                "ru": "Шаг {step}: V = (1/3)πr²h = (1/3)π × {r}² × {h} = {result}",
                "en": "Step {step}: V = (1/3)πr²h = (1/3)π × {r}² × {h} = {result}"
            },
            "dot_product_formula": {
                "ru": "Шаг {step}: a·b = ax×bx + ay×by + az×bz = {result}",
                "en": "Step {step}: a·b = ax×bx + ay×by + az×bz = {result}"
            },
            "cross_product_formula": {
                "ru": "Шаг {step}: a×b = ({i_comp}, {j_comp}, {k_comp})",
                "en": "Step {step}: a×b = ({i_comp}, {j_comp}, {k_comp})"
            },
            "angle_formula": {
                "ru": "Шаг {step}: cos(θ) = (a·b)/(|a||b|) = {cos_val}, θ = {angle}°",
                "en": "Step {step}: cos(θ) = (a·b)/(|a||b|) = {cos_val}, θ = {angle}°"
            },
            "line_slope": {
                "ru": "Шаг {step}: Угловой коэффициент k = (y₂-y₁)/(x₂-x₁) = {slope}",
                "en": "Step {step}: Slope k = (y₂-y₁)/(x₂-x₁) = {slope}"
            },
            "line_equation_result": {
                "ru": "Шаг {step}: Уравнение прямой: y = {slope}x + {intercept}",
                "en": "Step {step}: Line equation: y = {slope}x + {intercept}"
            },
            "vertical_line": {
                "ru": "Шаг 1: Прямая вертикальная, уравнение: x = {x}",
                "en": "Step 1: Vertical line, equation: x = {x}"
            },
            "midpoint_formula": {
                "ru": "Шаг {step}: M = ((x₁+x₂)/2, (y₁+y₂)/2) = ({mx}, {my})",
                "en": "Step {step}: M = ((x₁+x₂)/2, (y₁+y₂)/2) = ({mx}, {my})"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 21) MATRIX - Матрицы
    #----------------------------------------------------------------------------
    "matrix": {
        "misc": {
            "singular_matrix": {
                "ru": "Матрица вырождена",
                "en": "Matrix is singular"
            },
            "det_step": {
                "ru": "Шаг 2: det(A) = {det}",
                "en": "Step 2: det(A) = {det}"
            },
            "reduce_to_echelon": {
                "ru": "Шаг 1: Приводим матрицу к ступенчатому виду",
                "en": "Step 1: Reduce matrix to row echelon form"
            },
            "count_nonzero_rows": {
                "ru": "Шаг 2: Считаем ненулевые строки: {rank}",
                "en": "Step 2: Count non-zero rows: {rank}"
            },
            "trace_formula": {
                "ru": "Шаг 1: tr(A) = {diag_str} = {trace}",
                "en": "Step 1: tr(A) = {diag_str} = {trace}"
            },
            "add_elements": {
                "ru": "Шаг 1: Складываем соответствующие элементы матриц",
                "en": "Step 1: Add corresponding elements of matrices"
            },
            "scalar_multiply": {
                "ru": "Шаг 1: Умножаем каждый элемент на {scalar}",
                "en": "Step 1: Multiply each element by {scalar}"
            }
        },
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу с матрицами.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговая матрица или число)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the matrix problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final matrix or number)\n"
                "  </answer>"
            )
        },
        "problem": {
            "determinant": {
                "ru": "Найдите определитель матрицы:\n{matrix}",
                "en": "Find the determinant of the matrix:\n{matrix}"
            },
            "inverse": {
                "ru": "Найдите обратную матрицу для:\n{matrix}",
                "en": "Find the inverse of the matrix:\n{matrix}"
            },
            "multiplication": {
                "ru": "Найдите произведение матриц A × B:\nA = {matrix_a}\nB = {matrix_b}",
                "en": "Find the product of matrices A × B:\nA = {matrix_a}\nB = {matrix_b}"
            },
            "transpose": {
                "ru": "Найдите транспонированную матрицу:\n{matrix}",
                "en": "Find the transpose of the matrix:\n{matrix}"
            },
            "rank": {
                "ru": "Найдите ранг матрицы:\n{matrix}",
                "en": "Find the rank of the matrix:\n{matrix}"
            },
            "eigenvalues": {
                "ru": "Найдите собственные значения матрицы:\n{matrix}",
                "en": "Find the eigenvalues of the matrix:\n{matrix}"
            },
            "trace": {
                "ru": "Найдите след (сумму диагональных элементов) матрицы:\n{matrix}",
                "en": "Find the trace (sum of diagonal elements) of the matrix:\n{matrix}"
            },
            "add": {
                "ru": "Найдите сумму матриц A + B:\nA = {matrix_a}\nB = {matrix_b}",
                "en": "Find the sum of matrices A + B:\nA = {matrix_a}\nB = {matrix_b}"
            },
            "scalar_mult": {
                "ru": "Найдите произведение скаляра {scalar} на матрицу:\n{matrix}",
                "en": "Find the product of scalar {scalar} and the matrix:\n{matrix}"
            }
        },
        "steps": {
            "det_2x2": {
                "ru": "Шаг {step}: det(A) = a₁₁×a₂₂ - a₁₂×a₂₁ = {a11}×{a22} - {a12}×{a21} = {result}",
                "en": "Step {step}: det(A) = a₁₁×a₂₂ - a₁₂×a₂₁ = {a11}×{a22} - {a12}×{a21} = {result}"
            },
            "det_expansion": {
                "ru": "Шаг {step}: Разложение по {row_col} {index}: det = {expansion} = {result}",
                "en": "Step {step}: Expansion along {row_col} {index}: det = {expansion} = {result}"
            },
            "cofactor": {
                "ru": "Шаг {step}: Алгебраическое дополнение A_{i}{j} = (-1)^({i}+{j}) × M_{i}{j} = {result}",
                "en": "Step {step}: Cofactor A_{i}{j} = (-1)^({i}+{j}) × M_{i}{j} = {result}"
            },
            "inverse_formula": {
                "ru": "Шаг {step}: A⁻¹ = (1/det(A)) × adj(A)",
                "en": "Step {step}: A⁻¹ = (1/det(A)) × adj(A)"
            },
            "multiplication_element": {
                "ru": "Шаг {step}: C_{i}{j} = Σ(A_{i}k × B_k{j}) = {result}",
                "en": "Step {step}: C_{i}{j} = Σ(A_{i}k × B_k{j}) = {result}"
            },
            "transpose_result": {
                "ru": "Шаг {step}: Aᵀ[{i}][{j}] = A[{j}][{i}] = {result}",
                "en": "Step {step}: Aᵀ[{i}][{j}] = A[{j}][{i}] = {result}"
            },
            "eigenvalue_char_poly": {
                "ru": "Шаг {step}: Характеристический многочлен: det(A - λI) = {poly}",
                "en": "Step {step}: Characteristic polynomial: det(A - λI) = {poly}"
            },
            "eigenvalue_roots": {
                "ru": "Шаг {step}: Собственные значения (корни): λ = {eigenvalues}",
                "en": "Step {step}: Eigenvalues (roots): λ = {eigenvalues}"
            },
            "row_operation": {
                "ru": "Шаг {step}: R{i} → {operation}",
                "en": "Step {step}: R{i} → {operation}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 22) TRIGONOMETRY - Тригонометрия
    #----------------------------------------------------------------------------
    "trigonometry": {
        "misc": {
            "triangle_step2": {
                "ru": "Шаг 2: c² = {a}² + {b}² - 2×{a}×{b}×cos({angle}°)",
                "en": "Step 2: c² = {a}² + {b}² - 2×{a}×{b}×cos({angle}°)"
            },
            "triangle_step3": {
                "ru": "Шаг 3: c = {result}",
                "en": "Step 3: c = {result}"
            }
        },
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите тригонометрическую задачу.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the trigonometry problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "basic_value": {
                "ru": "Вычислите {func}({angle}).",
                "en": "Calculate {func}({angle})."
            },
            "equation": {
                "ru": "Решите уравнение {equation} на интервале {interval}.",
                "en": "Solve the equation {equation} on the interval {interval}."
            },
            "identity": {
                "ru": "Упростите выражение: {expression}",
                "en": "Simplify the expression: {expression}"
            },
            "triangle_solve": {
                "ru": "В треугольнике ABC известно: {given}. Найдите {find}.",
                "en": "In triangle ABC, given: {given}. Find {find}."
            },
            "inverse": {
                "ru": "Вычислите {func}({value}).",
                "en": "Calculate {func}({value})."
            }
        },
        "steps": {
            "angle_conversion": {
                "ru": "Шаг {step}: Переводим угол: {angle_deg}° = {angle_rad} рад",
                "en": "Step {step}: Convert angle: {angle_deg}° = {angle_rad} rad"
            },
            "basic_value_result": {
                "ru": "Шаг {step}: {func}({angle}) = {result}",
                "en": "Step {step}: {func}({angle}) = {result}"
            },
            "identity_apply": {
                "ru": "Шаг {step}: Применяем тождество: {identity}",
                "en": "Step {step}: Apply identity: {identity}"
            },
            "equation_transform": {
                "ru": "Шаг {step}: Преобразуем уравнение: {transformed}",
                "en": "Step {step}: Transform equation: {transformed}"
            },
            "equation_solutions": {
                "ru": "Шаг {step}: Решения: x = {solutions}",
                "en": "Step {step}: Solutions: x = {solutions}"
            },
            "law_of_cosines": {
                "ru": "Шаг {step}: По теореме косинусов: c² = a² + b² - 2ab·cos(C)",
                "en": "Step {step}: By the law of cosines: c² = a² + b² - 2ab·cos(C)"
            },
            "law_of_sines": {
                "ru": "Шаг {step}: По теореме синусов: a/sin(A) = b/sin(B) = c/sin(C)",
                "en": "Step {step}: By the law of sines: a/sin(A) = b/sin(B) = c/sin(C)"
            }
        },
        "identities": {
            "ru": {
                "pythagorean": "sin²(x) + cos²(x) = 1",
                "double_angle_sin": "sin(2x) = 2sin(x)cos(x)",
                "double_angle_cos": "cos(2x) = cos²(x) - sin²(x)",
                "sum_sin": "sin(a+b) = sin(a)cos(b) + cos(a)sin(b)",
                "sum_cos": "cos(a+b) = cos(a)cos(b) - sin(a)sin(b)"
            },
            "en": {
                "pythagorean": "sin²(x) + cos²(x) = 1",
                "double_angle_sin": "sin(2x) = 2sin(x)cos(x)",
                "double_angle_cos": "cos(2x) = cos²(x) - sin²(x)",
                "sum_sin": "sin(a+b) = sin(a)cos(b) + cos(a)sin(b)",
                "sum_cos": "cos(a+b) = cos(a)cos(b) - sin(a)sin(b)"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 23) INEQUALITY - Неравенства
    #----------------------------------------------------------------------------
    "inequality": {
        "misc": {
            "system_first_ineq": {
                "ru": "Шаг 1: Из первого неравенства: x {sign} {value}",
                "en": "Step 1: From first inequality: x {sign} {value}"
            },
            "system_second_ineq": {
                "ru": "Шаг 2: Из второго неравенства: x {sign} {value}",
                "en": "Step 2: From second inequality: x {sign} {value}"
            }
        },
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите неравенство.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Множество решений в интервальной записи)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the inequality.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Solution set in interval notation)\n"
                "  </answer>"
            )
        },
        "problem": {
            "linear": {
                "ru": "Решите неравенство: {a}x + {b} {sign} {c}",
                "en": "Solve the inequality: {a}x + {b} {sign} {c}"
            },
            "quadratic": {
                "ru": "Решите неравенство: {a}x² + {b}x + {c} {sign} 0",
                "en": "Solve the inequality: {a}x² + {b}x + {c} {sign} 0"
            },
            "rational": {
                "ru": "Решите неравенство: ({numerator}) / ({denominator}) {sign} 0",
                "en": "Solve the inequality: ({numerator}) / ({denominator}) {sign} 0"
            },
            "absolute": {
                "ru": "Решите неравенство: |{expression}| {sign} {value}",
                "en": "Solve the inequality: |{expression}| {sign} {value}"
            },
            "system": {
                "ru": "Решите систему неравенств:\n{inequalities}",
                "en": "Solve the system of inequalities:\n{inequalities}"
            }
        },
        "steps": {
            "linear_solve": {
                "ru": "Шаг {step}: {a}x {sign} {c} - {b} = {rhs}",
                "en": "Step {step}: {a}x {sign} {c} - {b} = {rhs}"
            },
            "divide_positive": {
                "ru": "Шаг {step}: Делим на {a} (положительное число), знак сохраняется: x {sign} {result}",
                "en": "Step {step}: Divide by {a} (positive), sign preserved: x {sign} {result}"
            },
            "divide_negative": {
                "ru": "Шаг {step}: Делим на {a} (отрицательное число), знак меняется: x {new_sign} {result}",
                "en": "Step {step}: Divide by {a} (negative), sign flips: x {new_sign} {result}"
            },
            "quadratic_roots": {
                "ru": "Шаг {step}: Корни уравнения: x₁ = {x1}, x₂ = {x2}",
                "en": "Step {step}: Roots of equation: x₁ = {x1}, x₂ = {x2}"
            },
            "sign_analysis": {
                "ru": "Шаг {step}: Анализ знаков на интервалах: {intervals}",
                "en": "Step {step}: Sign analysis on intervals: {intervals}"
            },
            "critical_points": {
                "ru": "Шаг {step}: Критические точки: {points}",
                "en": "Step {step}: Critical points: {points}"
            },
            "absolute_split": {
                "ru": "Шаг {step}: Разбиваем на случаи: {expression} ≥ 0 и {expression} < 0",
                "en": "Step {step}: Split into cases: {expression} ≥ 0 and {expression} < 0"
            },
            "system_intersection": {
                "ru": "Шаг {step}: Пересечение решений: {intersection}",
                "en": "Step {step}: Intersection of solutions: {intersection}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 24) COMPLEX_NUMBER - Комплексные числа
    #----------------------------------------------------------------------------
    "complex_number": {
        "misc": {
            "conjugate_step": {
                "ru": "Шаг 1: Сопряжённое к {z} есть {conjugate}",
                "en": "Step 1: Conjugate of {z} is {conjugate}"
            },
            "discriminant_step": {
                "ru": "Шаг 1: Дискриминант D = {a}² - 4×{b} = {discriminant}",
                "en": "Step 1: Discriminant D = {a}² - 4×{b} = {discriminant}"
            },
            "roots_step": {
                "ru": "Шаг 2: Корни уравнения: {roots}",
                "en": "Step 2: Roots: {roots}"
            }
        },
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу с комплексными числами.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ в алгебраической или тригонометрической форме)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the complex numbers problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer in algebraic or polar form)\n"
                "  </answer>"
            )
        },
        "problem": {
            "arithmetic": {
                "ru": "Вычислите: ({a1} + {b1}i) {op} ({a2} + {b2}i)",
                "en": "Calculate: ({a1} + {b1}i) {op} ({a2} + {b2}i)"
            },
            "modulus": {
                "ru": "Найдите модуль комплексного числа z = {a} + {b}i.",
                "en": "Find the modulus of the complex number z = {a} + {b}i."
            },
            "argument": {
                "ru": "Найдите аргумент комплексного числа z = {a} + {b}i.",
                "en": "Find the argument of the complex number z = {a} + {b}i."
            },
            "polar_form": {
                "ru": "Запишите комплексное число z = {a} + {b}i в тригонометрической форме.",
                "en": "Write the complex number z = {a} + {b}i in polar form."
            },
            "power": {
                "ru": "Вычислите ({a} + {b}i)^{n} с помощью формулы Муавра.",
                "en": "Calculate ({a} + {b}i)^{n} using De Moivre's formula."
            },
            "roots": {
                "ru": "Найдите все корни {n}-й степени из комплексного числа z = {a} + {b}i.",
                "en": "Find all {n}th roots of the complex number z = {a} + {b}i."
            },
            "conjugate": {
                "ru": "Найдите сопряжённое к комплексному числу z = {a} + {b}i.",
                "en": "Find the conjugate of the complex number z = {a} + {b}i."
            },
            "equation": {
                "ru": "Решите уравнение: {equation}",
                "en": "Solve the equation: {equation}"
            }
        },
        "steps": {
            "add": {
                "ru": "Шаг {step}: ({a1}+{b1}i) + ({a2}+{b2}i) = ({a1}+{a2}) + ({b1}+{b2})i = {result}",
                "en": "Step {step}: ({a1}+{b1}i) + ({a2}+{b2}i) = ({a1}+{a2}) + ({b1}+{b2})i = {result}"
            },
            "subtract": {
                "ru": "Шаг {step}: ({a1}+{b1}i) - ({a2}+{b2}i) = ({a1}-{a2}) + ({b1}-{b2})i = {result}",
                "en": "Step {step}: ({a1}+{b1}i) - ({a2}+{b2}i) = ({a1}-{a2}) + ({b1}-{b2})i = {result}"
            },
            "multiply": {
                "ru": "Шаг {step}: ({a1}+{b1}i)×({a2}+{b2}i) = {a1}×{a2} + {a1}×{b2}i + {b1}i×{a2} + {b1}×{b2}×i² = {result}",
                "en": "Step {step}: ({a1}+{b1}i)×({a2}+{b2}i) = {a1}×{a2} + {a1}×{b2}i + {b1}i×{a2} + {b1}×{b2}×i² = {result}"
            },
            "divide": {
                "ru": "Шаг {step}: Умножаем на сопряжённое: ({a1}+{b1}i)/({a2}+{b2}i) × ({a2}-{b2}i)/({a2}-{b2}i) = {result}",
                "en": "Step {step}: Multiply by conjugate: ({a1}+{b1}i)/({a2}+{b2}i) × ({a2}-{b2}i)/({a2}-{b2}i) = {result}"
            },
            "modulus_formula": {
                "ru": "Шаг {step}: |z| = √(a² + b²) = √({a}² + {b}²) = {result}",
                "en": "Step {step}: |z| = √(a² + b²) = √({a}² + {b}²) = {result}"
            },
            "argument_formula": {
                "ru": "Шаг {step}: arg(z) = arctan(b/a) = arctan({b}/{a}) = {result}",
                "en": "Step {step}: arg(z) = arctan(b/a) = arctan({b}/{a}) = {result}"
            },
            "polar_form_result": {
                "ru": "Шаг {step}: z = |z|(cos(φ) + i·sin(φ)) = {r}(cos({phi}) + i·sin({phi}))",
                "en": "Step {step}: z = |z|(cos(φ) + i·sin(φ)) = {r}(cos({phi}) + i·sin({phi}))"
            },
            "de_moivre": {
                "ru": "Шаг {step}: По формуле Муавра: z^n = r^n(cos(nφ) + i·sin(nφ)) = {result}",
                "en": "Step {step}: By De Moivre's formula: z^n = r^n(cos(nφ) + i·sin(nφ)) = {result}"
            },
            "root_formula": {
                "ru": "Шаг {step}: w_k = ⁿ√r(cos((φ+2πk)/n) + i·sin((φ+2πk)/n)), k = 0, 1, ..., {n}-1",
                "en": "Step {step}: w_k = ⁿ√r(cos((φ+2πk)/n) + i·sin((φ+2πk)/n)), k = 0, 1, ..., {n}-1"
            },
            "root_k": {
                "ru": "Шаг {step}: w_{k} = {result}",
                "en": "Step {step}: w_{k} = {result}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 25) LIMITS - Пределы
    #----------------------------------------------------------------------------
    "limits": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Найдите предел.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое вычисление предела)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Значение предела или ±∞)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Find the limit.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step calculation of the limit)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Value of the limit or ±∞)\n"
                "  </answer>"
            )
        },
        "problem": {
            "polynomial": {
                "ru": "Найдите предел: lim(x→{point}) ({expression})",
                "en": "Find the limit: lim(x→{point}) ({expression})"
            },
            "rational": {
                "ru": "Найдите предел: lim(x→{point}) (({numerator})/({denominator}))",
                "en": "Find the limit: lim(x→{point}) (({numerator})/({denominator}))"
            },
            "infinity": {
                "ru": "Найдите предел: lim(x→∞) ({expression})",
                "en": "Find the limit: lim(x→∞) ({expression})"
            },
            "indeterminate": {
                "ru": "Найдите предел: lim(x→{point}) ({expression}). Указание: имеется неопределённость {type}.",
                "en": "Find the limit: lim(x→{point}) ({expression}). Hint: this is an indeterminate form {type}."
            },
            "sequence": {
                "ru": "Найдите предел последовательности: lim(n→∞) {expression}",
                "en": "Find the limit of the sequence: lim(n→∞) {expression}"
            },
            "special": {
                "ru": "Найдите предел, используя замечательный предел: lim(x→{point}) ({expression})",
                "en": "Find the limit using a remarkable limit: lim(x→{point}) ({expression})"
            }
        },
        "steps": {
            "direct_substitution": {
                "ru": "Шаг {step}: Подставляем x = {point}: {expression} = {result}",
                "en": "Step {step}: Direct substitution x = {point}: {expression} = {result}"
            },
            "indeterminate_found": {
                "ru": "Шаг {step}: Получили неопределённость {type}",
                "en": "Step {step}: Found indeterminate form {type}"
            },
            "factorize": {
                "ru": "Шаг {step}: Раскладываем на множители: {factorization}",
                "en": "Step {step}: Factor: {factorization}"
            },
            "simplify": {
                "ru": "Шаг {step}: Сокращаем: {simplified}",
                "en": "Step {step}: Simplify: {simplified}"
            },
            "lhopital": {
                "ru": "Шаг {step}: Применяем правило Лопиталя: lim = lim(f'(x)/g'(x)) = lim({derivative})",
                "en": "Step {step}: Apply L'Hôpital's rule: lim = lim(f'(x)/g'(x)) = lim({derivative})"
            },
            "multiply_conjugate": {
                "ru": "Шаг {step}: Умножаем на сопряжённое: {expression}",
                "en": "Step {step}: Multiply by conjugate: {expression}"
            },
            "divide_highest_power": {
                "ru": "Шаг {step}: Делим на старшую степень x^{power}: {expression}",
                "en": "Step {step}: Divide by highest power x^{power}: {expression}"
            },
            "remarkable_limit": {
                "ru": "Шаг {step}: Используем замечательный предел: {limit_formula}",
                "en": "Step {step}: Use remarkable limit: {limit_formula}"
            },
            "squeeze_theorem": {
                "ru": "Шаг {step}: По теореме о сжатии: {lower} ≤ {expression} ≤ {upper}",
                "en": "Step {step}: By squeeze theorem: {lower} ≤ {expression} ≤ {upper}"
            }
        },
        "remarkable_limits": {
            "ru": {
                "sin_x_over_x": "lim(x→0) sin(x)/x = 1",
                "one_plus_one_over_x": "lim(x→∞) (1 + 1/x)^x = e",
                "ln_one_plus_x": "lim(x→0) ln(1+x)/x = 1",
                "e_x_minus_one": "lim(x→0) (e^x - 1)/x = 1"
            },
            "en": {
                "sin_x_over_x": "lim(x→0) sin(x)/x = 1",
                "one_plus_one_over_x": "lim(x→∞) (1 + 1/x)^x = e",
                "ln_one_plus_x": "lim(x→0) ln(1+x)/x = 1",
                "e_x_minus_one": "lim(x→0) (e^x - 1)/x = 1"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 26) SET_LOGIC - Множества и логика
    #----------------------------------------------------------------------------
    "set_logic": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по множествам и логике.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the sets and logic problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "union": {
                "ru": "Найдите A ∪ B, где A = {set_a} и B = {set_b}.",
                "en": "Find A ∪ B, where A = {set_a} and B = {set_b}."
            },
            "intersection": {
                "ru": "Найдите A ∩ B, где A = {set_a} и B = {set_b}.",
                "en": "Find A ∩ B, where A = {set_a} and B = {set_b}."
            },
            "difference": {
                "ru": "Найдите A \\ B (разность), где A = {set_a} и B = {set_b}.",
                "en": "Find A \\ B (difference), where A = {set_a} and B = {set_b}."
            },
            "symmetric_difference": {
                "ru": "Найдите A △ B (симметрическую разность), где A = {set_a} и B = {set_b}.",
                "en": "Find A △ B (symmetric difference), where A = {set_a} and B = {set_b}."
            },
            "complement": {
                "ru": "Найдите дополнение Aᶜ, где A = {set_a} и универсальное множество U = {universal}.",
                "en": "Find the complement Aᶜ, where A = {set_a} and the universal set U = {universal}."
            },
            "cardinality": {
                "ru": "Найдите |A ∪ B|, если |A| = {card_a}, |B| = {card_b}, |A ∩ B| = {card_intersection}.",
                "en": "Find |A ∪ B|, given |A| = {card_a}, |B| = {card_b}, |A ∩ B| = {card_intersection}."
            },
            "power_set": {
                "ru": "Найдите мощность степени множества P(A), где |A| = {n}.",
                "en": "Find the cardinality of the power set P(A), where |A| = {n}."
            },
            "cartesian_product": {
                "ru": "Найдите A × B, где A = {set_a} и B = {set_b}.",
                "en": "Find A × B, where A = {set_a} and B = {set_b}."
            },
            "boolean_simplify": {
                "ru": "Упростите логическое выражение: {expression}",
                "en": "Simplify the boolean expression: {expression}"
            },
            "truth_table": {
                "ru": "Постройте таблицу истинности для выражения: {expression}",
                "en": "Construct a truth table for the expression: {expression}"
            },
            "venn_problem": {
                "ru": "В опросе участвовало {total} человек. {desc} Сколько человек {question}?",
                "en": "{total} people were surveyed. {desc} How many people {question}?"
            }
        },
        "steps": {
            "union_result": {
                "ru": "Шаг {step}: A ∪ B = {set_a} ∪ {set_b} = {result}",
                "en": "Step {step}: A ∪ B = {set_a} ∪ {set_b} = {result}"
            },
            "intersection_result": {
                "ru": "Шаг {step}: A ∩ B = {set_a} ∩ {set_b} = {result}",
                "en": "Step {step}: A ∩ B = {set_a} ∩ {set_b} = {result}"
            },
            "difference_result": {
                "ru": "Шаг {step}: A \\ B = {result}",
                "en": "Step {step}: A \\ B = {result}"
            },
            "symmetric_diff_result": {
                "ru": "Шаг {step}: A △ B = (A \\ B) ∪ (B \\ A) = {result}",
                "en": "Step {step}: A △ B = (A \\ B) ∪ (B \\ A) = {result}"
            },
            "complement_result": {
                "ru": "Шаг {step}: Aᶜ = U \\ A = {result}",
                "en": "Step {step}: Aᶜ = U \\ A = {result}"
            },
            "cardinality_formula": {
                "ru": "Шаг {step}: |A ∪ B| = |A| + |B| - |A ∩ B| = {card_a} + {card_b} - {card_intersection} = {result}",
                "en": "Step {step}: |A ∪ B| = |A| + |B| - |A ∩ B| = {card_a} + {card_b} - {card_intersection} = {result}"
            },
            "power_set_formula": {
                "ru": "Шаг {step}: |P(A)| = 2^|A| = 2^{n} = {result}",
                "en": "Step {step}: |P(A)| = 2^|A| = 2^{n} = {result}"
            },
            "cartesian_pairs": {
                "ru": "Шаг {step}: A × B = {result}",
                "en": "Step {step}: A × B = {result}"
            },
            "boolean_law": {
                "ru": "Шаг {step}: Применяем закон {law}: {result}",
                "en": "Step {step}: Apply {law} law: {result}"
            },
            "venn_calculate": {
                "ru": "Шаг {step}: {calculation}",
                "en": "Step {step}: {calculation}"
            }
        },
        "boolean_laws": {
            "ru": {
                "de_morgan_1": "¬(A ∧ B) = ¬A ∨ ¬B",
                "de_morgan_2": "¬(A ∨ B) = ¬A ∧ ¬B",
                "idempotent": "A ∧ A = A, A ∨ A = A",
                "absorption": "A ∧ (A ∨ B) = A, A ∨ (A ∧ B) = A",
                "distributive": "A ∧ (B ∨ C) = (A ∧ B) ∨ (A ∧ C)"
            },
            "en": {
                "de_morgan_1": "¬(A ∧ B) = ¬A ∨ ¬B",
                "de_morgan_2": "¬(A ∨ B) = ¬A ∧ ¬B",
                "idempotent": "A ∧ A = A, A ∨ A = A",
                "absorption": "A ∧ (A ∨ B) = A, A ∨ (A ∧ B) = A",
                "distributive": "A ∧ (B ∨ C) = (A ∧ B) ∨ (A ∧ C)"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 27) GROUP_THEORY - Теория групп
    #----------------------------------------------------------------------------
    "group_theory": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по теории групп.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the group theory problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "inverse_element": {
                "ru": "Найдите обратный элемент для элемента {element} в {group_desc}.",
                "en": "Find the inverse element for {element} in {group_desc}."
            },
            "element_order": {
                "ru": "Определите порядок элемента {element} в {group_desc}.",
                "en": "Determine the order of element {element} in {group_desc}."
            },
            "is_abelian": {
                "ru": "Является ли {group_desc} абелевой группой? Обоснуйте свой ответ.",
                "en": "Is the group {group_desc} abelian? Justify your answer."
            },
            "group_order": {
                "ru": "Какой порядок у группы {group_desc}?",
                "en": "What is the order of the group {group_desc}?"
            }
        },
        "group_names": {
            "multiplicative_cyclic": {
                "ru": "мультипликативной группе по модулю {n}",
                "en": "multiplicative group modulo {n}"
            },
            "additive_cyclic": {
                "ru": "аддитивной группе по модулю {n}",
                "en": "additive group modulo {n}"
            },
            "symmetric": {
                "ru": "симметрической группе S_{n}",
                "en": "symmetric group S_{n}"
            }
        },
        "steps": {
            "gcd_check": {
                "ru": "Шаг 1: Находим НОД({a}, {b}) = {gcd}",
                "en": "Step 1: Find GCD({a}, {b}) = {gcd}"
            },
            "extended_euclidean": {
                "ru": "Шаг 2: Применяем расширенный алгоритм Евклида для нахождения обратного элемента: {inverse}",
                "en": "Step 2: Apply extended Euclidean algorithm to find inverse: {inverse}"
            },
            "inverse_permutation": {
                "ru": "Шаг 1: Находим обратную перестановку для {element}",
                "en": "Step 1: Find inverse permutation for {element}"
            },
            "verify_composition": {
                "ru": "Шаг 2: Проверяем композицию: {element} ∘ {inverse} = {result}",
                "en": "Step 2: Verify composition: {element} ∘ {inverse} = {result}"
            },
            "cycle_structure": {
                "ru": "Шаг 1: Цикловая структура: {structure}",
                "en": "Step 1: Cycle structure: {structure}"
            },
            "lcm_cycles": {
                "ru": "Шаг 2: Вычисляем НОК длин циклов: {order}",
                "en": "Step 2: Compute LCM of cycle lengths: {order}"
            },
            "order_computed": {
                "ru": "Порядок элемента вычислен через свойства циклической группы: {order}",
                "en": "Element order computed via cyclic group properties: {order}"
            },
            "property_check": {
                "ru": "Свойство: {property}",
                "en": "Property: {property}"
            },
            "answer_with_reason": {
                "ru": "Ответ: {answer}\nОбоснование: {reason}",
                "en": "Answer: {answer}\nJustification: {reason}"
            }
        },
        "reasons": {
            "cyclic_abelian": {
                "ru": "Все циклические группы являются абелевыми.",
                "en": "All cyclic groups are abelian."
            },
            "symmetric_not_abelian": {
                "ru": "Симметрическая группа S_n является абелевой только при n ≤ 2.",
                "en": "Symmetric group S_n is abelian only when n ≤ 2."
            },
            "additive_order": {
                "ru": "Порядок аддитивной группы по модулю n равен n.",
                "en": "Order of additive group modulo n equals n."
            },
            "multiplicative_order": {
                "ru": "Порядок мультипликативной группы по модулю n равен φ(n).",
                "en": "Order of multiplicative group modulo n equals φ(n)."
            },
            "symmetric_order": {
                "ru": "Порядок симметрической группы S_n равен n! = {factorial}.",
                "en": "Order of symmetric group S_n equals n! = {factorial}."
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 28) CATEGORY_THEORY - Теория категорий
    #----------------------------------------------------------------------------
    "category_theory": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по теории категорий.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the category theory problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "morphism_composition": {
                "ru": "Даны морфизмы:\n{morphisms}\n\nНайдите композицию h ∘ g ∘ f.",
                "en": "Given the morphisms:\n{morphisms}\n\nFind the composition h ∘ g ∘ f."
            },
            "commutative_diagram": {
                "ru": "Дана диаграмма морфизмов:\n{morphisms}\n\nКоммутирует ли эта диаграмма (т.е. верно ли, что h ∘ f = k ∘ g)?",
                "en": "Given the diagram of morphisms:\n{morphisms}\n\nDoes this diagram commute (i.e., is it true that h ∘ f = k ∘ g)?"
            }
        },
        "steps": {
            "identify_domains": {
                "ru": "Шаг 1: Определяем область и кообласть каждого морфизма.",
                "en": "Step 1: Identify the domain and codomain of each morphism."
            },
            "morphism_list": {
                "ru": "f: A → B, g: B → C, h: C → D",
                "en": "f: A → B, g: B → C, h: C → D"
            },
            "apply_morphisms": {
                "ru": "Шаг 2: Применяем морфизмы последовательно, начиная справа.",
                "en": "Step 2: Apply morphisms sequentially, starting from the right."
            },
            "composition_result": {
                "ru": "Композиция (h ∘ g ∘ f) отображает область первого морфизма (f) в кообласть последнего (h).",
                "en": "The composition (h ∘ g ∘ f) maps the domain of the first morphism (f) to the codomain of the last (h)."
            },
            "check_paths": {
                "ru": "Проверяем равенство двух путей из A в D.",
                "en": "Check equality of two paths from A to D."
            },
            "two_paths": {
                "ru": "Путь 1: h ∘ f. Путь 2: k ∘ g.",
                "en": "Path 1: h ∘ f. Path 2: k ∘ g."
            },
            "commutes": {
                "ru": "Диаграмма коммутирует, так как h ∘ f = k ∘ g.",
                "en": "The diagram commutes since h ∘ f = k ∘ g."
            },
            "not_commutes": {
                "ru": "Диаграмма не коммутирует, так как h ∘ f ≠ k ∘ g.",
                "en": "The diagram does not commute since h ∘ f ≠ k ∘ g."
            }
        },
        "final_answer": {
            "ru": "Результат: {answer}",
            "en": "Result: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 29) PROBABILITY_ADVANCED - Расширенная вероятность
    #----------------------------------------------------------------------------
    "probability_advanced": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по теории вероятностей.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение с формулами)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Числовой ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the probability problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution with formulas)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Numerical answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "bayes": {
                "ru": "По условию задачи:\n{conditions}\nИспользуя формулу Байеса, найдите P({event}|{given}).",
                "en": "Given:\n{conditions}\nUsing Bayes' theorem, find P({event}|{given})."
            },
            "conditional": {
                "ru": "Если P(A) = {pa}, P(B) = {pb}, P(A ∩ B) = {pab}, найдите P(A|B).",
                "en": "If P(A) = {pa}, P(B) = {pb}, P(A ∩ B) = {pab}, find P(A|B)."
            },
            "expected_value": {
                "ru": "Случайная величина X имеет распределение:\n{distribution}\nНайдите математическое ожидание E(X).",
                "en": "Random variable X has the distribution:\n{distribution}\nFind the expected value E(X)."
            },
            "variance": {
                "ru": "Случайная величина X имеет распределение:\n{distribution}\nНайдите дисперсию Var(X).",
                "en": "Random variable X has the distribution:\n{distribution}\nFind the variance Var(X)."
            },
            "binomial": {
                "ru": "Монета подбрасывается {n} раз. Вероятность выпадения орла = {p}. Какова вероятность получить ровно {k} орлов?",
                "en": "A coin is flipped {n} times. Probability of heads = {p}. What is the probability of getting exactly {k} heads?"
            },
            "geometric": {
                "ru": "Вероятность успеха в одном испытании = {p}. Найдите вероятность того, что первый успех произойдёт на {k}-м испытании.",
                "en": "Probability of success in one trial = {p}. Find the probability that the first success occurs on the {k}th trial."
            },
            "poisson": {
                "ru": "Число событий подчиняется распределению Пуассона с λ = {lambda_}. Найдите P(X = {k}).",
                "en": "Number of events follows Poisson distribution with λ = {lambda_}. Find P(X = {k})."
            }
        },
        "steps": {
            "bayes_formula": {
                "ru": "Шаг {step}: По формуле Байеса: P(A|B) = P(B|A)P(A) / P(B)",
                "en": "Step {step}: By Bayes' theorem: P(A|B) = P(B|A)P(A) / P(B)"
            },
            "total_probability": {
                "ru": "Шаг {step}: По формуле полной вероятности: P(B) = ΣP(B|Aᵢ)P(Aᵢ) = {result}",
                "en": "Step {step}: By total probability formula: P(B) = ΣP(B|Aᵢ)P(Aᵢ) = {result}"
            },
            "conditional_formula": {
                "ru": "Шаг {step}: P(A|B) = P(A ∩ B) / P(B) = {pab} / {pb} = {result}",
                "en": "Step {step}: P(A|B) = P(A ∩ B) / P(B) = {pab} / {pb} = {result}"
            },
            "expected_value_formula": {
                "ru": "Шаг {step}: E(X) = Σxᵢ·P(X=xᵢ) = {calculation} = {result}",
                "en": "Step {step}: E(X) = Σxᵢ·P(X=xᵢ) = {calculation} = {result}"
            },
            "variance_formula": {
                "ru": "Шаг {step}: Var(X) = E(X²) - [E(X)]² = {ex2} - {ex}² = {result}",
                "en": "Step {step}: Var(X) = E(X²) - [E(X)]² = {ex2} - {ex}² = {result}"
            },
            "binomial_formula": {
                "ru": "Шаг {step}: P(X={k}) = C({n},{k}) × {p}^{k} × (1-{p})^({n}-{k}) = {result}",
                "en": "Step {step}: P(X={k}) = C({n},{k}) × {p}^{k} × (1-{p})^({n}-{k}) = {result}"
            },
            "geometric_formula": {
                "ru": "Шаг {step}: P(X={k}) = (1-{p})^({k}-1) × {p} = {result}",
                "en": "Step {step}: P(X={k}) = (1-{p})^({k}-1) × {p} = {result}"
            },
            "poisson_formula": {
                "ru": "Шаг {step}: P(X={k}) = (λ^{k} × e^(-λ)) / {k}! = ({lambda_}^{k} × e^(-{lambda_})) / {k}! = {result}",
                "en": "Step {step}: P(X={k}) = (λ^{k} × e^(-λ)) / {k}! = ({lambda_}^{k} × e^(-{lambda_})) / {k}! = {result}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 30) STATISTICS - Статистика
    #----------------------------------------------------------------------------
    "statistics": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по статистике.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the statistics problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "mean": {
                "ru": "Найдите среднее арифметическое для набора данных: {data}",
                "en": "Find the arithmetic mean of the data set: {data}"
            },
            "median": {
                "ru": "Найдите медиану для набора данных: {data}",
                "en": "Find the median of the data set: {data}"
            },
            "mode": {
                "ru": "Найдите моду для набора данных: {data}",
                "en": "Find the mode of the data set: {data}"
            },
            "variance": {
                "ru": "Найдите дисперсию для набора данных: {data}",
                "en": "Find the variance of the data set: {data}"
            },
            "std_deviation": {
                "ru": "Найдите стандартное отклонение для набора данных: {data}",
                "en": "Find the standard deviation of the data set: {data}"
            },
            "correlation": {
                "ru": "Найдите коэффициент корреляции Пирсона между X = {x_data} и Y = {y_data}",
                "en": "Find Pearson correlation coefficient between X = {x_data} and Y = {y_data}"
            },
            "linear_regression": {
                "ru": "Найдите уравнение линейной регрессии для X = {x_data} и Y = {y_data}",
                "en": "Find the linear regression equation for X = {x_data} and Y = {y_data}"
            },
            "percentile": {
                "ru": "Найдите {p}-й перцентиль для набора данных: {data}",
                "en": "Find the {p}th percentile of the data set: {data}"
            },
            "quartiles": {
                "ru": "Найдите квартили (Q1, Q2, Q3) для набора данных: {data}",
                "en": "Find the quartiles (Q1, Q2, Q3) of the data set: {data}"
            },
            "z_score": {
                "ru": "Найдите z-оценку для значения {x} при среднем {mean} и стандартном отклонении {std}",
                "en": "Find the z-score for value {x} given mean {mean} and standard deviation {std}"
            }
        },
        "steps": {
            "sum_values": {
                "ru": "Шаг 1: Сумма значений: {values} = {sum}",
                "en": "Step 1: Sum of values: {values} = {sum}"
            },
            "count_values": {
                "ru": "Шаг 2: Количество значений: n = {n}",
                "en": "Step 2: Number of values: n = {n}"
            },
            "mean_formula": {
                "ru": "Шаг 3: Среднее = Σx / n = {sum} / {n} = {mean}",
                "en": "Step 3: Mean = Σx / n = {sum} / {n} = {mean}"
            },
            "sort_data": {
                "ru": "Шаг 1: Сортируем данные: {sorted_data}",
                "en": "Step 1: Sort data: {sorted_data}"
            },
            "median_odd": {
                "ru": "Шаг 2: n = {n} (нечётное), медиана = элемент [{pos}] = {median}",
                "en": "Step 2: n = {n} (odd), median = element [{pos}] = {median}"
            },
            "median_even": {
                "ru": "Шаг 2: n = {n} (чётное), медиана = ({a} + {b}) / 2 = {median}",
                "en": "Step 2: n = {n} (even), median = ({a} + {b}) / 2 = {median}"
            },
            "mode_count": {
                "ru": "Шаг 1: Подсчёт частот: {freq}",
                "en": "Step 1: Frequency count: {freq}"
            },
            "mode_result": {
                "ru": "Шаг 2: Мода (наиболее частое значение): {mode}",
                "en": "Step 2: Mode (most frequent value): {mode}"
            },
            "variance_deviations": {
                "ru": "Шаг 1: Отклонения от среднего: {deviations}",
                "en": "Step 1: Deviations from mean: {deviations}"
            },
            "variance_squared": {
                "ru": "Шаг 2: Квадраты отклонений: {squared}",
                "en": "Step 2: Squared deviations: {squared}"
            },
            "variance_formula": {
                "ru": "Шаг 3: Дисперсия = Σ(x-μ)² / n = {sum_sq} / {n} = {variance}",
                "en": "Step 3: Variance = Σ(x-μ)² / n = {sum_sq} / {n} = {variance}"
            },
            "std_formula": {
                "ru": "Шаг 4: Стандартное отклонение = √{variance} = {std}",
                "en": "Step 4: Standard deviation = √{variance} = {std}"
            },
            "correlation_formula": {
                "ru": "Шаг {step}: r = Σ(x-x̄)(y-ȳ) / √[Σ(x-x̄)²·Σ(y-ȳ)²] = {r}",
                "en": "Step {step}: r = Σ(x-x̄)(y-ȳ) / √[Σ(x-x̄)²·Σ(y-ȳ)²] = {r}"
            },
            "regression_slope": {
                "ru": "Шаг {step}: Наклон b = Σ(x-x̄)(y-ȳ) / Σ(x-x̄)² = {b}",
                "en": "Step {step}: Slope b = Σ(x-x̄)(y-ȳ) / Σ(x-x̄)² = {b}"
            },
            "regression_intercept": {
                "ru": "Шаг {step}: Свободный член a = ȳ - b·x̄ = {a}",
                "en": "Step {step}: Intercept a = ȳ - b·x̄ = {a}"
            },
            "z_score_formula": {
                "ru": "Шаг 1: z = (x - μ) / σ = ({x} - {mean}) / {std} = {z}",
                "en": "Step 1: z = (x - μ) / σ = ({x} - {mean}) / {std} = {z}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 31) INTEGRAL - Интегралы
    #----------------------------------------------------------------------------
    "integral": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Вычислите интеграл.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Compute the integral.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "indefinite_polynomial": {
                "ru": "Вычислите неопределённый интеграл: ∫({expression}) dx",
                "en": "Compute the indefinite integral: ∫({expression}) dx"
            },
            "definite_polynomial": {
                "ru": "Вычислите определённый интеграл: ∫[{a},{b}] ({expression}) dx",
                "en": "Compute the definite integral: ∫[{a},{b}] ({expression}) dx"
            },
            "indefinite_trig": {
                "ru": "Вычислите неопределённый интеграл: ∫{expression} dx",
                "en": "Compute the indefinite integral: ∫{expression} dx"
            },
            "definite_trig": {
                "ru": "Вычислите определённый интеграл: ∫[{a},{b}] {expression} dx",
                "en": "Compute the definite integral: ∫[{a},{b}] {expression} dx"
            },
            "by_parts": {
                "ru": "Вычислите интеграл методом интегрирования по частям: ∫{expression} dx",
                "en": "Compute the integral using integration by parts: ∫{expression} dx"
            },
            "substitution": {
                "ru": "Вычислите интеграл методом замены: ∫{expression} dx",
                "en": "Compute the integral using substitution: ∫{expression} dx"
            },
            "area": {
                "ru": "Найдите площадь под кривой y = {expression} на отрезке [{a}, {b}]",
                "en": "Find the area under the curve y = {expression} on the interval [{a}, {b}]"
            }
        },
        "steps": {
            "power_rule": {
                "ru": "Шаг {step}: ∫x^n dx = x^(n+1)/(n+1) + C",
                "en": "Step {step}: ∫x^n dx = x^(n+1)/(n+1) + C"
            },
            "apply_power": {
                "ru": "Шаг {step}: ∫{coef}x^{n} dx = {coef}·x^{new_n}/{new_n} = {result}",
                "en": "Step {step}: ∫{coef}x^{n} dx = {coef}·x^{new_n}/{new_n} = {result}"
            },
            "constant_rule": {
                "ru": "Шаг {step}: ∫{c} dx = {c}x",
                "en": "Step {step}: ∫{c} dx = {c}x"
            },
            "combine_terms": {
                "ru": "Шаг {step}: Объединяем: {result} + C",
                "en": "Step {step}: Combine: {result} + C"
            },
            "evaluate_definite": {
                "ru": "Шаг {step}: F({b}) - F({a}) = {fb} - {fa} = {result}",
                "en": "Step {step}: F({b}) - F({a}) = {fb} - {fa} = {result}"
            },
            "trig_integral": {
                "ru": "Шаг {step}: ∫{func} dx = {result}",
                "en": "Step {step}: ∫{func} dx = {result}"
            },
            "by_parts_formula": {
                "ru": "Шаг {step}: ∫u dv = uv - ∫v du, где u = {u}, dv = {dv}",
                "en": "Step {step}: ∫u dv = uv - ∫v du, where u = {u}, dv = {dv}"
            },
            "substitution_let": {
                "ru": "Шаг {step}: Пусть u = {u}, тогда du = {du}",
                "en": "Step {step}: Let u = {u}, then du = {du}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 32) DIFFERENTIAL_EQUATION - Дифференциальные уравнения
    #----------------------------------------------------------------------------
    "differential_equation": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите дифференциальное уравнение.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Общее или частное решение)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the differential equation.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (General or particular solution)\n"
                "  </answer>"
            )
        },
        "problem": {
            "separable": {
                "ru": "Решите дифференциальное уравнение с разделяющимися переменными: {equation}",
                "en": "Solve the separable differential equation: {equation}"
            },
            "linear_first_order": {
                "ru": "Решите линейное ДУ первого порядка: {equation}",
                "en": "Solve the first-order linear ODE: {equation}"
            },
            "homogeneous_second_order": {
                "ru": "Решите однородное ДУ второго порядка: {equation}",
                "en": "Solve the second-order homogeneous ODE: {equation}"
            },
            "cauchy_problem": {
                "ru": "Решите задачу Коши: {equation} при {conditions}",
                "en": "Solve the Cauchy problem: {equation} with {conditions}"
            },
            "exponential_growth": {
                "ru": "Решите уравнение экспоненциального роста: dy/dx = {k}y",
                "en": "Solve the exponential growth equation: dy/dx = {k}y"
            }
        },
        "steps": {
            "separate_variables": {
                "ru": "Шаг 1: Разделяем переменные: {separated}",
                "en": "Step 1: Separate variables: {separated}"
            },
            "integrate_both": {
                "ru": "Шаг 2: Интегрируем обе части: ∫{left} = ∫{right}",
                "en": "Step 2: Integrate both sides: ∫{left} = ∫{right}"
            },
            "general_solution": {
                "ru": "Шаг {step}: Общее решение: {solution}",
                "en": "Step {step}: General solution: {solution}"
            },
            "characteristic_equation": {
                "ru": "Шаг 1: Характеристическое уравнение: {char_eq}",
                "en": "Step 1: Characteristic equation: {char_eq}"
            },
            "find_roots": {
                "ru": "Шаг 2: Корни: {roots}",
                "en": "Step 2: Roots: {roots}"
            },
            "apply_initial": {
                "ru": "Шаг {step}: Применяем начальные условия: {conditions}",
                "en": "Step {step}: Apply initial conditions: {conditions}"
            },
            "particular_solution": {
                "ru": "Шаг {step}: Частное решение: {solution}",
                "en": "Step {step}: Particular solution: {solution}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 33) OPTIMIZATION - Оптимизация
    #----------------------------------------------------------------------------
    "optimization": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу оптимизации.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Оптимальное значение)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the optimization problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Optimal value)\n"
                "  </answer>"
            )
        },
        "problem": {
            "find_extremum": {
                "ru": "Найдите экстремумы функции f(x) = {expression}",
                "en": "Find the extrema of the function f(x) = {expression}"
            },
            "max_min_interval": {
                "ru": "Найдите максимум и минимум функции f(x) = {expression} на отрезке [{a}, {b}]",
                "en": "Find the maximum and minimum of f(x) = {expression} on [{a}, {b}]"
            },
            "constrained": {
                "ru": "Найдите экстремум f(x,y) = {objective} при ограничении {constraint}",
                "en": "Find the extremum of f(x,y) = {objective} subject to {constraint}"
            },
            "linear_programming": {
                "ru": "Решите задачу линейного программирования:\nМаксимизировать: {objective}\nПри ограничениях:\n{constraints}",
                "en": "Solve the linear programming problem:\nMaximize: {objective}\nSubject to:\n{constraints}"
            },
            "word_problem": {
                "ru": "{problem_text}\nНайдите оптимальное решение.",
                "en": "{problem_text}\nFind the optimal solution."
            }
        },
        "steps": {
            "find_derivative": {
                "ru": "Шаг 1: Находим производную: f'(x) = {derivative}",
                "en": "Step 1: Find derivative: f'(x) = {derivative}"
            },
            "critical_points": {
                "ru": "Шаг 2: Критические точки (f'(x) = 0): {points}",
                "en": "Step 2: Critical points (f'(x) = 0): {points}"
            },
            "second_derivative": {
                "ru": "Шаг 3: Вторая производная: f''(x) = {second_deriv}",
                "en": "Step 3: Second derivative: f''(x) = {second_deriv}"
            },
            "classify_point": {
                "ru": "Шаг {step}: В точке x = {x}: f''({x}) = {value} → {type}",
                "en": "Step {step}: At x = {x}: f''({x}) = {value} → {type}"
            },
            "check_endpoints": {
                "ru": "Шаг {step}: Проверяем концы: f({a}) = {fa}, f({b}) = {fb}",
                "en": "Step {step}: Check endpoints: f({a}) = {fa}, f({b}) = {fb}"
            },
            "lagrange_setup": {
                "ru": "Шаг 1: Лагранжиан L = {lagrangian}",
                "en": "Step 1: Lagrangian L = {lagrangian}"
            },
            "lp_vertices": {
                "ru": "Шаг {step}: Вершины допустимой области: {vertices}",
                "en": "Step {step}: Vertices of feasible region: {vertices}"
            },
            "evaluate_objective": {
                "ru": "Шаг {step}: Значения целевой функции в вершинах: {values}",
                "en": "Step {step}: Objective function values at vertices: {values}"
            }
        },
        "types": {
            "maximum": {"ru": "максимум", "en": "maximum"},
            "minimum": {"ru": "минимум", "en": "minimum"},
            "saddle": {"ru": "точка перегиба", "en": "saddle point"}
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 34) VECTOR_3D - Векторы в 3D
    #----------------------------------------------------------------------------
    "vector_3d": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по векторной алгебре в 3D.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the 3D vector algebra problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "cross_product": {
                "ru": "Найдите векторное произведение a⃗ × b⃗, где a⃗ = {a} и b⃗ = {b}",
                "en": "Find the cross product a⃗ × b⃗, where a⃗ = {a} and b⃗ = {b}"
            },
            "triple_scalar": {
                "ru": "Найдите смешанное произведение (a⃗, b⃗, c⃗), где a⃗ = {a}, b⃗ = {b}, c⃗ = {c}",
                "en": "Find the scalar triple product (a⃗, b⃗, c⃗), where a⃗ = {a}, b⃗ = {b}, c⃗ = {c}"
            },
            "plane_equation": {
                "ru": "Найдите уравнение плоскости, проходящей через точки A{a}, B{b}, C{c}",
                "en": "Find the equation of the plane passing through points A{a}, B{b}, C{c}"
            },
            "line_equation_3d": {
                "ru": "Найдите параметрическое уравнение прямой через точки A{a} и B{b}",
                "en": "Find the parametric equation of the line through points A{a} and B{b}"
            },
            "distance_point_plane": {
                "ru": "Найдите расстояние от точки P{p} до плоскости {plane}",
                "en": "Find the distance from point P{p} to the plane {plane}"
            },
            "angle_vectors": {
                "ru": "Найдите угол между векторами a⃗ = {a} и b⃗ = {b}",
                "en": "Find the angle between vectors a⃗ = {a} and b⃗ = {b}"
            },
            "projection": {
                "ru": "Найдите проекцию вектора a⃗ = {a} на вектор b⃗ = {b}",
                "en": "Find the projection of vector a⃗ = {a} onto vector b⃗ = {b}"
            },
            "parallelpiped_volume": {
                "ru": "Найдите объём параллелепипеда, построенного на векторах a⃗ = {a}, b⃗ = {b}, c⃗ = {c}",
                "en": "Find the volume of the parallelepiped spanned by vectors a⃗ = {a}, b⃗ = {b}, c⃗ = {c}"
            }
        },
        "steps": {
            "cross_formula": {
                "ru": "Шаг 1: a⃗ × b⃗ = |i  j  k |\n              |{a1} {a2} {a3}|\n              |{b1} {b2} {b3}|",
                "en": "Step 1: a⃗ × b⃗ = |i  j  k |\n              |{a1} {a2} {a3}|\n              |{b1} {b2} {b3}|"
            },
            "cross_compute": {
                "ru": "Шаг 2: = ({a2}·{b3} - {a3}·{b2})i - ({a1}·{b3} - {a3}·{b1})j + ({a1}·{b2} - {a2}·{b1})k = {result}",
                "en": "Step 2: = ({a2}·{b3} - {a3}·{b2})i - ({a1}·{b3} - {a3}·{b1})j + ({a1}·{b2} - {a2}·{b1})k = {result}"
            },
            "triple_product": {
                "ru": "Шаг {step}: (a⃗, b⃗, c⃗) = a⃗ · (b⃗ × c⃗) = {result}",
                "en": "Step {step}: (a⃗, b⃗, c⃗) = a⃗ · (b⃗ × c⃗) = {result}"
            },
            "plane_normal": {
                "ru": "Шаг {step}: Нормаль к плоскости n⃗ = AB⃗ × AC⃗ = {normal}",
                "en": "Step {step}: Normal to plane n⃗ = AB⃗ × AC⃗ = {normal}"
            },
            "plane_result": {
                "ru": "Шаг {step}: Уравнение плоскости: {a}x + {b}y + {c}z + {d} = 0",
                "en": "Step {step}: Plane equation: {a}x + {b}y + {c}z + {d} = 0"
            },
            "distance_formula": {
                "ru": "Шаг {step}: d = |Ax₀ + By₀ + Cz₀ + D| / √(A² + B² + C²) = {distance}",
                "en": "Step {step}: d = |Ax₀ + By₀ + Cz₀ + D| / √(A² + B² + C²) = {distance}"
            },
            "dot_product": {
                "ru": "Шаг {step}: a⃗ · b⃗ = {a1}·{b1} + {a2}·{b2} + {a3}·{b3} = {result}",
                "en": "Step {step}: a⃗ · b⃗ = {a1}·{b1} + {a2}·{b2} + {a3}·{b3} = {result}"
            },
            "magnitudes": {
                "ru": "Шаг {step}: |a⃗| = {mag_a}, |b⃗| = {mag_b}",
                "en": "Step {step}: |a⃗| = {mag_a}, |b⃗| = {mag_b}"
            },
            "angle_formula": {
                "ru": "Шаг {step}: cos θ = (a⃗ · b⃗) / (|a⃗| · |b⃗|) = {cos_val}, θ = {angle}°",
                "en": "Step {step}: cos θ = (a⃗ · b⃗) / (|a⃗| · |b⃗|) = {cos_val}, θ = {angle}°"
            },
            "projection_formula": {
                "ru": "Шаг {step}: proj_b⃗(a⃗) = (a⃗ · b⃗ / |b⃗|²) · b⃗ = {result}",
                "en": "Step {step}: proj_b⃗(a⃗) = (a⃗ · b⃗ / |b⃗|²) · b⃗ = {result}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 35) FINANCIAL_MATH - Финансовая математика
    #----------------------------------------------------------------------------
    "financial_math": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по финансовой математике.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the financial mathematics problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "simple_interest": {
                "ru": "Вычислите простой процент на сумму {P} при ставке {r}% годовых за {t} лет",
                "en": "Calculate simple interest on principal {P} at {r}% annual rate for {t} years"
            },
            "compound_interest": {
                "ru": "Вычислите сложный процент на сумму {P} при ставке {r}% годовых за {t} лет (начисление {n} раз в год)",
                "en": "Calculate compound interest on principal {P} at {r}% annual rate for {t} years (compounded {n} times per year)"
            },
            "present_value": {
                "ru": "Найдите текущую стоимость {FV}, которая будет получена через {t} лет при ставке {r}%",
                "en": "Find the present value of {FV} to be received in {t} years at {r}% rate"
            },
            "annuity_pv": {
                "ru": "Найдите текущую стоимость аннуитета с платежами {PMT} в течение {n} периодов при ставке {r}%",
                "en": "Find the present value of an annuity with payments {PMT} for {n} periods at {r}% rate"
            },
            "annuity_fv": {
                "ru": "Найдите будущую стоимость аннуитета с платежами {PMT} в течение {n} периодов при ставке {r}%",
                "en": "Find the future value of an annuity with payments {PMT} for {n} periods at {r}% rate"
            },
            "loan_payment": {
                "ru": "Рассчитайте ежемесячный платёж по кредиту {P} на {t} лет под {r}% годовых",
                "en": "Calculate monthly payment for a loan of {P} for {t} years at {r}% annual rate"
            },
            "npv": {
                "ru": "Рассчитайте NPV проекта с начальной инвестицией {I0} и денежными потоками {cash_flows} при ставке дисконтирования {r}%",
                "en": "Calculate NPV of a project with initial investment {I0} and cash flows {cash_flows} at discount rate {r}%"
            }
        },
        "steps": {
            "simple_interest_formula": {
                "ru": "Шаг 1: I = P × r × t = {P} × {r} × {t} = {I}",
                "en": "Step 1: I = P × r × t = {P} × {r} × {t} = {I}"
            },
            "simple_interest_total": {
                "ru": "Шаг 2: Итого: A = P + I = {P} + {I} = {A}",
                "en": "Step 2: Total: A = P + I = {P} + {I} = {A}"
            },
            "compound_formula": {
                "ru": "Шаг 1: A = P(1 + r/n)^(nt) = {P}(1 + {r}/{n})^({n}×{t})",
                "en": "Step 1: A = P(1 + r/n)^(nt) = {P}(1 + {r}/{n})^({n}×{t})"
            },
            "compound_result": {
                "ru": "Шаг 2: A = {A}, процент = {interest}",
                "en": "Step 2: A = {A}, interest = {interest}"
            },
            "pv_formula": {
                "ru": "Шаг 1: PV = FV / (1 + r)^t = {FV} / (1 + {r})^{t} = {PV}",
                "en": "Step 1: PV = FV / (1 + r)^t = {FV} / (1 + {r})^{t} = {PV}"
            },
            "annuity_pv_formula": {
                "ru": "Шаг 1: PV = PMT × [(1 - (1+r)^(-n)) / r] = {PMT} × [(1 - (1+{r})^(-{n})) / {r}] = {PV}",
                "en": "Step 1: PV = PMT × [(1 - (1+r)^(-n)) / r] = {PMT} × [(1 - (1+{r})^(-{n})) / {r}] = {PV}"
            },
            "loan_formula": {
                "ru": "Шаг 1: PMT = P × [r(1+r)^n] / [(1+r)^n - 1]",
                "en": "Step 1: PMT = P × [r(1+r)^n] / [(1+r)^n - 1]"
            },
            "npv_formula": {
                "ru": "Шаг 1: NPV = -I₀ + Σ(CFₜ / (1+r)^t)",
                "en": "Step 1: NPV = -I₀ + Σ(CFₜ / (1+r)^t)"
            },
            "npv_calculation": {
                "ru": "Шаг {step}: CF_{t} / (1+r)^{t} = {cf} / (1+{r})^{t} = {pv}",
                "en": "Step {step}: CF_{t} / (1+r)^{t} = {cf} / (1+{r})^{t} = {pv}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # 36) SERIES - Ряды и сходимость
    #----------------------------------------------------------------------------
    "series": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Исследуйте ряд на сходимость или найдите его сумму.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Итоговый ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Investigate series convergence or find its sum.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Final answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "geometric_sum": {
                "ru": "Найдите сумму геометрического ряда: {first_term} + {second_term} + ... (бесконечный ряд при |r| < 1)",
                "en": "Find the sum of the geometric series: {first_term} + {second_term} + ... (infinite series where |r| < 1)"
            },
            "convergence_test": {
                "ru": "Исследуйте сходимость ряда Σ({general_term}), n = 1, 2, 3, ...",
                "en": "Test the convergence of the series Σ({general_term}), n = 1, 2, 3, ..."
            },
            "partial_sum": {
                "ru": "Найдите сумму первых {n} членов ряда с общим членом aₙ = {general_term}",
                "en": "Find the sum of the first {n} terms of the series with general term aₙ = {general_term}"
            },
            "taylor_series": {
                "ru": "Найдите ряд Тейлора функции f(x) = {function} в точке x = {a} (первые {n} членов)",
                "en": "Find the Taylor series of f(x) = {function} at x = {a} (first {n} terms)"
            },
            "radius_convergence": {
                "ru": "Найдите радиус сходимости степенного ряда Σ({general_term})xⁿ",
                "en": "Find the radius of convergence of the power series Σ({general_term})xⁿ"
            },
            "telescoping": {
                "ru": "Найдите сумму телескопического ряда Σ({general_term}), n = 1 до ∞",
                "en": "Find the sum of the telescoping series Σ({general_term}), n = 1 to ∞"
            }
        },
        "steps": {
            "identify_type": {
                "ru": "Шаг 1: Определяем тип ряда: {type}",
                "en": "Step 1: Identify series type: {type}"
            },
            "geometric_ratio": {
                "ru": "Шаг {step}: Отношение r = {second}/{first} = {ratio}",
                "en": "Step {step}: Ratio r = {second}/{first} = {ratio}"
            },
            "geometric_sum_formula": {
                "ru": "Шаг {step}: S = a / (1 - r) = {a} / (1 - {r}) = {sum}",
                "en": "Step {step}: S = a / (1 - r) = {a} / (1 - {r}) = {sum}"
            },
            "ratio_test": {
                "ru": "Шаг {step}: Признак Даламбера: L = lim|aₙ₊₁/aₙ| = {limit}",
                "en": "Step {step}: Ratio test: L = lim|aₙ₊₁/aₙ| = {limit}"
            },
            "ratio_conclusion": {
                "ru": "Шаг {step}: L = {limit} {comparison} 1 → ряд {conclusion}",
                "en": "Step {step}: L = {limit} {comparison} 1 → series {conclusion}"
            },
            "root_test": {
                "ru": "Шаг {step}: Признак Коши: L = lim ⁿ√|aₙ| = {limit}",
                "en": "Step {step}: Root test: L = lim ⁿ√|aₙ| = {limit}"
            },
            "comparison_test": {
                "ru": "Шаг {step}: Сравниваем с рядом {comparison_series}",
                "en": "Step {step}: Compare with series {comparison_series}"
            },
            "taylor_coefficient": {
                "ru": "Шаг {step}: f⁽{n}⁾({a})/{n}! = {coef}",
                "en": "Step {step}: f⁽{n}⁾({a})/{n}! = {coef}"
            },
            "radius_formula": {
                "ru": "Шаг {step}: R = lim|aₙ/aₙ₊₁| = {radius}",
                "en": "Step {step}: R = lim|aₙ/aₙ₊₁| = {radius}"
            }
        },
        "conclusions": {
            "converges": {"ru": "сходится", "en": "converges"},
            "diverges": {"ru": "расходится", "en": "diverges"},
            "inconclusive": {"ru": "признак не применим", "en": "inconclusive"}
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    # ============================================================================
    # ФИЗИЧЕСКИЕ ЗАДАЧИ
    # ============================================================================

    #----------------------------------------------------------------------------
    # KINEMATICS - Кинематика
    #----------------------------------------------------------------------------
    "kinematics": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по кинематике.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение с формулами)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Численный ответ с единицами измерения)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the kinematics problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution with formulas)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Numerical answer with units)\n"
                "  </answer>"
            )
        },
        "problem": {
            "uniform_motion": {
                "ru": "Тело движется равномерно со скоростью {v} м/с. Какое расстояние оно пройдёт за {t} с?",
                "en": "A body moves uniformly at {v} m/s. What distance will it travel in {t} s?"
            },
            "find_velocity": {
                "ru": "Тело прошло расстояние {s} м за {t} с при равномерном движении. Найдите скорость.",
                "en": "A body traveled {s} m in {t} s with uniform motion. Find the velocity."
            },
            "accelerated_distance": {
                "ru": "Тело начинает движение из состояния покоя с ускорением {a} м/с². Какое расстояние оно пройдёт за {t} с?",
                "en": "A body starts from rest with acceleration {a} m/s². What distance will it travel in {t} s?"
            },
            "accelerated_velocity": {
                "ru": "Тело движется с начальной скоростью {v0} м/с и ускорением {a} м/с². Какова скорость через {t} с?",
                "en": "A body moves with initial velocity {v0} m/s and acceleration {a} m/s². What is the velocity after {t} s?"
            },
            "projectile_max_height": {
                "ru": "Тело брошено вертикально вверх со скоростью {v0} м/с. Найдите максимальную высоту подъёма. (g = {g} м/с²)",
                "en": "A body is thrown vertically upward at {v0} m/s. Find the maximum height. (g = {g} m/s²)"
            },
            "projectile_range": {
                "ru": "Тело брошено под углом {angle}° к горизонту со скоростью {v0} м/с. Найдите дальность полёта. (g = {g} м/с²)",
                "en": "A body is thrown at angle {angle}° to the horizontal at {v0} m/s. Find the range. (g = {g} m/s²)"
            },
            "circular_velocity": {
                "ru": "Тело движется по окружности радиусом {r} м с периодом {T} с. Найдите линейную скорость.",
                "en": "A body moves in a circle of radius {r} m with period {T} s. Find the linear velocity."
            },
            "circular_acceleration": {
                "ru": "Тело движется по окружности радиусом {r} м со скоростью {v} м/с. Найдите центростремительное ускорение.",
                "en": "A body moves in a circle of radius {r} m at velocity {v} m/s. Find the centripetal acceleration."
            }
        },
        "steps": {
            "formula": {
                "ru": "Шаг {step}: Используем формулу: {formula}",
                "en": "Step {step}: Using formula: {formula}"
            },
            "substitute": {
                "ru": "Шаг {step}: Подставляем значения: {substitution}",
                "en": "Step {step}: Substituting values: {substitution}"
            },
            "calculate": {
                "ru": "Шаг {step}: Вычисляем: {calculation}",
                "en": "Step {step}: Calculating: {calculation}"
            }
        },
        "formulas": {
            "uniform_motion": "s = v·t",
            "velocity_time": "v = v₀ + a·t",
            "distance_accelerated": "s = v₀·t + (a·t²)/2",
            "velocity_distance": "v² = v₀² + 2·a·s",
            "max_height": "h = v₀²/(2g)",
            "projectile_range": "R = (v₀²·sin(2θ))/g",
            "circular_velocity": "v = 2πr/T",
            "centripetal_acceleration": "a = v²/r"
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # DYNAMICS - Динамика
    #----------------------------------------------------------------------------
    "dynamics": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по динамике (законы Ньютона).\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Пошаговое решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ с единицами)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the dynamics problem (Newton's laws).\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Step-by-step solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer with units)\n"
                "  </answer>"
            )
        },
        "problem": {
            "newton_second": {
                "ru": "На тело массой {m} кг действует сила {F} Н. Найдите ускорение тела.",
                "en": "A force of {F} N acts on a body of mass {m} kg. Find the acceleration."
            },
            "find_force": {
                "ru": "Тело массой {m} кг движется с ускорением {a} м/с². Найдите силу, действующую на тело.",
                "en": "A body of mass {m} kg moves with acceleration {a} m/s². Find the force acting on it."
            },
            "weight": {
                "ru": "Найдите вес тела массой {m} кг. (g = {g} м/с²)",
                "en": "Find the weight of a body with mass {m} kg. (g = {g} m/s²)"
            },
            "friction": {
                "ru": "Тело массой {m} кг движется по горизонтальной поверхности. Коэффициент трения μ = {mu}. Найдите силу трения. (g = {g} м/с²)",
                "en": "A body of mass {m} kg moves on a horizontal surface. Friction coefficient μ = {mu}. Find the friction force. (g = {g} m/s²)"
            },
            "inclined_plane": {
                "ru": "Тело массой {m} кг находится на наклонной плоскости с углом {angle}°. Найдите силу, действующую вдоль плоскости. (g = {g} м/с²)",
                "en": "A body of mass {m} kg is on an inclined plane at angle {angle}°. Find the force along the plane. (g = {g} m/s²)"
            },
            "tension": {
                "ru": "Два тела массами {m1} кг и {m2} кг соединены нитью через блок. Найдите натяжение нити. (g = {g} м/с²)",
                "en": "Two bodies of masses {m1} kg and {m2} kg are connected by a string over a pulley. Find the tension. (g = {g} m/s²)"
            }
        },
        "steps": {
            "identify_forces": {
                "ru": "Шаг 1: Определяем силы, действующие на тело: {forces}",
                "en": "Step 1: Identify forces acting on the body: {forces}"
            },
            "apply_newton": {
                "ru": "Шаг {step}: Применяем второй закон Ньютона: F = ma",
                "en": "Step {step}: Apply Newton's second law: F = ma"
            },
            "calculate_result": {
                "ru": "Шаг {step}: {calculation}",
                "en": "Step {step}: {calculation}"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # ENERGY - Работа, энергия, мощность
    #----------------------------------------------------------------------------
    "energy": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу на работу, энергию или мощность.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the work, energy, or power problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "work": {
                "ru": "Сила {F} Н перемещает тело на {s} м в направлении действия силы. Найдите работу силы.",
                "en": "A force of {F} N moves a body {s} m in the direction of the force. Find the work done."
            },
            "work_angle": {
                "ru": "Сила {F} Н действует на тело под углом {angle}° к направлению перемещения {s} м. Найдите работу.",
                "en": "A force of {F} N acts on a body at angle {angle}° to the displacement of {s} m. Find the work."
            },
            "kinetic_energy": {
                "ru": "Найдите кинетическую энергию тела массой {m} кг, движущегося со скоростью {v} м/с.",
                "en": "Find the kinetic energy of a body with mass {m} kg moving at {v} m/s."
            },
            "potential_energy": {
                "ru": "Найдите потенциальную энергию тела массой {m} кг на высоте {h} м. (g = {g} м/с²)",
                "en": "Find the potential energy of a body with mass {m} kg at height {h} m. (g = {g} m/s²)"
            },
            "power": {
                "ru": "Сила совершает работу {W} Дж за время {t} с. Найдите мощность.",
                "en": "A force does {W} J of work in {t} s. Find the power."
            },
            "conservation": {
                "ru": "Тело массой {m} кг падает с высоты {h} м. Найдите скорость в момент удара о землю. (g = {g} м/с²)",
                "en": "A body of mass {m} kg falls from height {h} m. Find the velocity at impact. (g = {g} m/s²)"
            }
        },
        "steps": {
            "work_formula": {
                "ru": "Шаг 1: Работа A = F·s·cos(α)",
                "en": "Step 1: Work W = F·s·cos(α)"
            },
            "kinetic_formula": {
                "ru": "Шаг 1: Кинетическая энергия Eₖ = mv²/2",
                "en": "Step 1: Kinetic energy Eₖ = mv²/2"
            },
            "potential_formula": {
                "ru": "Шаг 1: Потенциальная энергия Eₚ = mgh",
                "en": "Step 1: Potential energy Eₚ = mgh"
            },
            "power_formula": {
                "ru": "Шаг 1: Мощность P = A/t",
                "en": "Step 1: Power P = W/t"
            },
            "conservation_law": {
                "ru": "Шаг 1: По закону сохранения энергии: mgh = mv²/2",
                "en": "Step 1: By conservation of energy: mgh = mv²/2"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # MOMENTUM - Импульс
    #----------------------------------------------------------------------------
    "momentum": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу на импульс и столкновения.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the momentum and collision problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "momentum": {
                "ru": "Найдите импульс тела массой {m} кг, движущегося со скоростью {v} м/с.",
                "en": "Find the momentum of a body with mass {m} kg moving at {v} m/s."
            },
            "impulse": {
                "ru": "Сила {F} Н действует на тело в течение {t} с. Найдите импульс силы.",
                "en": "A force of {F} N acts on a body for {t} s. Find the impulse."
            },
            "inelastic_collision": {
                "ru": "Тело массой {m1} кг со скоростью {v1} м/с сталкивается с неподвижным телом массой {m2} кг. После столкновения тела движутся вместе. Найдите скорость после столкновения.",
                "en": "A body of mass {m1} kg moving at {v1} m/s collides with a stationary body of mass {m2} kg. After collision they move together. Find the velocity after collision."
            },
            "elastic_collision": {
                "ru": "Тело массой {m1} кг со скоростью {v1} м/с упруго сталкивается с неподвижным телом массой {m2} кг. Найдите скорости тел после столкновения.",
                "en": "A body of mass {m1} kg moving at {v1} m/s elastically collides with a stationary body of mass {m2} kg. Find velocities after collision."
            }
        },
        "steps": {
            "momentum_formula": {
                "ru": "Шаг 1: Импульс p = mv",
                "en": "Step 1: Momentum p = mv"
            },
            "conservation": {
                "ru": "Шаг 1: По закону сохранения импульса: m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'",
                "en": "Step 1: By conservation of momentum: m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # CIRCUITS - Электрические цепи
    #----------------------------------------------------------------------------
    "circuits": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по электрическим цепям.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the electrical circuit problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "ohms_law": {
                "ru": "В цепи с сопротивлением {R} Ом протекает ток {I} А. Найдите напряжение.",
                "en": "A current of {I} A flows through a resistance of {R} Ω. Find the voltage."
            },
            "find_current": {
                "ru": "К резистору сопротивлением {R} Ом приложено напряжение {U} В. Найдите силу тока.",
                "en": "A voltage of {U} V is applied to a resistor of {R} Ω. Find the current."
            },
            "find_resistance": {
                "ru": "При напряжении {U} В через проводник протекает ток {I} А. Найдите сопротивление.",
                "en": "At voltage {U} V, a current of {I} A flows through a conductor. Find the resistance."
            },
            "series": {
                "ru": "Резисторы {resistors} соединены последовательно. Найдите общее сопротивление.",
                "en": "Resistors {resistors} are connected in series. Find the total resistance."
            },
            "parallel": {
                "ru": "Резисторы {resistors} соединены параллельно. Найдите общее сопротивление.",
                "en": "Resistors {resistors} are connected in parallel. Find the total resistance."
            },
            "power_circuit": {
                "ru": "В цепи с напряжением {U} В и током {I} А найдите мощность.",
                "en": "In a circuit with voltage {U} V and current {I} A, find the power."
            },
            "kirchhoff": {
                "ru": "В узле сходятся токи: {currents}. Найдите неизвестный ток по первому закону Кирхгофа.",
                "en": "Currents meet at a junction: {currents}. Find the unknown current using Kirchhoff's first law."
            }
        },
        "steps": {
            "ohms_law": {
                "ru": "Шаг 1: По закону Ома: U = IR",
                "en": "Step 1: By Ohm's law: U = IR"
            },
            "series_formula": {
                "ru": "Шаг 1: При последовательном соединении: R = R₁ + R₂ + ...",
                "en": "Step 1: For series connection: R = R₁ + R₂ + ..."
            },
            "parallel_formula": {
                "ru": "Шаг 1: При параллельном соединении: 1/R = 1/R₁ + 1/R₂ + ...",
                "en": "Step 1: For parallel connection: 1/R = 1/R₁ + 1/R₂ + ..."
            },
            "power_formula": {
                "ru": "Шаг 1: Мощность P = UI = I²R = U²/R",
                "en": "Step 1: Power P = UI = I²R = U²/R"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # ELECTROSTATICS - Электростатика
    #----------------------------------------------------------------------------
    "electrostatics": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по электростатике.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the electrostatics problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "coulomb": {
                "ru": "Два точечных заряда {q1} Кл и {q2} Кл находятся на расстоянии {r} м. Найдите силу взаимодействия. (k = 9×10⁹ Н·м²/Кл²)",
                "en": "Two point charges {q1} C and {q2} C are {r} m apart. Find the force. (k = 9×10⁹ N·m²/C²)"
            },
            "electric_field": {
                "ru": "Точечный заряд {q} Кл создаёт электрическое поле. Найдите напряжённость поля на расстоянии {r} м от заряда.",
                "en": "A point charge {q} C creates an electric field. Find the field strength at distance {r} m."
            },
            "potential": {
                "ru": "Найдите потенциал электрического поля точечного заряда {q} Кл на расстоянии {r} м.",
                "en": "Find the electric potential of a point charge {q} C at distance {r} m."
            },
            "work_in_field": {
                "ru": "Заряд {q} Кл перемещается в однородном электрическом поле с напряжённостью {E} В/м на расстояние {d} м вдоль линий поля. Найдите работу поля.",
                "en": "A charge {q} C moves in a uniform electric field of {E} V/m through distance {d} m along field lines. Find the work done."
            }
        },
        "steps": {
            "coulomb_law": {
                "ru": "Шаг 1: По закону Кулона: F = k·|q₁·q₂|/r²",
                "en": "Step 1: By Coulomb's law: F = k·|q₁·q₂|/r²"
            },
            "field_formula": {
                "ru": "Шаг 1: Напряжённость поля: E = k·q/r²",
                "en": "Step 1: Field strength: E = k·q/r²"
            },
            "potential_formula": {
                "ru": "Шаг 1: Потенциал: φ = k·q/r",
                "en": "Step 1: Potential: φ = k·q/r"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # CAPACITORS - Конденсаторы
    #----------------------------------------------------------------------------
    "capacitors": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу на конденсаторы.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the capacitor problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "charge": {
                "ru": "Конденсатор ёмкостью {C} Ф заряжен до напряжения {U} В. Найдите заряд на обкладках.",
                "en": "A capacitor of {C} F is charged to {U} V. Find the charge on the plates."
            },
            "energy": {
                "ru": "Найдите энергию конденсатора ёмкостью {C} Ф, заряженного до напряжения {U} В.",
                "en": "Find the energy of a capacitor of {C} F charged to {U} V."
            },
            "series": {
                "ru": "Конденсаторы {capacitors} соединены последовательно. Найдите общую ёмкость.",
                "en": "Capacitors {capacitors} are connected in series. Find the total capacitance."
            },
            "parallel": {
                "ru": "Конденсаторы {capacitors} соединены параллельно. Найдите общую ёмкость.",
                "en": "Capacitors {capacitors} are connected in parallel. Find the total capacitance."
            }
        },
        "steps": {
            "charge_formula": {
                "ru": "Шаг 1: Заряд q = CU",
                "en": "Step 1: Charge q = CU"
            },
            "energy_formula": {
                "ru": "Шаг 1: Энергия W = CU²/2 = qU/2 = q²/(2C)",
                "en": "Step 1: Energy W = CU²/2 = qU/2 = q²/(2C)"
            },
            "series_formula": {
                "ru": "Шаг 1: При последовательном соединении: 1/C = 1/C₁ + 1/C₂ + ...",
                "en": "Step 1: For series: 1/C = 1/C₁ + 1/C₂ + ..."
            },
            "parallel_formula": {
                "ru": "Шаг 1: При параллельном соединении: C = C₁ + C₂ + ...",
                "en": "Step 1: For parallel: C = C₁ + C₂ + ..."
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # GAS_LAWS - Газовые законы
    #----------------------------------------------------------------------------
    "gas_laws": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу на газовые законы.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the gas laws problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "ideal_gas": {
                "ru": "{n} моль идеального газа при температуре {T} К занимает объём {V} л. Найдите давление. (R = 8.314 Дж/(моль·К))",
                "en": "{n} mol of ideal gas at temperature {T} K occupies volume {V} L. Find the pressure. (R = 8.314 J/(mol·K))"
            },
            "isothermal": {
                "ru": "Газ при давлении {P1} Па занимает объём {V1} л. При изотермическом процессе объём изменился до {V2} л. Найдите новое давление.",
                "en": "A gas at pressure {P1} Pa occupies volume {V1} L. In an isothermal process, volume changed to {V2} L. Find the new pressure."
            },
            "isobaric": {
                "ru": "Газ при температуре {T1} К занимает объём {V1} л. При изобарическом нагревании температура стала {T2} К. Найдите новый объём.",
                "en": "A gas at temperature {T1} K occupies volume {V1} L. After isobaric heating to {T2} K, find the new volume."
            },
            "isochoric": {
                "ru": "Газ при температуре {T1} К имеет давление {P1} Па. При изохорическом нагревании температура стала {T2} К. Найдите новое давление.",
                "en": "A gas at temperature {T1} K has pressure {P1} Pa. After isochoric heating to {T2} K, find the new pressure."
            },
            "combined": {
                "ru": "Газ в состоянии (P₁={P1} Па, V₁={V1} л, T₁={T1} К) переходит в состояние с V₂={V2} л, T₂={T2} К. Найдите P₂.",
                "en": "A gas changes from state (P₁={P1} Pa, V₁={V1} L, T₁={T1} K) to V₂={V2} L, T₂={T2} K. Find P₂."
            }
        },
        "steps": {
            "ideal_gas_law": {
                "ru": "Шаг 1: Уравнение Менделеева-Клапейрона: PV = nRT",
                "en": "Step 1: Ideal gas law: PV = nRT"
            },
            "boyle_law": {
                "ru": "Шаг 1: Закон Бойля-Мариотта (T=const): P₁V₁ = P₂V₂",
                "en": "Step 1: Boyle's law (T=const): P₁V₁ = P₂V₂"
            },
            "charles_law": {
                "ru": "Шаг 1: Закон Гей-Люссака (P=const): V₁/T₁ = V₂/T₂",
                "en": "Step 1: Charles's law (P=const): V₁/T₁ = V₂/T₂"
            },
            "gay_lussac_law": {
                "ru": "Шаг 1: Закон Шарля (V=const): P₁/T₁ = P₂/T₂",
                "en": "Step 1: Gay-Lussac's law (V=const): P₁/T₁ = P₂/T₂"
            },
            "combined_law": {
                "ru": "Шаг 1: Объединённый газовый закон: P₁V₁/T₁ = P₂V₂/T₂",
                "en": "Step 1: Combined gas law: P₁V₁/T₁ = P₂V₂/T₂"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # HEAT_TRANSFER - Теплопередача
    #----------------------------------------------------------------------------
    "heat_transfer": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу на теплопередачу.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the heat transfer problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "heat_capacity": {
                "ru": "Сколько теплоты нужно для нагревания {m} кг {substance} от {T1}°C до {T2}°C? (c = {c} Дж/(кг·°C))",
                "en": "How much heat is needed to warm {m} kg of {substance} from {T1}°C to {T2}°C? (c = {c} J/(kg·°C))"
            },
            "mixing": {
                "ru": "Смешивают {m1} кг воды при {T1}°C и {m2} кг воды при {T2}°C. Найдите температуру смеси.",
                "en": "Mix {m1} kg of water at {T1}°C with {m2} kg of water at {T2}°C. Find the mixture temperature."
            },
            "phase_change": {
                "ru": "Сколько теплоты нужно для плавления {m} кг льда при 0°C? (λ = {lambda_} Дж/кг)",
                "en": "How much heat is needed to melt {m} kg of ice at 0°C? (λ = {lambda_} J/kg)"
            },
            "efficiency": {
                "ru": "Тепловая машина получает {Q1} Дж теплоты и отдаёт {Q2} Дж. Найдите КПД.",
                "en": "A heat engine receives {Q1} J of heat and releases {Q2} J. Find the efficiency."
            }
        },
        "steps": {
            "heat_formula": {
                "ru": "Шаг 1: Количество теплоты Q = cm(T₂ - T₁)",
                "en": "Step 1: Heat Q = cm(T₂ - T₁)"
            },
            "mixing_equation": {
                "ru": "Шаг 1: Уравнение теплового баланса: Q_отд = Q_пол",
                "en": "Step 1: Heat balance equation: Q_released = Q_absorbed"
            },
            "phase_formula": {
                "ru": "Шаг 1: Теплота фазового перехода Q = λm",
                "en": "Step 1: Latent heat Q = λm"
            },
            "efficiency_formula": {
                "ru": "Шаг 1: КПД η = (Q₁ - Q₂)/Q₁ = A/Q₁",
                "en": "Step 1: Efficiency η = (Q₁ - Q₂)/Q₁ = W/Q₁"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # WAVES - Волны
    #----------------------------------------------------------------------------
    "waves": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу на волны.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the wave problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "wavelength": {
                "ru": "Волна с частотой {f} Гц распространяется со скоростью {v} м/с. Найдите длину волны.",
                "en": "A wave with frequency {f} Hz travels at {v} m/s. Find the wavelength."
            },
            "frequency": {
                "ru": "Волна длиной {lambda_} м распространяется со скоростью {v} м/с. Найдите частоту.",
                "en": "A wave of length {lambda_} m travels at {v} m/s. Find the frequency."
            },
            "period": {
                "ru": "Найдите период волны с частотой {f} Гц.",
                "en": "Find the period of a wave with frequency {f} Hz."
            },
            "sound_speed": {
                "ru": "Звук с частотой {f} Гц имеет длину волны {lambda_} м. Найдите скорость звука.",
                "en": "Sound with frequency {f} Hz has wavelength {lambda_} m. Find the speed of sound."
            },
            "doppler": {
                "ru": "Источник звука с частотой {f0} Гц движется к наблюдателю со скоростью {v_s} м/с. Скорость звука {v} м/с. Найдите воспринимаемую частоту.",
                "en": "A sound source of frequency {f0} Hz moves toward the observer at {v_s} m/s. Speed of sound is {v} m/s. Find the perceived frequency."
            }
        },
        "steps": {
            "wave_equation": {
                "ru": "Шаг 1: Уравнение волны: v = λf",
                "en": "Step 1: Wave equation: v = λf"
            },
            "period_formula": {
                "ru": "Шаг 1: Период T = 1/f",
                "en": "Step 1: Period T = 1/f"
            },
            "doppler_formula": {
                "ru": "Шаг 1: Эффект Доплера: f' = f₀·(v ± v_наб)/(v ∓ v_ист)",
                "en": "Step 1: Doppler effect: f' = f₀·(v ± v_obs)/(v ∓ v_src)"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

    #----------------------------------------------------------------------------
    # OPTICS - Оптика
    #----------------------------------------------------------------------------
    "optics": {
        "instructions": {
            "ru": (
                "type: structured_text_with_tags\n"
                "Описание: Решите задачу по оптике.\n"
                "Формат ответа:\n"
                "  <reasoning>\n"
                "    (Решение)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Ответ)\n"
                "  </answer>"
            ),
            "en": (
                "type: structured_text_with_tags\n"
                "Description: Solve the optics problem.\n"
                "Answer format:\n"
                "  <reasoning>\n"
                "    (Solution)\n"
                "  </reasoning>\n"
                "  <answer>\n"
                "    (Answer)\n"
                "  </answer>"
            )
        },
        "problem": {
            "snell": {
                "ru": "Луч света падает из среды с показателем преломления {n1} в среду с {n2} под углом {angle1}°. Найдите угол преломления.",
                "en": "Light travels from a medium with refractive index {n1} to {n2} at angle {angle1}°. Find the refraction angle."
            },
            "critical_angle": {
                "ru": "Найдите критический угол полного внутреннего отражения при переходе из среды с n = {n1} в среду с n = {n2}.",
                "en": "Find the critical angle for total internal reflection from a medium with n = {n1} to n = {n2}."
            },
            "thin_lens": {
                "ru": "Предмет находится на расстоянии {d} см от тонкой линзы с фокусным расстоянием {f} см. Найдите расстояние до изображения.",
                "en": "An object is {d} cm from a thin lens with focal length {f} cm. Find the image distance."
            },
            "magnification": {
                "ru": "Линза даёт изображение на расстоянии {f_img} см при расстоянии до предмета {d_obj} см. Найдите увеличение.",
                "en": "A lens produces an image at {f_img} cm when object distance is {d_obj} cm. Find the magnification."
            },
            "mirror": {
                "ru": "Предмет находится на расстоянии {d} см от вогнутого зеркала с радиусом кривизны {R} см. Найдите расстояние до изображения.",
                "en": "An object is {d} cm from a concave mirror with radius {R} cm. Find the image distance."
            }
        },
        "steps": {
            "snell_law": {
                "ru": "Шаг 1: Закон Снелла: n₁·sin(θ₁) = n₂·sin(θ₂)",
                "en": "Step 1: Snell's law: n₁·sin(θ₁) = n₂·sin(θ₂)"
            },
            "lens_formula": {
                "ru": "Шаг 1: Формула тонкой линзы: 1/f = 1/d + 1/f'",
                "en": "Step 1: Thin lens formula: 1/f = 1/d + 1/f'"
            },
            "magnification_formula": {
                "ru": "Шаг 1: Увеличение Г = f'/d = H'/H",
                "en": "Step 1: Magnification M = f'/d = H'/H"
            },
            "mirror_formula": {
                "ru": "Шаг 1: Формула зеркала: 1/d + 1/f' = 2/R",
                "en": "Step 1: Mirror formula: 1/d + 1/f' = 2/R"
            }
        },
        "final_answer": {
            "ru": "Ответ: {answer}",
            "en": "Answer: {answer}"
        }
    },

}
