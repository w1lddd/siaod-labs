#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 2. Рекурсия, динамический массив, стек и дек. Вариант 7, seed 37.

Учебные реализации расположены в разделах 1-3. Загрузка, основные проверки,
методика замеров и графики адаптированы из заготовки курса mel0d1an.

Из корня личного репозитория:
    python lab02/generate_data.py --variant 7 --only ops --out data/generated-lab02
    python lab02/lab02.py --variant 7 --data data/generated-lab02

Проверки без замеров:
    python lab02/lab02.py --variant 7 --data data/generated-lab02 --check-only
"""

from __future__ import annotations

import argparse
import collections
import functools
import hashlib
import json
import math
import random
import statistics
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Параметры эксперимента
# ---------------------------------------------------------------------------

#: Размеры структуры для замера операций у начала (вставка и удаление).
FRONT_SIZES = (1_000, 3_000, 10_000, 30_000, 100_000)

#: Операций у начала в одном замере: одна операция слишком быстра для таймера.
FRONT_OPS = 1_000

#: n для таблицы числа вызовов наивной и мемоизированной рекурсии.
FIB_NS = (5, 10, 15, 20, 25, 30)

REPEATS = 5  # повторов на точку (берётся медиана)

# ---------------------------------------------------------------------------
# 1. Рекурсивные функции (счётчик вызовов — для сравнения наивной рекурсии
#    и мемоизации; результаты счётчика включаются в отчёт)
# ---------------------------------------------------------------------------


CALLS = {"fib_naive": 0, "fib_memo": 0}
TIMING_SAMPLES = {}


def _check_n(n: int) -> None:
    if not isinstance(n, int):
        raise TypeError("n должно быть целым числом")
    if n < 0:
        raise ValueError("n не может быть отрицательным")


def factorial(n: int) -> int:
    """n!: O(n) вызовов и O(n) памяти стека при единичной стоимости арифметики."""
    _check_n(n)
    if n == 0:
        return 1
    return n * factorial(n - 1)


def fib_naive(n: int) -> int:
    """Наивная рекурсия: экспоненциальное число вызовов, O(n) памяти стека."""
    _check_n(n)
    CALLS["fib_naive"] += 1
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n: int, memo: dict[int, int] | None = None) -> int:
    """Мемоизация: O(n) вызовов, O(n) записей кэша и глубина стека O(n)."""
    _check_n(n)
    CALLS["fib_memo"] += 1
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


def hanoi(
    n: int,
    src: str = "A",
    dst: str = "C",
    aux: str = "B",
    moves: list[tuple[str, str]] | None = None,
) -> int:
    """Переносит n дисков: 2**n - 1 ходов; при moves сохраняет сами ходы."""
    _check_n(n)
    if len({src, dst, aux}) != 3:
        raise ValueError("Нужны три разных стержня")
    if n == 0:
        return 0
    count = hanoi(n - 1, src, aux, dst, moves)
    if moves is not None:
        moves.append((src, dst))
    count += 1
    return count + hanoi(n - 1, aux, dst, src, moves)


class DynamicArray:
    """Буфер фиксированной длины; ёмкость удваивается только при заполнении."""

    INITIAL_CAPACITY = 4

    def __init__(self) -> None:
        self._capacity = self.INITIAL_CAPACITY
        self._size = 0
        self._buffer = [None] * self._capacity
        self.copies = 0

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    def _grow(self) -> None:
        new_capacity = self._capacity * 2
        new_buffer = [None] * new_capacity
        for i in range(self._size):
            new_buffer[i] = self._buffer[i]
        self.copies += self._size
        self._buffer = new_buffer
        self._capacity = new_capacity

    def append(self, x) -> None:
        if self._size == self._capacity:
            self._grow()
        self._buffer[self._size] = x
        self._size += 1

    def pop(self):
        if self._size == 0:
            raise IndexError("Массив пуст")
        self._size -= 1
        x = self._buffer[self._size]
        self._buffer[self._size] = None
        return x

    def get(self, index: int):
        if index < 0 or index >= self._size:
            raise IndexError("Индекс вне массива")
        return self._buffer[index]

    def set(self, index: int, x) -> None:
        if index < 0 or index >= self._size:
            raise IndexError("Индекс вне массива")
        self._buffer[index] = x


class Stack:
    """LIFO; использует только публичные методы DynamicArray."""

    def __init__(self) -> None:
        self._data = DynamicArray()

    def __len__(self) -> int:
        return len(self._data)

    def push(self, x) -> None:
        self._data.append(x)

    def pop(self):
        return self._data.pop()

    def peek(self):
        if len(self._data) == 0:
            raise IndexError("Стек пуст")
        return self._data.get(len(self._data) - 1)


class _Node:
    __slots__ = ("value", "prev", "next")

    def __init__(self, value, prev=None, next=None) -> None:
        self.value = value
        self.prev = prev
        self.next = next


class Deque:
    """Двусвязный список: операции на обоих концах O(1)."""

    def __init__(self) -> None:
        self._head = None
        self._tail = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def push_front(self, x) -> None:
        node = _Node(x, next=self._head)
        if self._head is None:
            self._tail = node
        else:
            self._head.prev = node
        self._head = node
        self._size += 1

    def push_back(self, x) -> None:
        node = _Node(x, prev=self._tail)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def pop_front(self):
        if self._head is None:
            raise IndexError("Дек пуст")
        node = self._head
        self._head = node.next
        if self._head is None:
            self._tail = None
        else:
            self._head.prev = None
        node.next = None
        self._size -= 1
        return node.value

    def pop_back(self):
        if self._tail is None:
            raise IndexError("Дек пуст")
        node = self._tail
        self._tail = node.prev
        if self._tail is None:
            self._head = None
        else:
            self._tail.next = None
        node.prev = None
        self._size -= 1
        return node.value


# ---------------------------------------------------------------------------
# 4. Данные варианта: поиск каталога и загрузка
# ---------------------------------------------------------------------------

Op = tuple[str, int | None]  # операция и её аргумент (None, если аргумента нет)


def find_data_dir(explicit: Path | None) -> Path:
    """Каталог с данными варианта: --data, либо data/generated рядом с работой."""
    if explicit is not None:
        if not explicit.is_dir():
            raise SystemExit(f"Каталог не найден: {explicit}")
        return explicit
    candidates = []
    for base in (Path.cwd(), Path(__file__).resolve().parent):
        for parent in (base, *base.parents):
            candidates.append(parent / "data" / "generated")
    for path in candidates:
        if path.is_dir():
            return path
    raise SystemExit(
        "Не найден каталог data/generated с данными варианта.\n"
        "Сгенерируйте данные из корня репозитория курса:\n"
        "    python scripts/generate_data.py --variant N --only ops\n"
        "или укажите каталог явно: --data <путь>"
    )


def check_variant(data_dir: Path, variant: int) -> None:
    """Сверить номер варианта с паспортом данных (manifest.json)."""
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Нет паспорта данных: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = manifest.get("variant")
    if actual != variant:
        raise SystemExit(
            f"Данные в {data_dir} сгенерированы для варианта {actual}, "
            f"а работа запущена с --variant {variant}.\n"
            f"Перегенерируйте данные: "
            f"python scripts/generate_data.py --variant {variant} --only ops"
        )
    if manifest.get("seed") != 30 + variant:
        raise SystemExit("Seed в паспорте не соответствует варианту")
    print(f"Данные варианта {variant} (seed={manifest.get('seed')}) из {data_dir}")


def read_data_lines(data_dir: Path, name: str) -> list[str]:
    """Строки файла данных варианта; при его отсутствии — подсказка, как создать."""
    path = data_dir / name
    if not path.is_file():
        raise SystemExit(
            f"Не найден файл данных: {path}\n"
            f"Сгенерируйте его: python scripts/generate_data.py "
            f"--variant <ваш вариант> --only ops"
        )
    return path.read_text(encoding="utf-8").splitlines()


def load_append_sizes(data_dir: Path) -> list[int]:
    """Размеры серий append из ops_append_sizes.txt."""
    return [int(line) for line in read_data_lines(data_dir, "ops_append_sizes.txt")]


def load_ops(data_dir: Path, kind: str) -> list[Op]:
    """Операции из ops_<kind>.txt (kind — stack или deque): «push 17», «pop», ..."""
    ops: list[Op] = []
    for line in read_data_lines(data_dir, f"ops_{kind}.txt"):
        name, *arg = line.split()
        ops.append((name, int(arg[0]) if arg else None))
    return ops


# ---------------------------------------------------------------------------
# 5. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def expect_index_error(call, what: str) -> None:
    """call() должен бросить IndexError."""
    try:
        call()
    except IndexError:
        return
    raise SelfCheckError(f"{what}: ожидался IndexError")


# Операции над структурой — словарь «имя операции из данных -> метод»;
# ключ "len" нужен для сверки размера. Эталоны — list и collections.deque.


def stack_methods(st: Stack) -> dict:
    return {"push": st.push, "pop": st.pop, "peek": st.peek, "len": st.__len__}


def list_stack_methods(a: list) -> dict:
    return {"push": a.append, "pop": a.pop, "peek": lambda: a[-1], "len": a.__len__}


def deque_methods(dq: Deque) -> dict:
    return {
        "push_front": dq.push_front,
        "push_back": dq.push_back,
        "pop_front": dq.pop_front,
        "pop_back": dq.pop_back,
        "len": dq.__len__,
    }


def std_deque_methods(d: collections.deque) -> dict:
    return {
        "push_front": d.appendleft,
        "push_back": d.append,
        "pop_front": d.popleft,
        "pop_back": d.pop,
        "len": d.__len__,
    }


def apply_op(methods: dict, op: str, arg: int | None):
    """Выполнить операцию; IndexError превращается в результат "IndexError"."""
    try:
        return methods[op]() if arg is None else methods[op](arg)
    except IndexError:
        return "IndexError"


def compare_with_reference(ops: list[Op], own: dict, ref: dict, label: str) -> None:
    """Выполнить ops над своей структурой и эталоном, сверяя результат и размер."""
    for i, (op, arg) in enumerate(ops, start=1):
        call = op if arg is None else f"{op} {arg}"
        got, expected = apply_op(own, op, arg), apply_op(ref, op, arg)
        expect(
            got == expected,
            f"{label}, операция №{i} ({call}): получено {got!r}, эталон {expected!r}",
        )
        expect(
            own["len"]() == ref["len"](),
            f"{label}, операция №{i} ({call}): len = {own['len']()}, эталон {ref['len']()}",
        )


def random_ops(
    rng: random.Random,
    pushes: tuple[str, ...],
    others: tuple[str, ...],
    count: int,
    max_size: int,
) -> list[Op]:
    """Случайная серия операций над маленькой структурой — с частыми опустошениями."""
    ops: list[Op] = []
    size = 0
    for _ in range(count):
        op = rng.choice(pushes + others)
        if op in pushes and size >= max_size:
            op = rng.choice(others)
        if op in pushes:
            ops.append((op, rng.randrange(100)))
            size += 1
        else:
            ops.append((op, None))
            size = max(0, size - op.startswith("pop"))
    return ops


def expected_capacity(size: int) -> int:
    """Ёмкость после size подряд идущих append в пустой массив (рост x2)."""
    cap = DynamicArray.INITIAL_CAPACITY
    while cap < size:
        cap *= 2
    return cap


def expected_copies(size: int) -> int:
    """Число копирований после size подряд идущих append в пустой массив."""
    copies, cap = 0, DynamicArray.INITIAL_CAPACITY
    while cap < size:
        copies += cap
        cap *= 2
    return copies


def check_recursion() -> None:
    """Факториал, числа Фибоначчи со счётчиками вызовов, ходы Ханойских башен."""
    for n in range(21):
        got = factorial(n)
        expect(
            got == math.factorial(n),
            f"factorial({n}) = {got}, ожидалось {math.factorial(n)}",
        )

    fib = [0, 1]
    while len(fib) <= 90:
        fib.append(fib[-1] + fib[-2])
    for n in range(21):
        got = fib_naive(n)
        expect(got == fib[n], f"fib_naive({n}) = {got}, ожидалось {fib[n]}")
    CALLS["fib_naive"] = 0
    fib_naive(20)
    expect(
        CALLS["fib_naive"] >= fib[20],
        f"fib_naive(20): число вызовов {CALLS['fib_naive']} — это не наивная рекурсия",
    )
    for n in (0, 1, 2, 10, 30, 90):
        CALLS["fib_memo"] = 0
        got = fib_memo(n)
        expect(got == fib[n], f"fib_memo({n}) = {got}, ожидалось {fib[n]}")
        expect(
            CALLS["fib_memo"] <= 2 * n + 1,
            f"fib_memo({n}): число вызовов {CALLS['fib_memo']}, а с мемоизацией оно "
            f"не больше 2n + 1 = {2 * n + 1} — memo не передаётся в рекурсию?",
        )

    for n, (src, dst, aux) in (
        (0, "ACB"),
        (1, "ACB"),
        (2, "ACB"),
        (3, "XZY"),
        (6, "ACB"),
        (7, "PQR"),
    ):
        where = f"hanoi({n}, {src!r}, {dst!r}, {aux!r})"
        moves: list[tuple[str, str]] = []
        count = hanoi(n, src, dst, aux, moves)
        expect(count == 2**n - 1, f"{where} вернул {count}, ожидалось {2 ** n - 1}")
        expect(
            len(moves) == count,
            f"{where}: записано ходов {len(moves)}, возвращено {count}",
        )
        towers = {src: list(range(n, 0, -1)), dst: [], aux: []}
        for k, move in enumerate(moves, start=1):
            expect(
                len(move) == 2
                and move[0] in towers
                and move[1] in towers
                and move[0] != move[1],
                f"{where}, ход {k}: {move!r} — не пара разных стержней из {src}, {dst}, {aux}",
            )
            frm, to = move
            expect(bool(towers[frm]), f"{where}, ход {k}: стержень {frm} пуст")
            disk = towers[frm].pop()
            top = towers[to][-1] if towers[to] else None
            expect(
                top is None or top > disk,
                f"{where}, ход {k}: диск {disk} кладётся на меньший диск {top}",
            )
            towers[to].append(disk)
        expect(
            towers[dst] == list(range(n, 0, -1)),
            f"{where}: после всех ходов на стержне {dst} лежит {towers[dst]}",
        )
        expect(
            hanoi(n, src, dst, aux) == count, f"{where} без moves вернул другое число"
        )


def check_dynamic_array() -> None:
    """Границы индексов, рост x2 (ёмкость и копирования), pop и допустимое сжатие."""
    initial = DynamicArray.INITIAL_CAPACITY
    arr = DynamicArray()
    expect(
        len(arr) == 0 and arr.capacity == initial,
        f"пустой массив: len = {len(arr)}, capacity = {arr.capacity}",
    )
    expect_index_error(lambda: arr.get(0), "get(0) пустого массива")
    expect_index_error(lambda: arr.set(0, 1), "set(0, 1) пустого массива")
    expect_index_error(arr.pop, "pop() пустого массива")

    ref: list[int] = []
    for i in range(100):  # проходим границы ёмкости 4, 8, 16, 32, 64
        arr.append(i * i)
        ref.append(i * i)
        size = len(ref)
        expect(len(arr) == size, f"после {size} append: len = {len(arr)}")
        expect(
            arr.capacity == expected_capacity(size),
            f"после {size} append: capacity = {arr.capacity}, ожидалось "
            f"{expected_capacity(size)} (расширение x2 и только при size == capacity)",
        )
        expect(
            arr.copies == expected_copies(size),
            f"после {size} append: copies = {arr.copies}, ожидалось {expected_copies(size)}",
        )
    for i, value in enumerate(ref):
        got = arr.get(i)
        expect(got == value, f"get({i}) = {got!r}, ожидалось {value!r}")
    arr.set(0, -1)
    arr.set(99, -99)
    ref[0], ref[99] = -1, -99
    expect(
        arr.get(0) == -1 and arr.get(99) == -99,
        "set(0, ...) или set(99, ...) не изменил элемент",
    )
    for bad in (100, arr.capacity - 1, arr.capacity, -1, -100):
        expect_index_error(lambda bad=bad: arr.get(bad), f"get({bad}) при size = 100")
        expect_index_error(
            lambda bad=bad: arr.set(bad, 0), f"set({bad}, 0) при size = 100"
        )

    # pop до пустого, повторный рост и снова pop; сжатие, если есть, — только на ¼
    for refill in (70, 0):
        while ref:
            cap_before = arr.capacity
            got, expected = arr.pop(), ref.pop()
            size = len(ref)
            expect(
                got == expected,
                f"pop() при size = {size + 1}: {got!r}, ожидалось {expected!r}",
            )
            expect(len(arr) == size, f"после pop(): len = {len(arr)}, ожидалось {size}")
            expect(
                arr.capacity == cap_before
                or (
                    arr.capacity == cap_before // 2
                    and size <= cap_before // 4
                    and arr.capacity >= initial
                ),
                f"pop() при size = {size + 1}: capacity {cap_before} -> {arr.capacity}; "
                f"сжимать можно только вдвое, при size <= capacity // 4 и не ниже {initial}",
            )
        expect_index_error(arr.pop, "pop() опустошённого массива")
        for i in range(refill):
            arr.append(i)
            ref.append(i)
            expect(
                len(arr) == len(ref) <= arr.capacity,
                f"повторный рост: len = {len(arr)}, capacity = {arr.capacity}",
            )
        for i, value in enumerate(ref):
            got = arr.get(i)
            expect(
                got == value,
                f"после повторного роста get({i}) = {got!r}, ожидалось {value!r}",
            )


def check_stack() -> None:
    """LIFO через границы ёмкости, pop/peek пустого стека, сверка с list."""
    st = Stack()
    expect(len(st) == 0, f"пустой стек: len = {len(st)}")
    expect_index_error(st.pop, "pop() пустого стека")
    expect_index_error(st.peek, "peek() пустого стека")

    for start in (0, 100):  # второй проход — после опустошения
        values = list(range(start, start + 20))  # 20 элементов: границы 4, 8 и 16
        for k, x in enumerate(values, start=1):
            st.push(x)
            top = st.peek()
            expect(
                top == x and len(st) == k,
                f"после push({x}): peek() = {top!r}, len = {len(st)}",
            )
        top = st.peek()
        expect(
            top == values[-1] and len(st) == len(values),
            "повторный peek() изменил стек",
        )
        for k, expected in enumerate(reversed(values), start=1):
            got = st.pop()
            expect(
                got == expected, f"pop() №{k}: {got!r}, ожидалось {expected!r} (LIFO)"
            )
            expect(len(st) == len(values) - k, f"после pop() №{k}: len = {len(st)}")
        expect_index_error(st.pop, "pop() опустошённого стека")
        expect_index_error(st.peek, "peek() опустошённого стека")

    own, ref = Stack(), []
    ops = random_ops(
        random.Random(1), ("push",), ("pop", "peek"), count=3_000, max_size=40
    )
    compare_with_reference(
        ops,
        stack_methods(own),
        list_stack_methods(ref),
        "Stack против list, случайная серия",
    )


def check_deque() -> None:
    """Операции с обоих концов, опустошение и повторное наполнение, сверка с deque."""
    dq = Deque()
    expect(len(dq) == 0, f"пустой дек: len = {len(dq)}")
    expect_index_error(dq.pop_front, "pop_front() пустого дека")
    expect_index_error(dq.pop_back, "pop_back() пустого дека")

    # Все сочетания концов для одного элемента с повторным наполнением:
    # забытые head/tail при опустошении проявляются только так.
    pushes, pops = ("push_front", "push_back"), ("pop_front", "pop_back")
    for push1 in pushes:
        for pop1 in pops:
            for push2 in pushes:
                for pop2 in pops:
                    dq = Deque()
                    story = f"{push1}(1), {pop1}(), {push2}(2), {pop2}()"
                    getattr(dq, push1)(1)
                    first = getattr(dq, pop1)()
                    getattr(dq, push2)(2)
                    second = getattr(dq, pop2)()
                    expect(
                        (first, second, len(dq)) == (1, 2, 0),
                        f"{story}: извлечено {first!r} и {second!r}, len = {len(dq)}",
                    )
                    expect_index_error(dq.pop_front, f"{story}, затем pop_front()")
                    expect_index_error(dq.pop_back, f"{story}, затем pop_back()")

    own, ref = Deque(), collections.deque()
    ops = random_ops(random.Random(2), pushes, pops, count=5_000, max_size=12)
    compare_with_reference(
        ops,
        deque_methods(own),
        std_deque_methods(ref),
        "Deque против collections.deque, случайная серия",
    )


def check_variant_ops(stack_ops: list[Op], deque_ops: list[Op]) -> None:
    """Операции варианта: свой стек против list, свой дек против collections.deque."""
    compare_with_reference(
        stack_ops, stack_methods(Stack()), list_stack_methods([]), "ops_stack.txt"
    )
    compare_with_reference(
        deque_ops,
        deque_methods(Deque()),
        std_deque_methods(collections.deque()),
        "ops_deque.txt",
    )


def check_array_state(arr: DynamicArray, ref: list) -> None:
    expect(0 <= len(arr) <= arr.capacity, "Нарушено size <= capacity")
    expect(len(arr._buffer) == arr.capacity, "Длина буфера не равна capacity")
    expect([arr.get(i) for i in range(len(arr))] == ref, "Содержимое массива")
    expect(
        all(x is None for x in arr._buffer[len(arr) :]),
        "Хвост буфера удерживает ссылки",
    )


def check_deque_links(dq: Deque, ref: collections.deque) -> None:
    values = []
    previous = None
    node = dq._head
    while node is not None:
        expect(node.prev is previous, "Нарушена обратная ссылка узла")
        values.append(node.value)
        expect(len(values) <= len(dq), "Цикл в списке или неправильный size")
        previous, node = node, node.next
    expect(values == list(ref), "Порядок элементов дека")
    expect(previous is dq._tail, "Последний узел не равен tail")
    expect(len(values) == len(dq) == len(ref), "Размер дека")
    if dq._head is None:
        expect(dq._tail is None, "У пустого дека остался tail")
    else:
        expect(dq._head.prev is None and dq._tail.next is None, "Ссылки на концах")


def expect_value_error(call, label: str) -> None:
    try:
        call()
    except ValueError:
        return
    raise SelfCheckError(f"{label}: ожидался ValueError")


def check_extended() -> None:
    """300 случайных сценариев для каждой структуры; seed = 37."""
    for fn in (factorial, fib_naive, fib_memo, hanoi):
        expect_value_error(lambda fn=fn: fn(-1), f"{fn.__name__}(-1)")
    expect_value_error(lambda: hanoi(1, "A", "A", "B"), "Одинаковые стержни")
    for n in range(15):
        CALLS["fib_naive"] = CALLS["fib_memo"] = 0
        value = fib_naive(n)
        expect(value == fib_memo(n), "Фибоначчи: разные значения")
        a, b = 0, 1
        for _ in range(n + 1):
            a, b = b, a + b
        expect(CALLS["fib_naive"] == 2 * a - 1, "Формула числа наивных вызовов")
        expect(
            CALLS["fib_memo"] == (1 if n == 0 else 2 * n - 1),
            "Формула числа мемоизированных вызовов",
        )

    rng = random.Random(37)
    for _ in range(300):
        arr, ref = DynamicArray(), []
        for _ in range(100):
            op = rng.choice(("append", "pop", "get", "set"))
            x = rng.choice((None, -3, 0, 2, "x"))
            if op == "append":
                arr.append(x)
                ref.append(x)
            elif op == "pop":
                if ref:
                    expect(arr.pop() == ref.pop(), "Случайный pop массива")
                else:
                    expect_index_error(arr.pop, "Случайный pop пустого массива")
            else:
                index = rng.randrange(-2, len(ref) + 2)
                if 0 <= index < len(ref):
                    if op == "set":
                        arr.set(index, x)
                        ref[index] = x
                    else:
                        expect(arr.get(index) == ref[index], "Случайный get")
                else:
                    expect_index_error(
                        lambda: arr.get(index) if op == "get" else arr.set(index, x),
                        "Случайный неверный индекс",
                    )
            check_array_state(arr, ref)

        stack_ops = random_ops(rng, ("push",), ("pop", "peek"), 100, 30)
        compare_with_reference(
            stack_ops,
            stack_methods(Stack()),
            list_stack_methods([]),
            "Дополнительный стек",
        )
        dq, ref_dq = Deque(), collections.deque()
        operations = random_ops(
            rng, ("push_front", "push_back"), ("pop_front", "pop_back"), 100, 30
        )
        for op, arg in operations:
            got = apply_op(deque_methods(dq), op, arg)
            expected = apply_op(std_deque_methods(ref_dq), op, arg)
            expect(got == expected, "Дополнительный дек: результат")
            check_deque_links(dq, ref_dq)


def self_check(stack_ops: list[Op], deque_ops: list[Op]) -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    checks = (
        ("рекурсия", check_recursion),
        ("DynamicArray", check_dynamic_array),
        ("Stack", check_stack),
        ("Deque", check_deque),
        ("операции варианта", lambda: check_variant_ops(stack_ops, deque_ops)),
        ("собственные инварианты и 900 сценариев", check_extended),
    )
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where}")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(
            f"self_check: не пройдено разделов — {failed}; "
            f"замеры выполняются только после всех проверок."
        )
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Замеры (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------


def bench(call, label: str) -> float:
    """Медиана времени выполнения call() по REPEATS запускам, с прогревом."""
    call()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        call()
        times.append(time.perf_counter() - t0)
    TIMING_SAMPLES[label] = times
    return statistics.median(times)


def log_log_slope(points: list[tuple[int, float]]) -> float:
    """Наклон прямой в осях (log n, log t) — оценка показателя степени."""
    xs = [math.log10(n) for n, _ in points]
    ys = [math.log10(t) for _, t in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum(
        (x - mx) ** 2 for x in xs
    )


def appends(add, n: int) -> None:
    """n последовательных добавлений в конец."""
    for i in range(n):
        add(i)


def steady_ops(add, remove, k: int = FRONT_OPS) -> None:
    """k пар «добавить + удалить»: размер структуры не меняется."""
    for i in range(k):
        add(i)
        remove()


def replay(ops: list[Op], methods: dict) -> None:
    """Выполнить операции варианта без сверки — для замера."""
    for op, arg in ops:
        try:
            if arg is None:
                methods[op]()
            else:
                methods[op](arg)
        except IndexError:
            pass


def filled_structure(kind: str, n: int):
    """list, collections.deque или свой Deque из n элементов."""
    if kind == "list":
        return list(range(n))
    if kind == "deque":
        return collections.deque(range(n))
    dq = Deque()
    appends(dq.push_back, n)
    return dq


#: Операции у начала: подпись, тип структуры и пара методов (добавить, удалить).
#: Второй метод работает на другом конце и держит размер равным n.
FRONT_CASES = {
    "insert": (
        (
            "list.insert(0, x) + pop()",
            "list",
            lambda a: (functools.partial(a.insert, 0), a.pop),
        ),
        ("deque.appendleft + pop", "deque", lambda d: (d.appendleft, d.pop)),
        ("Deque.push_front + pop_back", "Deque", lambda d: (d.push_front, d.pop_back)),
    ),
    "remove": (
        (
            "list.append + pop(0)",
            "list",
            lambda a: (a.append, functools.partial(a.pop, 0)),
        ),
        ("deque.append + popleft", "deque", lambda d: (d.append, d.popleft)),
        ("Deque.push_back + pop_front", "Deque", lambda d: (d.push_back, d.pop_front)),
    ),
}
FRONT_TITLES = {"insert": "Вставка в начало", "remove": "Удаление из начала"}


def run_benchmarks(
    append_sizes: list[int], stack_ops: list[Op], deque_ops: list[Op]
) -> dict:
    """Замеры на данных варианта. Возвращает результаты для графиков."""
    TIMING_SAMPLES.clear()
    results: dict = {"fibonacci": [], "variant_ops": {}, "append_counts": []}

    print("\nЧисло вызовов: наивная рекурсия против мемоизации")
    for n in FIB_NS:
        CALLS["fib_naive"] = CALLS["fib_memo"] = 0
        value = fib_naive(n)
        fib_memo(n)
        results["fibonacci"].append(
            {
                "n": n,
                "value": value,
                "naive_calls": CALLS["fib_naive"],
                "memo_calls": CALLS["fib_memo"],
            }
        )
        print(
            f"  n={n:>2}  F(n)={value:>6}  fib_naive: {CALLS['fib_naive']:>7} вызовов"
            f"  fib_memo: {CALLS['fib_memo']:>2} вызовов"
        )

    print("\nСерии append на размерах варианта:")
    results["append"] = []
    for n in append_sizes:
        t_own = (
            bench(lambda: appends(DynamicArray().append, n), f"append:DynamicArray:{n}")
            / n
        )
        t_list = bench(lambda: appends([].append, n), f"append:list:{n}") / n
        arr = DynamicArray()
        appends(arr.append, n)
        cost = (n + arr.copies) / n  # записи и копирования на одну операцию
        results["append"].append((n, t_own, t_list, cost))
        results["append_counts"].append(
            {"n": n, "copies": arr.copies, "capacity": arr.capacity, "cost": cost}
        )
        print(
            f"  n={n:>7}  t/n: DynamicArray {t_own:.2e} c, list {t_list:.2e} c"
            f"  копирований {arr.copies:>7}  (n + копирования)/n = {cost:.3f}"
        )

    for key, title in FRONT_TITLES.items():
        print(
            f"\n{title}: время пары операций при размере n = "
            f"{', '.join(map(str, FRONT_SIZES))}"
        )
        results[key] = {}
        for label, kind, methods in FRONT_CASES[key]:
            points = []
            for n in FRONT_SIZES:
                add, remove = methods(filled_structure(kind, n))
                points.append(
                    (
                        n,
                        bench(lambda: steady_ops(add, remove), f"{key}:{kind}:{n}")
                        / FRONT_OPS,
                    )
                )
            results[key][label] = points
            row = "  ".join(f"{t:.2e}" for _, t in points)
            print(f"  {label:28s} {row}   наклон {log_log_slope(points):.2f}")

    print("\nОперации варианта целиком: время на операцию")
    cases = (
        (
            "ops_stack.txt",
            stack_ops,
            "Stack",
            lambda: stack_methods(Stack()),
            "list",
            lambda: list_stack_methods([]),
        ),
        (
            "ops_deque.txt",
            deque_ops,
            "Deque",
            lambda: deque_methods(Deque()),
            "collections.deque",
            lambda: std_deque_methods(collections.deque()),
        ),
    )
    for name, ops, own_label, make_own, ref_label, make_ref in cases:
        t_own = bench(lambda: replay(ops, make_own()), f"variant:{own_label}") / len(
            ops
        )
        t_ref = bench(lambda: replay(ops, make_ref()), f"variant:{ref_label}") / len(
            ops
        )
        results["variant_ops"][name] = {
            "operations": len(ops),
            "own": own_label,
            "reference": ref_label,
            "own_seconds_per_op": t_own,
            "reference_seconds_per_op": t_ref,
            "ratio": t_own / t_ref,
        }
        print(
            f"  {name}: {own_label} {t_own:.2e} c, {ref_label} {t_ref:.2e} c"
            f" — в {t_own / t_ref:.1f} раза медленнее"
        )
    results["timing_samples"] = dict(TIMING_SAMPLES)
    return results


# ---------------------------------------------------------------------------
# 7. Графики
# ---------------------------------------------------------------------------


def plot_results(results: dict, out_dir: Path) -> None:
    """Два графика: серии append варианта и операции у начала (log-log)."""
    try:
        import matplotlib

        matplotlib.use("Agg")  # сохранение в файл без графической оболочки
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "\nmatplotlib не установлен — графики пропущены "
            "(pip install -r requirements.txt)"
        )
        return

    rows = results["append"]
    ns = [row[0] for row in rows]
    fig, (ax_t, ax_c) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax_t.plot(ns, [row[1] for row in rows], marker="o", label="DynamicArray.append")
    ax_t.plot(ns, [row[2] for row in rows], marker="s", label="list.append")
    ax_t.set_xscale("log")
    ax_t.set_xlabel("число операций n")
    ax_t.set_ylabel("время на операцию t/n, с")
    ax_t.set_title("Средняя стоимость append")
    ax_t.grid(True, which="both", linewidth=0.3)
    ax_t.legend()
    ax_c.plot(ns, [row[3] for row in rows], marker="o", label="(n + копирования)/n")
    ax_c.axhline(3, color="grey", linestyle="--", label="оценка методом учёта")
    ax_c.set_xscale("log")
    ax_c.set_ylim(0, 3.5)
    ax_c.set_xlabel("число операций n")
    ax_c.set_ylabel("записей и копирований на операцию")
    ax_c.set_title("DynamicArray: стоимость в элементарных действиях")
    ax_c.grid(True, which="both", linewidth=0.3)
    ax_c.legend(loc="lower right")
    fig.tight_layout()
    append_path = out_dir / "lab02_append.png"
    fig.savefig(append_path, dpi=150)
    plt.close(fig)

    fig2, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, (key, title) in zip(axes, FRONT_TITLES.items()):
        for label, points in results[key].items():
            ax.plot(
                [n for n, _ in points],
                [t for _, t in points],
                marker="o",
                label=f"{label} (наклон ≈ {log_log_slope(points):.2f})",
            )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("размер структуры n")
        ax.set_title(title)
        ax.grid(True, which="both", linewidth=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("время пары операций, с")
    fig2.tight_layout()
    front_path = out_dir / "lab02_front.png"
    fig2.savefig(front_path, dpi=150)
    plt.close(fig2)

    print(f"\nГрафики сохранены:\n  {append_path}\n  {front_path}")


# ---------------------------------------------------------------------------


def save_results(results: dict, data_dir: Path, variant: int, out_dir: Path) -> None:
    names = ("manifest.json", "ops_stack.txt", "ops_deque.txt", "ops_append_sizes.txt")
    hashes = {
        name: hashlib.sha256((data_dir / name).read_bytes()).hexdigest()
        for name in names
    }
    metadata = {
        "variant": variant,
        "seed": 30 + variant,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repeats": REPEATS,
        "warmup_runs": 1,
        "front_sizes": FRONT_SIZES,
        "front_pairs_per_run": FRONT_OPS,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256(
            Path(__file__).with_name("generate_data.py").read_bytes()
        ).hexdigest(),
        "input_sha256": hashes,
        "verification": {
            "starter_sections_passed": 5,
            "additional_random_scenarios": 900,
            "additional_random_seed": 37,
            "stack_variant_operations": results["variant_ops"]["ops_stack.txt"][
                "operations"
            ],
            "deque_variant_operations": results["variant_ops"]["ops_deque.txt"][
                "operations"
            ],
        },
        "timing_notes": "Front timings are pairs of operations. Append and variant timings include empty container construction. Inputs are loaded before timing. GC uses Python defaults.",
    }
    payload = {"metadata": metadata, "results": results}
    (out_dir / "measurements.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument(
        "--data",
        type=Path,
        default=None,
        help="каталог с данными варианта (по умолчанию ищется data/generated)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "results-new",
        help="каталог результатов (по умолчанию lab02/results-new)",
    )
    ap.add_argument(
        "--check-only", action="store_true", help="только проверки, без замеров"
    )
    args = ap.parse_args()

    data_dir = find_data_dir(args.data)
    check_variant(data_dir, args.variant)
    append_sizes = load_append_sizes(data_dir)
    stack_ops = load_ops(data_dir, "stack")
    deque_ops = load_ops(data_dir, "deque")

    self_check(stack_ops, deque_ops)
    if args.check_only:
        return
    if (args.out / "measurements.json").exists():
        raise SystemExit(
            f"Результаты уже существуют: {args.out}. Выберите другой --out."
        )
    args.out.mkdir(parents=True, exist_ok=True)
    results = run_benchmarks(append_sizes, stack_ops, deque_ops)
    save_results(results, data_dir, args.variant, args.out)
    plot_results(results, args.out)


if __name__ == "__main__":
    main()
