# re-rl

Библиотека для генерации математических и физических задач с пошаговыми решениями для обучения LLM навыкам reasoning (Chain-of-Thought).

## Особенности

- **961 типа задач**: 621 математических + 1 формальная (Lean 4) + 57 машинного обучения + 46 обучения с подкреплением + 236 физических
- **Визуальные (VLM) задачи**: 57 типов с генерацией изображений — графики функций, столбчатые/круговые/линейные диаграммы, гистограммы, диаграммы размаха, диаграммы рассеяния, числовая прямая, наклон прямой, диаграммы Венна, площадь по графику, графики движения (v–t и траектории), геометрия, выпуклая оболочка, аналоговые часы и ряд циферблатов, кости, столбцы блоков, счёты, цепочка домино, клетчатые квадраты, путь по сетке, шахматная доска, цветная сетка, взвешенные/ориентированные графы (кратчайший путь, MST, раскраска, топ-сортировка, макс. поток), диаграммы ДКА, схемы логических вентилей и резисторных цепей, чашечные весы и рычаг, «Сапёр», «Мастермайнд», ферзи, «Жизнь» Конвея, магический квадрат, лабиринт, P–V диаграммы, многоугольники, а также картиночные варианты судоку/пятнашек/ARC — картинка + текстовый ответ, плюс аугментации изображений. Превью каждого типа: [`examples/previews/README.md`](examples/previews/README.md)
- **Языки**: русский и английский
- **Система сложности**: 10 уровней для каждого типа задач
- **Пошаговые решения**: детальные цепочки рассуждений для SFT/RL обучения
- **Форматы экспорта**: JSON, JSONL, SFT-формат, Chat-формат, мультимодальный (`generate_vlm_dataset`)

## Быстрый старт

```bash
pip install -e .
```

### Генерация SFT датасета

```python
from re_rl.dataset_generator import DatasetGenerator

generator = DatasetGenerator()

# Генерация 10000 примеров для SFT
dataset = generator.generate_sft_dataset(
    task_types=["quadratic", "kinematics", "quantum", "circuits"],
    num_samples=10000,
    language="ru",
    difficulties=[3, 5, 7, 9],  # Средняя и высокая сложность
)

# Разделение на train/eval
train, eval = generator.split_dataset(dataset, train_ratio=0.9)

# Сохранение в JSONL (для transformers/trl)
generator.save_jsonl(train, "train.jsonl")
generator.save_jsonl(eval, "eval.jsonl")
```

### Формат SFT данных

```json
{
  "instruction": "Решите задачу пошагово, объясняя каждый шаг рассуждения.",
  "input": "Фотон с частотой 1e15 Гц падает на металл с работой выхода 2 эВ. Найдите кинетическую энергию фотоэлектрона.",
  "output": "Шаг 1: Уравнение Эйнштейна для фотоэффекта: hν = A + Eₖ\nE_фотона = hν = 6.626e-34 × 1e15 = 6.626e-19 Дж = 4.14 эВ\nEₖ = hν - A = 4.14 - 2.0 = 2.14 эВ\n\nОтвет: 2.14 эВ",
  "metadata": {"task_type": "quantum", "difficulty": 5, "language": "ru"}
}
```

### Chat-формат (для Llama/ChatML)

```python
chat_dataset = generator.generate_chat_dataset(
    task_types=["quadratic", "quantum"],
    num_samples=5000,
    language="ru"
)
# Формат: {"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}
```

## Улучшения каталога

Волна ниже закрывает конкретные дыры: формульные и переборные задачи уже были, а алгоритмов с однозначным следом и чтения новых диаграмм не хватало.

1. **stable_matching** — устойчивое паросочетание Гейла–Шепли и проверка блокирующей пары. Обычное паросочетание в двудольном графе уже есть, устойчивость предпочтений — нет.
2. **hamming_code** — код Хэмминга (7,4): кодовое слово, синдром единственной ошибки, расстояние Хэмминга. Рядом уже были дополнительный код и Хаффман, но не коды с исправлением ошибок.
3. **page_replacement** — число отказов страниц FIFO / LRU / OPT по трассе обращений.
4. **tree_queries** — диаметр, листья, высота и наименьший общий предок дерева. Графовые задачи покрывали пути и связность, но не запросы к дереву.
5. **os_scheduling** — суммарное ожидание SJF и FCFS и перемещение головки SSTF. Интервальное расписание уже было, планирование заявок и диска — нет.
6. **numerical_methods** — один шаг Ньютона, метод трапеций и левый конец отрезка после бисекции. Правило округления середины зафиксировано, ответ однозначен.
7. **min_coins** — минимум монет, в том числе когда жадный выбор крупного номинала ошибается. Число способов набрать сумму по-прежнему живёт в `dynamic_programming`.
8. **box_plot**, **number_line**, **slope_read**, **balance_scale** — диаграмма размаха (медиана, межквартильный размах, размах), целое на числовой прямой, наклон и пересечение с осью Oy, масса «?» на весах и на рычаге. Числа только на рисунке.

Вторая волна считает ответ точно, без допуска на округление:

9. **lagrange_interpolation** — значение многочлена Лагранжа в целой точке. Узлы сняты с многочлена с целыми коэффициентами, формула на дробях совпадает с прямой подстановкой.
10. **euler_method** — один или несколько шагов метода Эйлера для y' = px + qy + r при h = 1. Все узлы целые.
11. **fractional_knapsack** — дробный рюкзак. Удельные стоимости — различные целые, поэтому и разрезанный предмет даёт целую стоимость.
12. **union_find** — число компонент, «в одной ли компоненте» и размер компоненты после серии объединений.
13. **direct_mapped_cache** — попадания, промахи и tag в кэше прямого отображения.
14. **knight_moves** — минимум ходов коня по пустой доске 8×8.
15. **adiabatic** — конечные T, P или V обратимой адиабаты. Объёмы — степени двойки, сокращающиеся с γ = 5/3 или 7/5.
16. **ballistic_pendulum** — скорость после неупругого удара, высота подъёма и скорость пули при g = 10. Импульс и V^2 = 2gh сходятся на целых.

Отдельный раздел — база машинного обучения. Логарифмы энтропии берутся только на степенях двойки, критерий расщепления — Джини (точная дробь), остальные ответы тоже целые или несократимые дроби: `shannon_entropy`, `gini_split`, `knn_classify`, `perceptron_update`, `kmeans_step`, `naive_bayes`, `confusion_metrics`, `gradient_step`, `ranking_auc`, `hinge_loss`, `cosine_rank`, `univariate_regression`, `decision_stump`, `brier_score`, `mse_loss`, `precision_at_k`, `cohen_kappa`, `r2_score`, `mean_average_precision`, `mae_loss`, `jaccard_index`, `reciprocal_rank`, `kalman_update`, `hmm_decode`, `elimination_query`, `pagerank`.

Дальше по всем направлениям, тоже с точным ответом и шкалой сложности: `catalan`, `stirling_second`, `gray_code`, `binary_search`, `matrix_chain`, `common_substring`, `solid_volume`, `round_robin`, `deadlock`, `second_price`, `shapley_value`, `internal_resistance`, `restitution`, `meeting_motion`, `lc_oscillator`, `stellar_parallax`.

Для претрейна, SFT и RL отдельно считаются отдача, Q-learning и шаг Беллмана, а также классическая динамика: `discounted_return`, `q_learning`, `bellman_backup`, `max_subarray`, `house_robber`, `rod_cutting`, `pair_sum`, `heap_array`, `weighted_interval`, `half_life_steps`, `fourier_conduction`, `spring_energy`.

Следующий слой: `sarsa`, `epsilon_greedy`, `policy_expectation`, `min_path_sum`, `stock_profit`, `jump_game`, `container_water`, `decode_ways`, `gas_station`, `pendulum_ratio`, `mechanical_efficiency`, `relative_velocity`.

