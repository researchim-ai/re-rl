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
    },
    "contradiction": {
        "problem": {
            "ru": "Найдите ложное утверждение в следующем наборе:\n{statements}",
            "en": "Find the false statement in the following set:\n{statements}"
        },
        "step1": {
            "ru": "Шаг 1: Проанализируйте представленные утверждения.",
            "en": "Step 1: Analyze the provided statements."
        },
        "final_answer": {
            "ru": "Ложное утверждение: {false_statement}",
            "en": "False statement: {false_statement}"
        }
    },
    "contradiction_facts": {
    "ru": {
        "true": [
            "Кошки являются млекопитающими.",
            "Собаки имеют четыре ноги.",
            "Слоны – самые большие млекопитающие на суше.",
            "Большинство птиц умеют летать.",
            "Некоторые рыбы могут менять цвет.",
            "Деревья имеют корни.",
            "Многие растения используют солнечный свет для фотосинтеза.",
            "Цветы имеют яркие окраски для привлечения насекомых.",
            "Большинство трав растёт на открытых пространствах.",
            "Листья помогают растениям производить энергию.",
            "Река Волга является самой длинной в Европе.",
            "Москва является столицей России.",
            "Горы образуют естественные преграды.",
            "Многие города расположены на берегах рек.",
            "Океаны покрывают большую часть Земли.",
            "Вода состоит из двух атомов водорода и одного атома кислорода.",
            "Земля вращается вокруг своей оси.",
            "Свет имеет волновую природу.",
            "Электричество передаётся по проводам.",
            "Гравитация удерживает планеты на орбитах.",
            "Пирамида Хеопса является древним чудом света.",
            "Римская империя оказала огромное влияние на Европу.",
            "Великая Китайская стена строилась веками.",
            "Средневековье характеризуется феодальной системой.",
            "Эпоха Возрождения принесла множество художественных достижений.",
            "Северное сияние наблюдается в высоких широтах.",
            "Луна является единственным естественным спутником Земли.",
            "Солнце является центром Солнечной системы.",
            "Атом состоит из протонов, нейтронов и электронов.",
            "Молекулы образуются при соединении атомов.",
            "Орбиты планет являются эллиптическими.",
            "Вулканическая активность изменяет ландшафт.",
            "Метеориты падают на Землю с космоса.",
            "Антарктида покрыта льдом.",
            "Пустыни характеризуются крайне низкой влажностью.",
            "Джунгли полны разнообразных видов животных и растений.",
            "Равнины занимают большую часть континентов.",
            "Океанские течения влияют на климат Земли.",
            "Многие реки впадают в океаны.",
            "Климат Земли меняется со временем.",
            "Глобальное потепление является результатом изменения климата.",
            "Воздух состоит преимущественно из азота и кислорода.",
            "Лесное хозяйство важно для экосистем.",
            "Почва служит основой для роста растений.",
            "Биосфера включает все живые организмы.",
            "Экосистемы зависят от естественного баланса.",
            "Многие виды исчезают из-за утраты среды обитания.",
            "Заповедники созданы для охраны природы.",
            "Биоразнообразие критически важно для устойчивости экосистем.",
            "Хищники регулируют численность добычи.",
            "Многие растения обладают лекарственными свойствами.",
            "Травы широко используются в традиционной медицине.",
            "Фрукты богаты витаминами и минералами.",
            "Овощи составляют важную часть рациона человека.",
            "Зерновые культуры играют ключевую роль в питании.",
            "Молоко является источником кальция.",
            "Яйца содержат белки и важные питательные вещества.",
            "Мясо является источником белка и железа.",
            "Рыба богата омега-3 жирными кислотами.",
            "Морепродукты способствуют здоровому питанию.",
            "Птицы строят гнезда для своих птенцов.",
            "Некоторые животные мигрируют на большие расстояния.",
            "Дикие животные адаптированы к жизни в природе.",
            "Млекопитающие кормят своих детёнышей молоком.",
            "Приматы обладают высокой степенью интеллекта.",
            "Пчёлы играют ключевую роль в опылении.",
            "Муравьи известны своей организованностью.",
            "Некоторые насекомые используют яркие цвета для защиты.",
            "Пауки плетут сети для ловли добычи.",
            "Ракообразные обитают как в пресной, так и в солёной воде.",
            "Многие рептилии откладывают яйца.",
            "Амфибии живут как в воде, так и на суше.",
            "Некоторые рыбы могут дышать воздухом.",
            "Скорпионы обладают ядовитыми жалами.",
            "Медузы могут быть опасны для человека.",
            "Некоторые кораллы образуют обширные рифы.",
            "Животные пустыней имеют адаптации к жаркому климату.",
            "Ледники формируют уникальные ландшафты.",
            "Ландшафты варьируются от тундры до тропических лесов.",
            "Земля обладает множеством природных ресурсов.",
            "Геологи изучают строение земной коры.",
            "Многие минералы применяются в промышленности.",
            "Кристаллы отличаются симметричной структурой.",
            "Сейсмическая активность может вызвать землетрясения.",
            "Населённость регионов сильно различается.",
            "Экономика стран зависит от природных ресурсов.",
            "Технологии развиваются с каждым годом.",
            "Интернет изменил способы общения.",
            "Мобильные телефоны стали неотъемлемой частью жизни.",
            "Социальные сети влияют на общественное мнение.",
            "Многие люди используют смартфоны для работы и развлечений.",
            "Транспортные системы постоянно совершенствуются.",
            "Железнодорожный транспорт играет важную роль в логистике.",
            "Автомобили влияют на качество воздуха в городах.",
            "Аэропорты способствуют международным перевозкам.",
            "Космические исследования расширяют наши знания о Вселенной.",
            "Ракетные технологии позволяют запускать спутники.",
            "Наука постоянно открывает новые горизонты.",
            "Образование играет ключевую роль в развитии общества.",
            "Культурное наследие важно для национальной идентичности."
            ],
        "false": [
                "Солнце вращается вокруг Земли.",
                "Вода замерзает при 50 градусах Цельсия.",
                "Луна сделана из сыра.",
                "Человеческий организм может жить без кислорода вечно.",
                "Горы растут в высоту каждую ночь.",
                "Пингвины летают быстрее самолетов.",
                "Собаки могут говорить, если их правильно обучить.",
                "Деревья перемещаются на небольшие расстояния каждую весну.",
                "Все океаны заполнены пресной водой.",
                "Кошки имеют восемь ног.",
                "Человек может пережить падение с высоты 1000 метров без ущерба для здоровья.",
                "Молоко можно использовать как топливо для автомобилей.",
                "Гравитация на Марсе в десять раз сильнее, чем на Земле.",
                "Земля имеет форму куба.",
                "Антарктида покрыта песками вместо льда.",
                "Свет может двигаться медленнее, чем звук.",
                "Человеческий мозг способен хранить бесконечное количество информации.",
                "Пчёлы являются ночными животными.",
                "Пустыня Сахара является самым холодным местом на Земле.",
                "Океаны состоят из молока.",
                "Биение сердца человека происходит только один раз в час.",
                "Человек может дышать под водой без специального оборудования.",
                "Вулкан извергает замороженную лаву.",
                "Многие растения растут быстрее, если их поливать газировкой.",
                "Собаки рождаются со способностью летать.",
                "Свет от звезд доходит до Земли за несколько секунд.",
                "Время в космосе течет в обратном направлении.",
                "Все люди имеют одинаковый отпечаток пальца.",
                "Рыбы могут жить на суше без воды.",
                "Бумага может быть использована для приготовления пищи.",
                "Сахар растворяется в пустоте.",
                "Металлы могут плавиться при комнатной температуре, если их правильно нагреть.",
                "Книги могут читать сами себя.",
                "Молния никогда не бьёт дважды в одно и то же место.",
                "Земля стоит на спинах гигантских черепах.",
                "Динозавры до сих пор живут в скрытых районах Земли.",
                "Люди могут слышать ультразвук без специального оборудования.",
                "Сталь может плавиться от прикосновения руки.",
                "Солнце холодное, и его тепло — это иллюзия.",
                "Вода никогда не кипит, независимо от температуры.",
                "Снег всегда черного цвета.",
                "Облака состоят из пуха.",
                "Луна растет в размерах с каждым месяцем.",
                "Рыбы могут летать, если им дать крылья.",
                "Земля имеет три солнца.",
                "Камни умеют двигаться сами по себе.",
                "Деревья общаются через свои корни, передавая секретные сообщения.",
                "Люди могут вырастить руки из своей кожи.",
                "Горы могут спать, как люди.",
                "Книга способна разговаривать, если её открыть ночью.",
                "Земля плоская, и край её можно достичь пешком.",
                "Время может остановиться, если повернуть часы в обратную сторону.",
                "Кошки могут предсказывать будущее.",
                "Люди могут выжить, прожив без еды целых 10 лет.",
                "Каждый год Земля меняет своё положение в солнечной системе.",
                "Звезды появляются и исчезают мгновенно.",
                "Молоко можно использовать как лекарство от всех болезней.",
                "Птицы могут жить под водой, если они достаточно глубоко ныряют.",
                "Кошки могут плавать в воздухе.",
                "Люди не нуждаются в сне, чтобы оставаться здоровыми.",
                "Деревья могут бегать по лесу.",
                "Земля — это гигантский магнит, который притягивает все вещи к себе.",
                "Вулкан может извергнуть холодную лаву.",
                "Человеческий глаз способен видеть инфракрасное излучение.",
                "Каждый человек рождается с золотыми волосами.",
                "Планеты Земли и Марса меняются местами каждую ночь.",
                "Кошки умеют читать и писать.",
                "Сахар можно использовать для строительства домов.",
                "Вода имеет вкус шоколада.",
                "Люди могут менять свой возраст по желанию.",
                "Вода может гореть, если её правильно разогреть.",
                "Солнце утопает в океане каждую ночь.",
                "Облака могут петь, когда ветер дует.",
                "Луна излучает яркий зеленый свет.",
                "Метеоры могут превращаться в живых существ.",
                "Человек может прыгнуть до Луны.",
                "Земля имеет два центра гравитации.",
                "Все растения растут вниз ногами.",
                "Люди могут слышать мысли других людей без помощи технологий.",
                "Мозг человека состоит преимущественно из шоколада.",
                "Время можно измерить по длине волос на голове.",
                "Скорость света меняется в зависимости от настроения наблюдателя.",
                "Камни способны говорить на древних языках.",
                "Дети могут вырастить крылья, если они достаточно верят в чудеса.",
                "Человек может жить в космосе без скафандра.",
                "Птицы откладывают яйца из пластика.",
                "Океаны начинают свой ход по кругу каждую неделю.",
                "Северное сияние происходит из-за танца летающих медведей.",
                "Вода может замерзнуть при температуре 100 градусов Цельсия.",
                "Лед может плавать на воздухе.",
                "Молекулы состоят из маленьких планет.",
                "Солнце светит только по вечерам.",
                "Все реки текут в обратном направлении каждый год.",
                "Песок в пустынях состоит из измельченных звезд.",
                "Корабли могут плыть по небу, как по морю.",
                "Люди могут летать без каких-либо приспособлений, если сильно захотят.",
                "Земля периодически переворачивается и меняет полюса.",
                "Сердце человека может работать, если его перевернуть вверх ногами.",
                "Горы могут перемещаться с места на место, как облака.",
                "Земля не имеет атмосферы, а воздух является иллюзией."
            ]
        },
        "en": {
            "true": [
                "Cats are mammals.",
                "Dogs have four legs.",
                "Elephants are the largest land mammals.",
                "Most birds can fly.",
                "Some fish can change color.",
                "Trees have roots.",
                "Many plants use sunlight for photosynthesis.",
                "Some flowers have bright colors to attract insects.",
                "Most grasses grow in open fields.",
                "Leaves help plants produce energy.",
                "The Volga River is the longest in Europe.",
                "Moscow is the capital of Russia.",
                "Mountains often form natural barriers.",
                "Many cities are located along rivers.",
                "Oceans cover most of the Earth.",
                "Water consists of two hydrogen atoms and one oxygen atom.",
                "The Earth rotates on its axis.",
                "Light has a wave-like nature.",
                "Electricity is transmitted through wires.",
                "Gravity keeps planets in orbit.",
                "The Pyramid of Khufu is one of the ancient wonders.",
                "The Roman Empire greatly influenced Europe.",
                "The Great Wall of China was built over centuries.",
                "The Middle Ages were characterized by feudalism.",
                "The Renaissance brought many artistic achievements.",
                "The Northern Lights can be seen at high latitudes.",
                "The Moon is Earth's only natural satellite.",
                "The Sun is the center of our Solar System.",
                "An atom consists of protons, neutrons, and electrons.",
                "Molecules form when atoms bond together.",
                "Planetary orbits are elliptical.",
                "Volcanic activity reshapes landscapes.",
                "Meteorites fall to Earth from space.",
                "Antarctica is covered in ice.",
                "Deserts have extremely low humidity.",
                "Jungles are home to diverse species of plants and animals.",
                "Plains cover large areas of continents.",
                "Ocean currents influence Earth's climate.",
                "Many rivers flow into the oceans.",
                "The Earth's climate changes over time.",
                "Global warming is a result of climate change.",
                "Air is composed mainly of nitrogen and oxygen.",
                "Forestry is vital for ecosystems.",
                "Soil provides the foundation for plant growth.",
                "The biosphere includes all living organisms.",
                "Ecosystems rely on natural balance.",
                "Many species become endangered due to habitat loss.",
                "Nature reserves protect wildlife.",
                "Biodiversity is essential for ecosystem stability.",
                "Predators regulate prey populations.",
                "Many plants have medicinal properties.",
                "Herbs are used in traditional medicine.",
                "Fruits are rich in vitamins and minerals.",
                "Vegetables are an important part of the human diet.",
                "Grains play a key role in nutrition.",
                "Milk is a source of calcium.",
                "Eggs contain proteins and essential nutrients.",
                "Meat is a source of protein and iron.",
                "Fish are rich in omega-3 fatty acids.",
                "Seafood is part of a healthy diet.",
                "Birds build nests for their young.",
                "Some animals migrate long distances.",
                "Wild animals are adapted to life in nature.",
                "Mammals nurse their young with milk.",
                "Primates are highly intelligent.",
                "Bees play a crucial role in pollination.",
                "Ants are known for their organization.",
                "Some insects use bright colors for defense.",
                "Spiders weave webs to catch prey.",
                "Crustaceans live in both freshwater and saltwater.",
                "Many reptiles lay eggs.",
                "Amphibians live both in water and on land.",
                "Some fish can breathe air.",
                "Scorpions have venomous stingers.",
                "Jellyfish can be dangerous to humans.",
                "Some corals form vast reefs.",
                "Desert animals are adapted to extreme heat.",
                "Glaciers create unique landscapes.",
                "Landscapes vary from tundra to tropical forests.",
                "The Earth has abundant natural resources.",
                "Geologists study the Earth's crust.",
                "Many minerals are used in industry.",
                "Crystals exhibit symmetrical structures.",
                "Seismic activity can cause earthquakes.",
                "Population density varies widely.",
                "A country's economy depends on natural resources.",
                "Technology evolves rapidly each year.",
                "The internet has transformed communication.",
                "Mobile phones are integral to modern life.",
                "Social media influences public opinion.",
                "Many people use smartphones for work and leisure.",
                "Transportation systems are constantly improving.",
                "Rail transport is vital for logistics.",
                "Cars affect urban air quality.",
                "Airports facilitate international travel.",
                "Space exploration expands our understanding of the universe.",
                "Rocket technology enables satellite launches.",
                "Science continually pushes new frontiers.",
                "Education is key to societal development.",
                "Cultural heritage is vital for national identity."
                ],
        "false": [
            "The Sun revolves around the Earth.",
            "Water freezes at 50 degrees Celsius.",
            "The Moon is made of cheese.",
            "The human body can live without oxygen forever.",
            "Mountains grow taller every night.",
            "Penguins fly faster than airplanes.",
            "Dogs can talk if trained properly.",
            "Trees move slightly every spring.",
            "All oceans are filled with fresh water.",
            "Cats have eight legs.",
            "A person can survive a fall from 1000 meters without harm.",
            "Milk can be used as fuel for cars.",
            "Gravity on Mars is ten times stronger than on Earth.",
            "The Earth is cube-shaped.",
            "Antarctica is covered with sand instead of ice.",
            "Light can travel slower than sound.",
            "The human brain can store an infinite amount of information.",
            "Bees are nocturnal animals.",
            "The Sahara Desert is the coldest place on Earth.",
            "Oceans are made of milk.",
            "A human heart beats only once per hour.",
            "Humans can breathe underwater without special equipment.",
            "A volcano erupts frozen lava.",
            "Many plants grow faster when watered with soda.",
            "Dogs are born with the ability to fly.",
            "Light from stars reaches Earth in a few seconds.",
            "Time in space flows backward.",
            "All people have the same fingerprint.",
            "Fish can live on land without water.",
            "Paper can be used as food.",
            "Sugar dissolves in a vacuum.",
            "Metals can melt at room temperature if heated properly.",
            "Books can read themselves.",
            "Lightning never strikes the same place twice.",
            "The Earth rests on the backs of giant turtles.",
            "Dinosaurs still live in hidden parts of the Earth.",
            "Humans can hear ultrasonic sounds without special equipment.",
            "Steel can melt from a hand's touch.",
            "The Sun is cold, and its warmth is an illusion.",
            "Water never boils, regardless of temperature.",
            "Snow is always black.",
            "Clouds are made of fluff.",
            "The Moon grows in size every month.",
            "Fish can fly if given wings.",
            "The Earth has three suns.",
            "Rocks can move on their own.",
            "Trees communicate through their roots by transmitting secret messages.",
            "People can grow extra arms from their skin.",
            "Mountains can sleep like people.",
            "A book can talk if opened at night.",
            "The Earth is flat and its edge can be reached on foot.",
            "Time can stop if you turn the clocks backward.",
            "Cats can predict the future.",
            "People can survive without food for 10 years.",
            "Every year, the Earth changes its position in the solar system.",
            "Stars appear and disappear instantly.",
            "Milk can be used as a cure for all diseases.",
            "Birds can live underwater if they dive deep enough.",
            "Cats can swim in air.",
            "People do not need sleep to stay healthy.",
            "Trees can run through the forest.",
            "The Earth is a giant magnet that attracts everything.",
            "A volcano can erupt cold lava.",
            "The human eye can see infrared radiation.",
            "Every person is born with golden hair.",
            "Earth and Mars swap places every night.",
            "Cats can read and write.",
            "Sugar can be used to build houses.",
            "Water tastes like chocolate.",
            "People can change their age at will.",
            "Water can burn if heated properly.",
            "The Sun drowns in the ocean every night.",
            "Clouds can sing when the wind blows.",
            "The Moon emits a bright green light.",
            "Meteors can turn into living beings.",
            "A person can jump to the Moon.",
            "The Earth has two centers of gravity.",
            "All plants grow upside down.",
            "People can hear others' thoughts without technology.",
            "The human brain is mostly made of chocolate.",
            "Time can be measured by the length of hair on one's head.",
            "The speed of light changes depending on the observer's mood.",
            "Rocks are capable of speaking ancient languages.",
            "Children can grow wings if they believe in miracles.",
            "A person can live in space without a spacesuit.",
            "Birds lay eggs made of plastic.",
            "Oceans change their flow direction every week.",
            "The Northern Lights occur due to dancing flying bears.",
            "Water can freeze at 100 degrees Celsius.",
            "Ice can float in the air.",
            "Molecules are made up of tiny planets.",
            "The Sun only shines in the evenings.",
            "All rivers flow in the opposite direction every year.",
            "The sand in deserts is made from pulverized stars.",
            "Ships can sail through the sky as if on the sea.",
            "People can fly unaided if they really want to.",
            "The Earth periodically flips over and changes its poles.",
            "A human heart can function if turned upside down.",
            "Mountains can move from place to place like clouds.",
            "The Earth does not have an atmosphere, and air is an illusion."
        ]
            }
        }
}

