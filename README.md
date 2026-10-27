# СиАОД: лабораторные работы

Вариант **7**, seed **37** (`30 + номер варианта`).

## Лабораторная работа №1

Анализ временной сложности элементарных алгоритмов.

- [Код](lab01/lab01.py): сумма, максимум, равные пары и рекурсивное бинарное возведение в степень. Проверки, измерения и графики находятся в этом же файле.
- [Краткий отчёт в PDF](lab01/REPORT.pdf).
- [Исходные замеры](lab01/results/measurements.json), [окружение эксперимента](lab01/results/environment.json).
- [График log-log](lab01/results/lab01_loglog.png) и [график бинарной степени](lab01/results/lab01_binary_pow.png).
- [Источники и проверка опубликованной версии](SOURCES.md).

## Запуск

Python 3.10+. Команды выполняются из корня репозитория:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_data.py --variant 7 --only arrays
python lab01/lab01.py --variant 7 --out lab01/results-new
```

В Windows вместо `source` используйте `.venv\Scripts\activate`.
Сгенерированные данные не хранятся в Git. Новые измерения сохраняются отдельно,
чтобы не перезаписать результаты, на которых основан отчёт.

Только проверка алгоритмов, без длительных замеров:

```bash
python -c "from lab01.lab01 import self_check; self_check()"
```

Проверка оформления кода:

```bash
python -m pip install -r requirements-dev.txt
python -m black --check lab01/lab01.py
python -m ruff check lab01/lab01.py
```

Перед измерениями желательно подключить питание и закрыть тяжёлые фоновые
приложения. Выполняются прогрев, пять повторов и расчёт медианы; чтение данных
и построение графиков не входят в измеряемое время.

## Лабораторная работа №2

Рекурсия, динамический массив, стек и дек. Вариант **7**, seed **37**.

Короткая [демонстрация](lab02/demo.py) без данных и длительных замеров:

```bash
python lab02/demo.py
```

Показывает рекурсию, рост массива, LIFO, ошибки пустого стека, операции
с обоих концов дека и порядок FIFO при переносе между двумя стеками.

- [Основной код](lab02/lab02.py): факториал, Фибоначчи наивно и с мемоизацией,
  Ханойские башни, `DynamicArray`, `Stack`, `Deque`. В этом же файле находятся
  проверки, замеры и построение графиков из заготовки курса.
- [Краткий PDF-отчёт](lab02/REPORT.pdf): таблица вызовов, результаты измерений,
  анализ `append` методом учёта и выводы.
- [Исходные времена и хеши](lab02/results/measurements.json),
  [результаты проверки согласованности](lab02/results/verification.json).
- Графики: [append](lab02/results/lab02_append.png),
  [операции у начала](lab02/results/lab02_front.png).

Используется отдельная неизменённая версия
[генератора ЛР 2](lab02/generate_data.py) из текущей заготовки курса.
Она не заменяет генератор, по которому выполнялась первая лабораторная.

Из корня репозитория, после активации Python-окружения:

```bash
python lab02/generate_data.py --variant 7 --only ops --out data/generated-lab02
python lab02/lab02.py --variant 7 --data data/generated-lab02 --check-only
```

Новые измерения сохраняются отдельно от результатов отчёта:

```bash
python lab02/lab02.py --variant 7 --data data/generated-lab02 --out lab02/results-new
```

Повторная запись в каталог с `measurements.json` запрещена; выберите другой
`--out`, если этот каталог уже использовался. Графики требуют matplotlib.

Проверки работают и в оптимизированном режиме Python:

```bash
python -O lab02/lab02.py --variant 7 --data data/generated-lab02 --check-only
python -m black --check lab02/lab02.py
python -m ruff check lab02/lab02.py
```

Реализованы все обязательные структуры и рекурсивные функции КИМ-02.
`DynamicArray` растёт вдвое от начальной ёмкости 4, не использует методы
расширения встроенного списка для буфера и не сжимается при `pop`.
Стек использует только публичные методы массива; дек хранит узлы
двусвязного списка. Отрицательные индексы собственного массива запрещены.

Проверки охватывают все разделы заготовки, 100 000 операций стека,
100 000 операций дека и ещё 900 случайных сценариев. Все проверки
выполняются через явные исключения, а не отключаемые `assert`.
У рекурсивных функций есть обычный предел глубины стека Python;
`sys.setrecursionlimit` не меняется.

## Материалы курса

[Задание ЛР №1](https://github.com/mel0d1an/data-structures-and-algorithms/blob/main/M1-intro-and-basic-structures/kim-01-complexity-analysis.md),
[порядок сдачи](https://github.com/mel0d1an/data-structures-and-algorithms/blob/main/methodical-guidelines/students/README.md).
В репозитории размещаются код и отчёт; работа также требует устной защиты.

[Задание ЛР №2](https://github.com/mel0d1an/data-structures-and-algorithms/blob/main/M1-intro-and-basic-structures/kim-02-recursion-linear-structures.md).
