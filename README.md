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

## Материалы курса

[Задание ЛР №1](https://github.com/mel0d1an/data-structures-and-algorithms/blob/main/M1-intro-and-basic-structures/kim-01-complexity-analysis.md),
[порядок сдачи](https://github.com/mel0d1an/data-structures-and-algorithms/blob/main/methodical-guidelines/students/README.md).
В репозитории размещаются код и отчёт; работа также требует устной защиты.