Ещё один слой вне графов: отдача с выбранного шага, Double Q-learning и мягкое обновление весов, формула Пика, удержанная вода, элемент большинства и алгоритм Евклида, а также волна, нагрев без фазового перехода и пара резисторов: `reward_to_go`, `double_q`, `polyak_update`, `pick_theorem`, `trapping_rain`, `majority_element`, `euclid_gcd`, `wave_relation`, `sensible_heat`, `resistor_pair`.

Дальше: след затухания, Expected SARSA и GAE, среднеквадратичная ошибка и точность на топ-k, задача Иосифа, прямоугольник в гистограмме, расстановки знаков и последовательность Коллатца, приведённая масса, циклотронная частота и красное смещение: `eligibility_trace`, `expected_sarsa`, `gae_advantage`, `mse_loss`, `precision_at_k`, `josephus`, `histogram_area`, `target_sum`, `collatz_steps`, `reduced_mass`, `cyclotron`, `spectral_redshift`.

Ещё слой: обрезка PPO, произведение отношений важности и дифференциальная ошибка средней награды, каппа Коэна, коэффициент детерминации и средняя точность, прибыль при многих сделках, минимум квадратов и палиндромная подпоследовательность, рациональный фактор Лоренца, отношение светимостей и энергия катушки: `ppo_clip`, `importance_ratio`, `average_reward`, `cohen_kappa`, `r2_score`, `mean_average_precision`, `stock_unlimited`, `min_squares`, `palindrome_subseq`, `rational_gamma`, `stefan_ratio`, `inductor_energy`.

Следующий слой: один шаг V-trace, вероятность приоритетного семплирования и отдача после обрезки наград, средняя абсолютная ошибка, индекс Жаккара и обратный ранг, число подмассивов с заданной суммой, целый квадратный корень и наибольшее произведение, а также целочисленный эффект Доплера, закон Хаббла и свободное падение: `vtrace`, `priority_replay`, `reward_clip`, `mae_loss`, `jaccard_index`, `reciprocal_rank`, `subarray_sum`, `integer_sqrt`, `max_product`, `doppler_shift`, `hubble_law`, `free_fall`.

Крупные многошаговые задачи: обратная индукция на горизонте, цепочка обновлений Q-learning, назначение работников, кратчайшие пути Флойда, выравнивание Нидлмана–Вунша, замены в массиве и сумма отрезка, несколько шагов фильтра Калмана и смешанное равновесие 2×2: `finite_horizon`, `q_trajectory`, `min_assignment`, `floyd_distance`, `sequence_alignment`, `range_query`, `kalman_update`, `mixed_nash`.

Ещё один слой длинных алгоритмов: траектория SARSA, expectimax и минимакс на явном дереве, Витерби и вероятность наблюдений, вывод в цепочке признаков, локальное выравнивание, укладка РНК и оптимальное дерево поиска: `sarsa_trajectory`, `expectimax`, `minimax_tree`, `hmm_decode`, `elimination_query`, `local_alignment`, `nussinov`, `optimal_bst`.

Следом: альфа-бета отсечение, произведение многочленов, прибавления на отрезке, независимое множество дерева, число вхождений подпоследовательности, секрет Шамира, точный PageRank и серия обновлений Double Q-learning: `alpha_beta`, `polynomial_product`, `range_add`, `tree_mis`, `subsequence_count`, `secret_share`, `pagerank`, `double_q_trajectory`.

Целые модели на SymPy и SciPy. Две схемы осциллятора сравниваются по энергии, регулятор сдвигает место на целую половину силы, толчок меняет скорость осциллятора, два сосуда обмениваются целой половиной разности, доза снимает целую половину уровня, кольцо заменяет ячейку суммой соседей, три возраста обновляются одновременно, ротатор испускает разность энергий соседних уровней: `energy_drift`, `pid_track`, `drive_osc`, `two_tank`, `dose_decay`, `wrap_ring`, `age_flow`, `rotor_drop`.

Задачи, где привычный короткий вывод ошибается. Сумма перевесов групп и перевес после сложения считаются разными произведениями. Запас работы — это поздний срок минус ранний, а не длительность. Победитель всех пар может отсутствовать при цикле. Положительные тесты больных и здоровых считаются отдельно, целыми долями. Коэффициенты сгорания зависят от чётности водорода. Индекс цитирований — позиция в убывающем ряду, а не среднее. Аллели ребёнка возможны только если каждый родитель может отдать один из них. Точка вытесняет другую только при нехудшей плате, нехудшем качестве и строгой разнице: `simpson_pool`, `job_slack`, `pair_vote`, `screen_count`, `burn_balance`, `h_index`, `allele_fit`, `pareto_keep`.

Группы и кольца с точным следом. Порядок подстановки — наименьшее общее кратное длин циклов. Сопряжение переводит сигма(x) в сигма(тау(x)). В кольце вычетов шаг прибавления обходит циклическую подгруппу, единицы — остатки, взаимно простые с модулем, а нильпотентный элемент доводится до нуля степенями. Многочлены умножаются над простым полем. Тройки Гейзенберга умножаются с перекрёстным членом. Смежный класс циклической подгруппы заменяется наименьшим представителем: `perm_order`, `perm_conj`, `add_orbit`, `unit_mod`, `nil_index`, `mod_poly`, `heisen_mul`, `coset_rep`.

Квантовые цепочки с целым ответом. У частицы в яме энергия уровня — квадрат номера, а дипольный переход меняет номер на нечётное число. У осциллятора разрешён только соседний уровень. У колебательно-вращательной линии v меняется на 1 и J на 1, энергия равна 2v+1+J(J+1). Зеемановская компонента меняет магнитное число на -1, 0 или 1 внутри своего l. Четвёрка n, l, m, s проверяется обычными неравенствами. Подоболочки заполняются по Паули и Хунду. Уровень водорода без спина вмещает n*n состояний. Амплитуды путей складываются до возведения в квадрат. Электрон Франка–Герца теряет энергию равными квантами. Удвоенный порядок связи — связывающие электроны минус разрыхляющие: `box_jump`, `ho_jump`, `rovib_line`, `zeeman_line`, `qnum_ok`, `shell_fill`, `level_deg`, `path_amp`, `franck_hertz`, `bond_order`.

Дискретное уравнение Шрёдингера в единицах ħ²/2m = 1 и шага сетки 1. Стрельба строит волну из стационарного уравнения и смотрит, обнуляется ли правый край. Среднее значение гамильтониана считается отдельно от нормы. Невязка — действие гамильтониана минус пробная энергия на функцию. Кинетическая часть отделена от потенциальной. Явный шаг временного уравнения обновляет действительную и мнимую части и не сохраняет норму. Ток вероятности берётся с соседней пары узлов. Две пробные функции сравниваются произведением числителя на чужую норму: `shoot_psi`, `expect_h`, `sch_defect`, `split_energy`, `tdse_step`, `prob_flow`, `trial_gap`.

Симуляции, в которых ответ зависит от интерференции или от поиска спектра. Квантовое блуждание на прямой сдвигает правую и левую амплитуды после монеты. Цепочка делителей и смен знака считает порты интерферометра. Стрельба по нескольким энергиям отмечает стационарные значения по нулю или смене знака края. Понижение момента умножает вес на (j+m)(j-m+1). Степенной метод (8I-H) с сокращением на общий делитель приближает основное состояние ямы. Спины 1/2 добавляются по одному, и число способов получить проекцию пересчитывается: `qwalk_line`, `mz_port`, `bound_sign`, `ladder_down`, `ground_iter`, `spin_add`.

