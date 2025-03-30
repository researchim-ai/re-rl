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

}