Частичный след двух частиц, волна энергии 2 сквозь барьер, вторая поправка к уровню ямы, схема Йи с энергией полушага, скачок Ренкина–Гюгонио при показателе 5/3 и числа Бетти по модулю 2: `reduce_rho`, `barrier_amp`, `perturb_sum`, `yee_line`, `shock_jump`, `betti_mod`.

Эллиптическая кривая складывает точку с собой хордой и касательной. Инвариантные множители собираются при добавлении циклических групп. Положительная бинарная форма приводится к неравенству |b| <= a <= c. Результант пары многочленов считается алгоритмом Евклида. Цепочка Штурма считает различные вещественные корни на полуинтервале. Алгебраическая нормальная форма булевой функции получается преобразованием Мёбиуса по модулю 2: `curve_add`, `smith_inv`, `form_reduce`, `res_chain`, `sturm_root`, `anf_fold`.

Ожидание бросков до двоичного слова складывается из степеней двойки по совпадениям конца и начала. Среднее время равной игры до 0 или цели собирается разностями, которые убывают на 2. Разные веса успеха дают целое распределение числа успехов. Повторный тест оставляет только положительных, умножая оба числа на делитель, если они на него не делятся. Сумма квадратов распадается на внутригрупповую и межгрупповую. Среднее число сравнений случайной сортировки считается рекуррентно и сокращается: `coin_wait`, `ruin_time`, `mix_count`, `repeat_test`, `group_var`, `pivot_cost`.

Идеальный газ проходит несколько изотерм, изобар и изохор, и P V / T не меняется. В трубе переменного сечения скорость равна расходу, делённому на площадь, а давление находится из постоянной суммы давления, квадрата скорости и удвоенной высоты. Неявный шаг остывания берёт наклон в новой температуре и не перескакивает комнату. Неявная теплопроводность трёх ячеек сохраняет сумму отклонений и не увеличивает сумму квадратов: `gas_path`, `pipe_flow`, `stiff_cool`, `heat_back`.

Упругий удар по покоящемуся телу передаёт ему скорость 2 m1 u / (m1 + m2), и это тело бьёт следующее. На изобаре работа равна P ΔV, на изохоре она нулевая, а тепло равно изменению внутренней энергии плюс работа. У тонкой линзы расстояние до действительного изображения равно u f / (u - f), и следующая линза стоит уже за этим изображением: `knock_line`, `first_heat`, `focus_row`.

Адиабата одноатомного газа с показателем 5/3 меняет объём в k в кубе, температуру в k в квадрате и давление в k в пятой степени. Центр масс после каждого тела — сокращённая дробь момента и массы. Теорема Штейнера добавляет к собственному моменту массу на квадрат расстояния. Определитель трёхдиагональной матрицы считается рекуррентно по главным минорам: `adiab_row`, `com_frac`, `axis_add`, `tri_det`.

Неупругий удар слипает тела: импульс сохраняется, а удвоенная кинетическая энергия убывает. Пустой конденсатор, подключённый параллельно, оставляет заряд прежним и уменьшает удвоенную энергию. Кулоновский вклад источника в нуле равен минус пробный заряд на Q на знак координаты, делённый на её квадрат: `stick_line`, `cap_spark`, `line_force`.

Квадрат периода круговой орбиты равен кубу радиуса: шаг с целым k умножает радиус на k в квадрате и период на k в кубе. Потенциал источника на отрезке с нулевыми концами линеен по обе стороны, а лапласиан равен нулю везде, кроме источника. При распаде импульс остатка равен старому импульсу минус импульс осколка, а удвоенная кинетическая энергия растёт: `kepler_row`, `path_green`, `burst_split`.

Числитель ковариации пары равен N на сумму произведений минус произведение сумм, а разность числителей дисперсий суммы и слагаемых равна его удвоению. Дефект независимости таблицы 2×2 равен N на клетку 1 1 минус произведение маргиналов. Свёртка двух дискретных законов прибавляет атомы второй величины к первой: масса перемножается, ненормированное среднее складывается: `cov_pair`, `indep_gap`, `sum_conv`.

Восстановление считает, сколько промежутков уложилось в горизонт, и возраст как горизонт минус их сумму. Ветвящийся процесс читает список потомков: поколение забирает столько чисел, сколько в нём особей, а нулевая сумма — вымирание. Гипергеометрическое число способов — произведение двух биномиальных коэффициентов, каждый делится нацело на шаге: `renew_age`, `birth_line`, `hyper_ways`.

Левый интеграл прибавляет позицию до приращения, и квадрат позиции равен удвоенному интегралу, сложенному с суммой квадратов приращений. Для шагов 1 и минус 1 модуль позиции равен модулю старта плюс интеграл знака плюс число шагов из нуля. У двух блужданий ковариация есть сумма произведений приращений, площадь — сумма левых косых произведений, а приращение произведения равно двум левым интегралам плюс ковариация. Стохастическая экспонента умножает уровень на единицу плюс скачок. На биномиальном дереве значение узла — максимум из платежа, умноженного на степень четырёх, и суммы потомков. Ожидание в очереди равно свободной сумме минус её минимум: `ito_left`, `tanaka_walk`, `parts_walk`, `expo_mart`, `snell_put`, `lindley_row`.

Целочисленное исключение Гаусса делит элемент столбца на опорный и вычитает кратную строку: определитель равен произведению опорных. Алгоритм Барейса пересчитывает нижний блок минором два на два и делит нацело на предыдущий ведущий минор. Степень матрицы 2 на 2 и её след удовлетворяют одной рекуррентности со следом и определителем. Квадрат площади двух векторов равен произведению сумм квадратов минус квадрат скалярного произведения. Элемент кронекерова произведения собирается по битам индексов, а его след — произведение следов множителей: `lu_exact`, `bareiss_det`, `cayley_vec`, `gram_area`, `kron_entry`.

Усечённая экспонента матрицы 2 на 2 домножается на факториал степени: следующий член равен матрице на предыдущий, делённый нацело на номер степени. Чётные степени со знаком плюс или минус собирают косинус, нечётные — синус. Геометрическая сумма копит степени матрицы, и единичная минус матрица, умноженная на сумму, равна единичной минус следующему члену: `matexp_row`, `matcos_row`, `neumann_row`.

Схема Горнера умножает накопитель на матрицу и прибавляет коэффициент к диагонали. Грамиан достижимости на шаге заменяется на A W A^T плюс внешний квадрат входа. Перманент трёхдиагональной матрицы прибавляет произведение уступа, а не вычитает его. Произведение цепочки матриц умножается справа, и определитель перемножается. Метод Леверье делит след на номер шага и получает коэффициенты характеристического многочлена. Логарифм единицы плюс строго верхняя треугольная матрица — конечный ряд со знаками и общим знаменателем: `mat_horner`, `reach_gram`, `tri_perm`, `mat_prod`, `leverrier`, `nil_log`.

## Типы задач

Полный перечень с примером условия и ответа открывается страницей [`examples/catalog.html`](examples/catalog.html). Ноутбук [`examples/Каталог_всех_задач.ipynb`](examples/Каталог_всех_задач.ipynb) собирает тот же реестр в Jupyter. Превью каждой визуальной задачи — [`examples/previews/README.md`](examples/previews/README.md). Таблицы ниже держат формулировку вопроса; счётчики в заголовках совпадают с реестром.

### Математика (621 типов)

| Категория | Задачи |
|-----------|--------|
| **Алгебра** | linear, quadratic, cubic, system_linear, exponential, logarithmic, inequality, symbolic_simplification, polynomial_factorization, vieta, fraction_ops, horner_eval, poly_div, sturm_root, res_chain |
| **Анализ** | calculus, limits, integral, differential_equation, series, optimization, taylor_series, partial_fractions, partial_derivatives, area_between_curves, lhopital, symbolic_regression, numerical_methods, lagrange_interpolation, euler_method, difference_table |
| **Геометрия** | geometry, trigonometry, vector_3d, coordinate_geometry, shoelace_area, triangle_solving, conic_sections, solid_volume, pick_theorem, clock_hands, grid_diagonal, manhattan_paths, polygon_angles, shadow_height, triangle_sides |
| **Линейная алгебра** | matrix, complex_number, matrix_reasoning, gaussian_elimination, matrix_multiplication, gram_schmidt, least_squares, roots_of_unity, tri_det, lu_exact, bareiss_det, cayley_vec, gram_area, kron_entry, matexp_row, matcos_row, neumann_row, mat_horner, reach_gram, tri_perm, mat_prod, leverrier, nil_log |
| **Дискретная математика** | number_theory, combinatorics, sequence, set_logic, graph, dynamic_programming, base_conversion, modular_arithmetic, recurrence, prime_factorization, diophantine, modular_inverse, continued_fraction, generating_function, catalan, stirling_second, gray_code, euclid_gcd, josephus, collatz_steps, min_squares, integer_sqrt, secret_share, bit_count, carry_add, cf_expand, combinatorial_optimization, crt_chain, digital_root, divisor_sum, door_toggles, extended_euclid, frobenius_coin, gcd_chain, graph_justification, greedy_coins, mod_chain, nim_sum, odd_sum, pascal_row, recurrence_walk, sandpile_path, walk_range, h_index, form_reduce |
| **Цепочки** | stern_path, partition_count, derange_count, gauss_mul, perm_compose, cover_span, reverse_add, stream_median, totient_row, coprime_count, digit_div, tree_depth, sign_walk, perm_rank, lcm_rise, zigzag_row, record_highs, sum_kinds, fib_word, mode_track, look_say, zeckendorf, roman_value, digit_stream, deque_trace, dragon_fold, permanent, bead_count, negabase, ulam_walk, luhn_sum, kaprekar_step, morton_code, stock_span, candy_row, digit_fact, recaman, xor_basis, palindrome_radius, squarefree_row, fenwick_sum, sparse_min, z_array, selection_swaps, rho_cycle, tree_times, dutch_flag, window_distinct, stable_place, naive_find, budget_take, skip_op, retry_goal, signal_edges, plan_gate, tool_pick, diff_count, cell_patch, pred_scan, rate_limit, lateness, switch_flip, turn_signs, first_fit, plurality, floor_run, saturate_count, undo_reg, cover_point, next_fit, scope_lookup, lock_log, path_toll, backoff_wait, priority_run, inbox_take, goal_match, craft_need, checkpoint_roll, schema_check, infix_value, ballot_walk, digit_root, crt_lift, mod_order, first_repeat, coupon_cover, coin_weigh, two_color, lattice_sum, horner_mod, rational_root, geom_sum, cyclo_eval, chebyshev_row, hermite_row, series_conv, transport_cost, pochhammer, binom_build, farey_next, mobius_sum, involution_count, jacobi_row, ruler_sum, thue_count, aliquot_walk, carmichael_row, cayley_trees, factoradic, stirling_first, bell_row, andre_row, bernoulli_den, chebyshev_u, sigma_row, prime_omega, motzkin_row, primorial, rgs_rank, bernoulli_numer, genocchi_row, kronecker_row, hook_length, legendre_frac, laguerre_frac, harmonic_frac, eulerian_row, fubini_row, delannoy_row, tau_row, prime_nu, sopfr_row, pell_row, tribonacci_row, narayana_row, schroder_row, gaussian_bin, kolakoski, cantor_pair, horn_fire, carry_row, lamp_trio, parity_sheet, mux_index, jury_veto, gate_fold, exactly_one, knave_next, priority_bit, interval_merge, cycle_count, stack_perm, inversion_row, run_length, median_merge, diag_cross, billiard_cross, popcount_sum, rencontres_row, ballot_tri, dedekind_psi, jordan_tot, sylvester_row, lucas_row, liouville_row, necklace_count, hamming_smooth, menage_count, bracket_final, unit_prop, gf2_solve, resolve_proof, bool_eq, assign_check, pigeon_place, kripke_box, all_are, literal_clash, until_line, dung_ground, causal_do, lukas_fold, doctrinal, knows_line, rough_set, naf_fire, agenda_vote, short_circuit, ref_count, wrap_index, bit_prog, break_sum, bounds_step, reg_swap, elif_pick, post_inc, min_hold, jump_add, div_chain, clamp_add, ptr_walk, continue_sum, delay_line, switch_case, digit_scan, rot_nibble, buf_len, cmp_branch, bit_set, cell_write, lcg_step, two_stack, sorted_insert, brace_pair, hash_probe, part_count, fill_forward, xor_fold, bubble_pass, mtf_list, turnstile, hamming_step, row_major, union_count, trie_node, minute_add, mod_accum, nfa_run, moore_run, sync_run, meet_run, lfsr_run, crc_rem, feistel_run, elgamal_enc, fact_base, cas_cell, memo_call, skip_fit, handoff_ask, reject_add, ref_resolve, belief_vote, join_wait, audit_sum, draw_out, die_build, rank_stop, day_clash, group_mean, safe_bits, first_to, odds_mass, borda_count, bound_scan, bracket_scan, claim_count, codon_scan, cooldown_schedule, corridor_keys, domino_chain, dose_schedule, fifo_cost, hat_line, johnson_span, lights_path, line_infection, melody_walk, next_greater, pancake_trace, portal_walk, quorum_rise, rally_lead, reagent_chain, shift_add, tax_brackets, turtle_walk, two_pointer_merge, window_max, simpson_pool, job_slack, pair_vote, screen_count, burn_balance, h_index, allele_fit, pareto_keep, perm_order, perm_conj, add_orbit, unit_mod, nil_index, mod_poly, heisen_mul, coset_rep, betti_mod, curve_add, smith_inv, form_reduce, res_chain, sturm_root, anf_fold, coin_wait, ruin_time, mix_count, repeat_test, group_var, pivot_cost, tri_det, cov_pair, indep_gap, sum_conv, renew_age, birth_line, hyper_ways, ito_left, tanaka_walk, parts_walk, expo_mart, snell_put, lindley_row, lu_exact, bareiss_det, cayley_vec, gram_area, kron_entry, matexp_row, matcos_row, neumann_row, mat_horner, reach_gram, tri_perm, mat_prod, leverrier, nil_log |
| **Абстрактная алгебра** | group_theory, category_theory, perm_order, perm_conj, add_orbit, unit_mod, nil_index, mod_poly, heisen_mul, coset_rep, betti_mod, curve_add, smith_inv |
| **Теория вероятностей** | urn_probability, statistics, bayesian_reasoning, expected_value, markov_chain, conditional_probability, hypothesis_testing, draw_out, die_build, rank_stop, day_clash, group_mean, safe_bits, first_to, odds_mass, bayes_updates, dice_ways, markov_steps, polya_urn, sir_ticks, simpson_pool, screen_count, coin_wait, ruin_time, mix_count, repeat_test, group_var, pivot_cost, cov_pair, indep_gap, sum_conv, renew_age, birth_line, hyper_ways, ito_left, tanaka_walk, parts_walk, expo_mart, snell_put, lindley_row |
| **Прикладная** | financial_math, arithmetic, age_gap, crew_work, ledger_guard, map_scale, mix_chain, mixture_concentration, ratio_split, truck_trips, work_rates, burn_balance |
| **Логика и планирование** | contradiction, knights_knaves, futoshiki, analogical, text_stats, sudoku, zebra_puzzle, csp_reasoning, sat_smt_mini, propositional_logic, regex_dfa, find_the_error, cryptarithmetic, inequality_proof, river_crossing, tower_of_hanoi, water_jug, blocks_world, nim_game |
| **Ризонинг и дедукция** | graph_reasoning, ordering_puzzle, state_tracking, grid_navigation, interval_scheduling, set_reasoning, pattern_induction, syllogism, logical_entailment, boolean_circuit, mastermind, countdown_24, game_theory_optimal, family_tree, minesweeper_deduction, proof_cases_counterexample |
| **CSP-головоломки (сетки)** | n_queens, magic_square, skyscrapers, kenken, kakuro, nonogram, binary_puzzle, hitori, star_battle, battleship |
| **Графы и оптимизация** | weighted_shortest_path, topological_sort, graph_coloring, mst_weight, eulerian_path, hamiltonian_path, bipartite_matching, tsp, max_flow, dag_longest_path, knapsack, subset_sum, fractional_knapsack, dag_paths, shortest_path_count, triangle_girth, wiener_index, tree_radius, prufer_code, havel_hakimi, spanning_trees, topo_count, floyd_distance, tree_mis |
| **Формальная логика и вычисления** | truth_table, model_counting, three_sat, logical_equivalence, qbf, dfa_simulation, turing_machine, game_of_life, elementary_ca, rpn_eval, balanced_brackets, sorting_trace |
| **Дедукция и игры** | logic_grid, seating_circular, tournament, combinatorial_games, tic_tac_toe, mixed_nash, expectimax, minimax_tree, alpha_beta |
| **Пространственное мышление и прочее** | cube_net, dice_reasoning, rotation_reflection, paper_folding, cipher_decode, pigeonhole, monty_hall, allen_relations |
| **Продвинутый ризонинг** | arc_grid_induction, program_trace, sprague_grundy, natural_deduction, edit_distance, calendar_reasoning, word_ladder, cfg_membership |
| **Логика, вывод и алгоритмы** | datalog_inference, unification, lambda_calculus, resolution, lis_dp, kmp_matching, sliding_puzzle, algorithm_complexity, twos_complement, connect_four, graph_connectivity, huffman_coding, dfa_minimization, anf_fold |
| **Вычислительная геометрия** | computational_geometry (выпуклая оболочка, пересечение отрезков, точка в многоугольнике, ближайшая пара) |
| **Алгоритмы, коды и системы** | stable_matching, hamming_code, page_replacement, tree_queries, os_scheduling, min_coins, union_find, direct_mapped_cache, knight_moves, binary_search, matrix_chain, common_substring, round_robin, deadlock, second_price, shapley_value, max_subarray, house_robber, rod_cutting, pair_sum, heap_array, weighted_interval, min_path_sum, stock_profit, jump_game, container_water, decode_ways, gas_station, trapping_rain, majority_element, histogram_area, target_sum, stock_unlimited, palindrome_subseq, subarray_sum, max_product, min_assignment, sequence_alignment, range_query, local_alignment, nussinov, optimal_bst, polynomial_product, range_add, subsequence_count |

### Машинное обучение (57 типов)

Считается точно: энтропия — только на кратностях-степенях двойки, расщепление — по Джини, дроби сравниваются как рациональные числа.

| Задача | Что спрашивается |
|---|---|
| `shannon_entropy` | энтропия в битах или какое из двух распределений её больше |
| `gini_split` | прирост Джини одного признака или какой из двух признаков лучше |
| `knn_classify` | класс запроса (манхэттен, нечётное k) или номер ближайшего соседа |
| `perceptron_update` | веса w1, w2, b после одного примера или прохода |
| `kmeans_step` | ближайший центроид, размер кластера или новая x-координата центроида |
| `naive_bayes` | класс запроса или условная вероятность со сглаживанием Лапласа |
| `confusion_metrics` | TP, precision, recall или F1 |
| `gradient_step` | градиент или вес после одного шага для y = w·x |
| `ranking_auc` | число согласованных пар или AUC |
| `hinge_loss` | суммарная шарнирная потеря или число ошибок |
| `cosine_rank` | какой вектор ближе по косинусу или скалярное произведение |
| `univariate_regression` | наклон или свободный член прямой МНК |
| `decision_stump` | минимум ошибок одномерного порога, включая постоянный классификатор |
| `brier_score` | средняя квадратичная ошибка вероятностного прогноза |
| `mse_loss` | среднеквадратичная ошибка регрессии или сумма квадратов |
| `precision_at_k` | число релевантных в топ-k или точность; при равенстве оценок левый объект выше |
| `cohen_kappa` | каппа Коэна или доля наблюдаемого согласия po |
| `r2_score` | коэффициент детерминации или сумма квадратов отклонений истины |
| `mean_average_precision` | средняя точность отсортированного списка или точность на последнем релевантном |
| `mae_loss` | средняя абсолютная ошибка или сумма модулей |
| `jaccard_index` | индекс Жаккара двух бинарных векторов или размер пересечения |
| `reciprocal_rank` | обратный ранг первого релевантного объекта или сам ранг |
| `kalman_update` | среднее или дисперсия после нескольких одномерных обновлений Калмана |
| `hmm_decode` | вероятность наблюдений или путь Витерби |
| `elimination_query` | маргинальная вероятность конца цепочки или апостериорная вероятность начала |
| `pagerank` | ранг вершины или вершина с наибольшим рангом при затухании 1/2 |
| `kmeans_rounds` | центры одномерного k-means после нескольких раундов |
| `boost_weights` | вес примера или сумма весов после раундов удвоения на ошибке |
| `momentum_sgd` | вес или скорость после цепочки импульса |
| `decision_list` | ответ первого сработавшего правила или его номер |
| `neighbor_vote` | метка большинства ближайших соседей или число смен метки |
| `sgd_online` | вес или сумма квадратов остатков после пошагового градиентного спуска |
| `grad_clip` | вес или число обрезанных градиентов |
| `weight_decay` | вес или сумма целочисленных затуханий |
| `early_stop` | лучшая потеря или эпоха, где терпение впервые исчерпано |
| `prototype_mean` | сумма класса или класс, ближайший к запросу |
| `roc_walk` | позиция первой положительной метки при обходе оценок или число отрицательных до неё |
| `ema_loss` | скользящее среднее потерь или его пик |
| `lr_decay` | вес после шагов с убывающим множителем или множитель в конце |
| `batch_grad` | вес после пакетов из двух примеров или градиент последнего пакета |
| `best_margin` | разность лучшего положительного и лучшего отрицательного счёта или сам положительный счёт |
| `ctc_collapse` | длина выхода после схлопывания повторов и пустышек или последняя выходная метка |
| `relu_chain` | выход последнего слоя или множитель начального значения; неположительный вход обнуляет множитель навсегда |
| `causal_pick` | ключ, выбранный на последней позиции среди уже виденных, или число взглядов назад |
| `triplet_gap` | число троек с запасом меньше 1 или наименьший запас |
| `beam_keep` | лучшая сумма луча ширины два или токен, добавленный к ней на последнем шаге |
| `draft_accept` | сколько позиций черновика принято до первого расхождения или номер этого расхождения |
| `class_margin` | число примеров с запасом верного класса меньше 1 или наименьший запас |
| `bin_tally` | верные ответы или ошибки внутри одной корзины счёта |
| `grad_accum` | вес после вычитания суммы каждой пары градиентов или сумма последней пары |
| `skip_add` | значение после вентилей остаточного прибавления или число открытых вентилей |
| `hard_attend` | сумма значений по наибольшему произведению запроса и ключа или последнее выбранное значение |
| `max_pool` | сумма максимумов неперекрывающихся пар или число побед левого числа |
| `adam_tick` | вес после шага по первому целому моменту или сам первый момент |
| `rnn_add` | скрытое состояние после прибавления входов с отсечением минуса или число обнулений |
| `margin_push` | счёт после шагов внутри запаса или число примеров, которые счёт не изменили |
| `template_lag` | номер лучшего наложения шаблона или его счёт |

### Обучение с подкреплением (46 типов)

γ и α — дроби, отдача и Q считаются точно.

| Задача | Что спрашивается |
|---|---|
| `discounted_return` | полная отдача, n-шаговая отдача с бутстрапом или преимущество G − V |
| `q_learning` | новая оценка Q или TD-ошибка одного обновления |
| `bellman_backup` | оптимальная оценка состояния или жадное действие |
| `sarsa` | новая Q или TD-ошибка, в цели стоит выбранное следующее действие |
| `epsilon_greedy` | номер действия по ε и одному случайному числу u |
| `policy_expectation` | оценка политики V или преимущество действия |
| `reward_to_go` | отдача начиная с выбранного шага траектории |
| `double_q` | действие по Q1 или цель r + γ Q2 этого действия |
| `polyak_update` | новая координата целевых весов или её приращение |
| `eligibility_trace` | координата накапливающегося следа после домножения на γλ и +1 |
| `expected_sarsa` | среднее Q при равномерной политике или цель r + γ * среднее |
| `gae_advantage` | одношаговая TD-ошибка или преимущество GAE с шага t |
| `ppo_clip` | обрезанное отношение вероятностей или суррогат PPO |
| `importance_ratio` | произведение пошаговых отношений или число шагов с большим числителем |
| `average_reward` | средняя награда или дифференциальная TD-ошибка |
| `vtrace` | обрезанное отношение ρ или цель одного шага V-trace |
| `priority_replay` | вероятность номера или номер наибольшего приоритета |
| `reward_clip` | обрезанная награда шага или отдача после обрезки |
| `finite_horizon` | оценка состояния или действие перед первым шагом конечного горизонта |
| `q_trajectory` | Q пары после серии обновлений или лучшее действие состояния |
| `sarsa_trajectory` | Q после серии обновлений SARSA, в цели стоит выбранное следующее действие |
| `double_q_trajectory` | Q одной из двух голов после серии обновлений или её лучшее действие |
| `policy_rollout` | сумма наград или конечное состояние при заданной политике |
| `td_table` | оценка состояния или сумма оценок после серии TD(0) |
| `trace_decay` | координата следа или сумма координат после серии визитов с делением на 2 |
| `actor_critic` | оценка состояния или предпочтительное действие после серии переходов |
| `ucb_bandit` | сумма наград или самая частая рука целочисленного выбора |
| `target_sync` | онлайн-оценка или целевая оценка после редких копий таблицы |
| `replay_fifo` | значение в ячейке буфера или число вытесненных записей |
| `shape_reward` | сумма сформированных наград или сумма потенциальных добавок |
| `eps_schedule` | число исследовательских шагов или действие на выбранном шаге |
| `online_base` | преимущество шага относительно среднего прошлых наград или среднее в конце |
| `td_clip` | сумма обрезанных TD-ошибок или число ошибок, которые обрезка изменила |
| `count_bonus` | сумма добавок за редкие визиты или сумма наград с добавками |
| `option_hold` | действие на такте при удержании опции или число тактов |
| `policy_eval` | оценка состояния после проходов фиксированной политики или сумма оценок |
| `hindsight_hit` | число попаданий в исходную цель или в последнее состояние после замены цели |
| `legal_greedy` | сумма номеров жадно выбранных разрешённых действий или выбор в последнем состоянии |
| `reward_machine` | сумма наград автомата с тремя фазами или фаза после последнего события |
| `episode_cut` | сумма наград до первого попадания в цель, включая этот шаг, или номер этого шага |
| `best_reply` | сумма наград игрока при поочерёдных лучших ответах или его последнее действие |
| `arm_rate` | какая из двух рук впереди по доле успехов или число успехов первой руки |
| `budget_step` | конечное место при платном шаге или число заблокированных действий |
| `done_boot` | сумма целей шага, где конец обнуляет следующее значение, или число таких концов |
| `greedy_gap` | сумма разрывов между двумя оценками действия или число нулевых разрывов |
| `switch_cost` | сумма наград минус плата за смену действия или число смен |

### Физика (236 типов)

| Категория | Задачи |
|-----------|--------|
| **Механика** | kinematics, dynamics, energy, momentum, projectile_motion, rotational_dynamics, center_of_mass, atwood_machine, inclined_plane, statics_equilibrium, circular_dynamics, rolling_motion, elasticity, terminal_velocity, elastic_chain, composite_inertia, ballistic_pendulum, restitution, meeting_motion, spring_energy, mechanical_efficiency, relative_velocity, reduced_mass, free_fall, knock_line, com_frac, axis_add, stick_line, burst_split |
| **Электричество и магнетизм** | circuits, electrostatics, capacitors, electromagnetic_induction, ac_circuits, rc_circuits, magnetism, magnetic_force, kirchhoff_laws, rl_circuits, gauss_law, transformer, wheatstone_bridge, internal_resistance, lc_oscillator, resistor_pair, cyclotron, inductor_energy, yee_line, cap_spark, line_force, path_green |
| **Термодинамика** | gas_laws, heat_transfer, thermodynamic_cycles, entropy, phase_transitions, kinetic_theory, thermal_expansion, blackbody_radiation, gas_work, mean_free_path, pv_cycle, calorimetry_mix, adiabatic, fourier_conduction, sensible_heat, stefan_ratio, shock_jump, gas_path, stiff_cool, heat_back, first_heat, adiab_row |
| **Волны, оптика и звук** | waves, optics, doppler_effect, interference, diffraction, polarization, standing_waves, sound_intensity, beats, abcd_optics, wave_relation, doppler_shift, focus_row |
| **Квантовая физика** | quantum, bohr_model, de_broglie, uncertainty_principle, radioactive_decay, radiation_pressure, pair_production, half_life_steps, box_jump, ho_jump, rovib_line, zeeman_line, qnum_ok, shell_fill, level_deg, path_amp, franck_hertz, bond_order, shoot_psi, expect_h, sch_defect, split_energy, tdse_step, prob_flow, trial_gap, qwalk_line, mz_port, bound_sign, ladder_down, ground_iter, spin_add, reduce_rho, barrier_amp, perturb_sum, yee_line, shock_jump |
| **Ядерная физика** | nuclear |
| **Теория относительности** | relativity, relativistic_energy, velocity_addition, rational_gamma |
| **Колебания** | oscillations, pendulum_ratio |
| **Гидростатика и гидродинамика** | fluids, surface_tension, pipe_flow |
| **Астрофизика** | astrophysics, stellar_parallax, spectral_redshift, hubble_law, kepler_row |
| **Измерения и анализ** | dimensional_analysis, error_propagation, unit_conversion |
| **Масштабируемые сети** | series_parallel_network (резисторы/конденсаторы/пружины/тепловые сопротивления) |
| **Цепочки механики** | motion_segments, slope_run, echo_bounce, fall_ticks, friction_slide, heat_mix, heat_rod, wave_row, leak_charge, resistor_ladder, doppler_chain, float_load, melt_heat, throw_ticks, impulse_run, beam_load, mass_shift, spring_join, optic_path, pulse_meet, cool_ticks, series_cap, column_pressure, cradle_hit, photon_eject, orbit_years, grating_order, wire_force, escape_speed, harmonic_nodes, snell_shift, heat_steps, hydraulic_lift, euler_drift, verlet_push, drag_coast, spring_pair, swing_map, poisson_row, hydro_line, force_work, rocket_burn, projectile_tick, lc_tick, polar_stack, upwind_row, branch_decay, ising_pass, flow_mix, box_scope, spike_cut, twin_box, peak_hold, crack_close, source_dist, slope_field, charge_run, heun_cool, log_growth, energy_drift, pid_track, drive_osc, two_tank, dose_decay, wrap_ring, age_flow, rotor_drop, average_speed, billiard_box, block_stack, boat_current, boost_chain, bounce_heights, cascade_tanks, charge_redistribute, decay_generations, density, drop_cross, echo_delay, gear_ratio, gear_train, hooke_law, joule_heat, lens_stack, lever_balance, mirror_glance, mobile_torque, network_reduce, relay_time, siding_counter, spring_series, sticking_chain, switch_net, ternary_balance, traffic_light, voltage_divider, weighing_trace, box_jump, ho_jump, rovib_line, zeeman_line, qnum_ok, shell_fill, level_deg, path_amp, franck_hertz, bond_order, shoot_psi, expect_h, sch_defect, split_energy, tdse_step, prob_flow, trial_gap, qwalk_line, mz_port, bound_sign, ladder_down, ground_iter, spin_add, reduce_rho, barrier_amp, perturb_sum, yee_line, shock_jump, gas_path, pipe_flow, stiff_cool, heat_back, knock_line, first_heat, focus_row, adiab_row, com_frac, axis_add, stick_line, cap_spark, line_force, kepler_row, path_green, burst_split |

### Визуальные (VLM) задачи

Мультимодальные задачи: изображение + вопрос → текстовый ответ (проверка `verify` без изменений). Реестр — `ALL_VISUAL_TASK_GENERATORS` (отдельно от текстового `ALL_TASK_GENERATORS`).

| Тип | Бэкенд | Подтипы |
|---|---|---|
| `function_plot_read` | matplotlib | count_roots, y_intercept |
| `bar_chart_read` | matplotlib | max_category, min_category, difference, total |
| `grid_color_count` | PIL | count_color, most_color |
| `geometry_figure` | matplotlib | right_triangle_area, perimeter, missing_angle |
| `line_plot_read` | matplotlib | value_at, max_x, num_increases |
| `pie_chart_read` | matplotlib | largest, smallest |
| `clock_read` | PIL | чтение времени по циферблату (Ч:ММ) |
| `dice_read` | PIL | sum, count_value |
| `chessboard_count` | PIL | total, on_dark, on_light |
| `sudoku_image` | PIL | судоку-картинка: число в выделенной клетке |
| `sliding_puzzle_image` | PIL | пятнашки-картинка: solvable, min_moves |
| `arc_grid_image` | PIL | ARC-индукция на цветных сетках |
| `shortest_path_image` | networkx | взвешенный граф: вес кратчайшего пути |
| `mst_image` | networkx | взвешенный граф: вес минимального остовного дерева |
| `dfa_image` | matplotlib | диаграмма ДКА: принимает ли строку |
| `boolean_circuit_image` | matplotlib | схема вентилей: evaluate, count |
| `minesweeper_image` | PIL | поле «Сапёра»: мина/безопасно |
| `queens_check_image` | PIL | ферзи на доске: корректна ли расстановка |
| `mastermind_image` | PIL | доска «Мастермайнда»: восстановить код |
| `pv_cycle_image` | matplotlib | P–V диаграмма: работа за цикл (площадь) |
| `shoelace_image` | matplotlib | многоугольник по вершинам: площадь |
| `venn_diagram` | matplotlib | диаграмма Венна: intersection, union, only_a, sym_diff |
| `area_read` | matplotlib | площадь по графику: under_curve, between_curves |
| `stats_histogram` | matplotlib | гистограмма: mode, median, range |
| `kinematics_graph` | matplotlib | график v(t): displacement, acceleration |
| `projectile_graph` | matplotlib | траектория-парабола: range, max_height |
| `graph_coloring_image` | networkx | граф: хроматическое число / k-раскрашиваемость |
| `topological_sort_image` | networkx | орграф: топ-порядок / наличие цикла |
| `max_flow_image` | networkx | сеть с пропускными: максимальный поток |
| `game_of_life_image` | PIL | «Жизнь» Конвея: поле через k шагов |
| `magic_square_image` | PIL | магический квадрат 3×3 с пропусками |
| `grid_navigation_image` | PIL | лабиринт: длина кратчайшего пути |
| `convex_hull_image` | matplotlib | точки на плоскости: число вершин выпуклой оболочки |
| `scatter_plot` | matplotlib | диаграмма рассеяния: характер связи (±/нет) |
| `circuit_resistance_image` | matplotlib | схема резисторов: эквивалентное сопротивление |
| `box_plot` | matplotlib | диаграмма размаха: медиана, межквартильный размах, размах |
| `number_line` | matplotlib | числовая прямая: значение точки, расстояние, середина |
| `slope_read` | matplotlib | прямая на сетке: наклон, пересечение с Oy |
| `balance_scale` | matplotlib | весы или рычаг: масса неизвестного груза |
| `mirror_fault` | PIL | сетка: число несимметричных пар или строк |
| `blob_count` | PIL | тёмные фигуры: число фигур или размер самой большой |
| `ink_spread` | PIL | краска от красной точки: достигнутые или недостигнутые клетки |
| `mirror_ray` | PIL | луч и два вида зеркал: число касаний или сторона выхода |
| `shape_match` | PIL | фигуры: сколько совпадает с образцом после поворота |
| `paint_order` | PIL | прямоугольники по слоям: покрытие или клетки первого цвета |
| `hanoi_disk` | PIL | башня на трёх стержнях: число ходов до правого стержня или диски уже на нём |
| `skyline_see` | PIL | здания слева направо: сколько видно или номер последнего видимого |
| `solid_block` | PIL | тёмная сетка: сторона наибольшего сплошного квадрата или число квадратов 2×2 |
| `edge_flip` | PIL | трёхцветная сетка: горизонтальные или вертикальные границы разных цветов |
| `arrow_turn` | PIL | ряд стрелок: число поворотов налево или направление последней |
| `nest_box` | PIL | рамки: число строгих вложений или число рамок, содержащих другую |
| `abacus_read` | PIL | счёты: число по чёрным косточкам или сумма цифр |
| `arrow_path` | PIL | ломаная на сетке: число шагов или число поворотов |
| `block_tower` | PIL | столбцы блоков: сумма высот или высота выбранного столбца |
| `clock_row` | PIL | ряд циферблатов: сумма часов или сумма минут |
| `domino_image` | PIL | цепочка костей: сумма очков или место разрыва стыка |
| `grid_squares` | PIL | клетчатый прямоугольник: число всех квадратов или число квадратов заданной стороны |

Дополнительно доступна лёгкая аугментация изображений `augment_image(img, seed=...)` (небольшой поворот на белом фоне) — верификация текстовая, поэтому корректность ответа не меняется.

```python
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS

task = ALL_VISUAL_TASK_GENERATORS["bar_chart_read"](language="ru", difficulty=6)
task.render_image().save("chart.png")   # PIL.Image
print(task.description, "→", task.final_answer)

# Мультимодальный датасет (PNG на диск + JSONL с путём и токеном <image>)
from re_rl.dataset_generator import DatasetGenerator
gen = DatasetGenerator(output_dir="datasets_vlm")
vlm = gen.generate_vlm_dataset(num_samples=100, language="ru", difficulties=[3, 5, 7])
gen.save_jsonl(vlm, "vlm.jsonl", validate=False)
```

Подробности и инлайн-картинки — в `examples/Визуальные_задачи.ipynb`.

## Примеры использования

### Генерация отдельных задач

```python
from re_rl.tasks.physics import QuantumTask, generate_random_physics_task
from re_rl.tasks import QuadraticTask

# Квантовая механика
task = QuantumTask(task_type="photoelectric", difficulty=5, language="ru")
task.solve()
print(task.description)
print(task.solution_steps)
print(task.final_answer)

# Случайная физическая задача
task = generate_random_physics_task(difficulty=7, language="en")
task.solve()
print(task.get_result())

# Квадратное уравнение
task = QuadraticTask(a=1, b=-5, c=6, language="ru")
result = task.get_result()
print(result["problem"])
print(result["solution_steps"])
print(result["final_answer"])
```

### Список всех задач

```python
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS

print("Математика:", list(ALL_TASK_GENERATORS.keys()))
print("Физика:", list(ALL_PHYSICS_TASK_GENERATORS.keys()))
```

### Физические константы

```python
from re_rl.tasks.physics import PHYSICS_CONSTANTS, get_constant

print(get_constant("c"))  # Скорость света: 299792458
print(get_constant("h"))  # Постоянная Планка: 6.62607015e-34
print(PHYSICS_CONSTANTS["G"])  # Гравитационная постоянная с описанием
```

## Использование для SFT обучения

### С Hugging Face transformers + trl

```python
from datasets import load_dataset
from trl import SFTTrainer

# Загрузка сгенерированного датасета
dataset = load_dataset("json", data_files={"train": "train.jsonl", "eval": "eval.jsonl"})

# Форматирование для SFT
def format_prompt(example):
    return f"""### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""

# Обучение
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    formatting_func=format_prompt,
    max_seq_length=2048,
)
trainer.train()
```

### С Axolotl

```yaml
# axolotl config
datasets:
  - path: train.jsonl
    type: alpaca
    
# Формат уже совместим с alpaca (instruction/input/output)
```

## Formal Math: Theorem Proving в Lean 4

Помимо текстовых задач, RE-RL воспроизводит pipeline генерации training data из формальных доказательств Lean 4 по подходу [LeanNavigator](https://arxiv.org/abs/2503.04772) (Yin & Gao, 2025) — BFS-обход графа состояний Mathlib4 через Pantograph с BERT+FAISS retrieval тактик. В общем реестре этому соответствует тип `lean_proof`.

### Два источника данных

| Источник | Описание | Скорость |
|----------|----------|----------|
| **Mathlib Extraction** | Готовые доказательства из traced Mathlib | Быстро (~100k pairs/мин) |
| **BFS LeanNavigator** | Новые альтернативные пути через BFS | Медленнее, но уникальные данные |

**Рекомендация**: комбинировать оба источника для максимального разнообразия.

### Быстрый старт

```bash
# 1. Трейсинг Mathlib4 (один раз, ~60 мин, результат кэшируется)
python scripts/fast_trace.py --version v4.26.0

# 2a. Извлечение готовых доказательств (быстро)
python examples/formal/extract_mathlib_proofs.py --min-proof-length 2 --max-theorems 50000

# 2b. BFS exploration (новые пути)
python examples/formal/run_bfs.py --max-theorems 100 --decompose-auto

# 3. (Опционально) Обучение BERT RAG для лучшего retrieval
python examples/formal/train_rag.py
```

### Jupyter Notebook (полный pipeline)

Интерактивный notebook с пошаговым объяснением:

```bash
cd examples/formal
jupyter notebook Formal_Math_Generation.ipynb
```

Подробная документация: [`re_rl/tasks/formal/README.md`](re_rl/tasks/formal/README.md) и [`examples/formal/README.md`](examples/formal/README.md)

## Структура проекта

```
re_rl/
├── tasks/
│   ├── math/              # Математические задачи (34 типа)
│   ├── physics/           # Физические задачи (18 типов)
│   └── formal/            # Formal Math — см. formal/README.md
│       ├── lean_navigator/    # Подход LeanNavigator (BFS + Pantograph + RAG)
│       │   ├── core.py            # BFS exploration + PantographDojo + TacticRAG
│       │   ├── rag_trainer.py     # Обучение BERT retriever (triplet loss)
│       │   └── ...
│       ├── lean_proof_task.py # Шаблонные задачи (без зависимостей)
│       └── ...
├── dataset_generator.py   # Генератор датасетов
├── environments/          # RL окружения
scripts/
└── fast_trace.py          # Трейсинг Mathlib4
examples/
├── formal/                    # ← Formal Math примеры и скрипты
│   ├── Formal_Math_Generation.ipynb  # Полный pipeline (notebook)
│   ├── extract_mathlib_proofs.py     # Извлечение из Mathlib
│   ├── run_bfs.py                    # BFS генерация (последовательный)
│   ├── run_bfs_parallel.py           # BFS генерация (Ray, параллельный)
│   └── train_rag.py                  # Обучение BERT RAG
├── Генерация_датасета.ipynb      # Генерация math/physics задач
└── test_all_tasks.py             # Тест всех 52 типов задач
```

## Подходит ли для SFT?

**Да!** Данные генерируются в формате, оптимальном для SFT обучения:

1. **Chain-of-Thought**: Каждая задача содержит пошаговое решение
2. **Стандартные форматы**: instruction/input/output (Alpaca), messages (ChatML)
3. **Контроль сложности**: 10 уровней для curriculum learning
4. **Двуязычность**: Можно обучать мультиязычные модели
5. **Верифицируемые ответы**: Все решения математически корректны

### Пример цепочки рассуждений

```
Задача: Найдите энергию связи ядра He-4 (A=4, Z=2).

Шаг 1: Eсв = Δm·c² = [Z·m_p + (A-Z)·m_n - M]·931.5 МэВ
Шаг 2: m_теор = 2×1.007276 + 2×1.008665 = 4.031882 а.е.м.
Шаг 3: Δm = 4.031882 - 4.002603 = 0.029279 а.е.м.
Шаг 4: Eсв = 0.029279 × 931.5 = 27.27 МэВ
Шаг 5: Eсв/A = 27.27/4 = 6.82 МэВ/нуклон

Ответ: Eсв = 27.27 МэВ (6.82 МэВ/нуклон)
```

## Тестирование и бенчмарки

### Быстрая проверка (все задачи)

```bash
# Запуск всех unit-тестов (~1 мин)
pytest tests/

# Тест всех 52 типов задач (math + physics)
python examples/test_all_tasks.py
```

### Formal Math бенчмарк (LeanNavigator)

Требует: `elan` (Lean toolchain), `pantograph`, `faiss-cpu`, `sentence-transformers`.

#### Установка и подготовка

```bash
# Установка Python-пакета
pip install -e .

# Трейсинг Mathlib4 (один раз, ~30-60 мин, результат кэшируется)
python scripts/fast_trace.py --version v4.26.0
```

#### Извлечение данных из Mathlib (быстрый способ)

Напрямую извлекает (state, tactic) пары из traced Mathlib — без BFS.

```bash
# Все теоремы с доказательствами ≥2 шагов
python examples/formal/extract_mathlib_proofs.py --min-proof-length 2

# Только определённый модуль
python examples/formal/extract_mathlib_proofs.py --module-prefix Mathlib.Algebra --max-theorems 10000

# SFT формат для обучения
python examples/formal/extract_mathlib_proofs.py --output-format sft
```

#### BFS Exploration (новые пути)

Генерирует альтернативные доказательства через BFS — данные, которых нет в Mathlib.

```bash
# Базовый запуск
python examples/formal/run_bfs.py --max-theorems 100 --decompose-auto

# С запретом автоматизаторов (для длинных путей)
python examples/formal/run_bfs.py --max-theorems 50 --no-auto --min-proof-length 3

# Параллельно (Ray, быстрее)
python examples/formal/run_bfs_parallel.py --workers 8 --max-theorems 500 --decompose-auto
```

#### Бенчмарк: Pretrained SBERT vs Обученный BERT

```bash
# Прогон 1: Pretrained SBERT
python examples/formal/run_bfs.py --seed 42 --max-theorems 50 --rag-model sbert

# Обучение BERT retriever
python examples/formal/train_rag.py

# Прогон 2: Обученный BERT (те же теоремы)
python examples/formal/run_bfs.py --seed 42 --max-theorems 50 --rag-model trained
```

Результаты сохраняются в `datasets/formal_math_data/`.

Подробная документация: [`re_rl/tasks/formal/README.md`](re_rl/tasks/formal/README.md) и [`examples/formal/README.md`](examples/formal/README.md)

## Лицензия

MIT License
