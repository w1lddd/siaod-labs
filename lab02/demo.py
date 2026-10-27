from lab02 import (
    CALLS,
    Deque,
    DynamicArray,
    Stack,
    factorial,
    fib_memo,
    fib_naive,
    hanoi,
)


def main():
    print("1. РЕКУРСИЯ")
    print("factorial(5) =", factorial(5))
    CALLS["fib_naive"] = 0
    CALLS["fib_memo"] = 0
    print("fib_naive(10) =", fib_naive(10), "вызовов:", CALLS["fib_naive"])
    print("fib_memo(10) =", fib_memo(10), "вызовов:", CALLS["fib_memo"])
    moves = []
    print("Ханой, 3 диска: ходов =", hanoi(3, moves=moves))
    print("Ходы:", moves)

    print("\n2. ДИНАМИЧЕСКИЙ МАССИВ")
    a = DynamicArray()
    for x in range(1, 6):
        a.append(x)
        print(
            "Добавили",
            x,
            "size =",
            len(a),
            "capacity =",
            a.capacity,
            "copies =",
            a.copies,
        )
    print("get(2) =", a.get(2))
    a.set(2, 30)
    print("После set(2, 30):", [a.get(i) for i in range(len(a))])
    print("pop() =", a.pop(), "size =", len(a), "capacity =", a.capacity)

    print("\n3. СТЕК: LIFO")
    stack = Stack()
    for x in (10, 20, 30):
        stack.push(x)
    print("Добавили: 10, 20, 30")
    print("peek() =", stack.peek(), "size =", len(stack))
    print("Порядок pop:", [stack.pop() for _ in range(len(stack))])
    for name in ("peek", "pop"):
        try:
            getattr(stack, name)()
        except IndexError as error:
            print("Пустой стек,", name + "():", type(error).__name__, str(error))

    print("\n4. ДЕК: ОБА КОНЦА")
    d = Deque()
    d.push_back(10)
    d.push_back(20)
    d.push_front(5)
    d.push_back(30)
    print("push_back(10), push_back(20), push_front(5), push_back(30)")
    print("pop_front() =", d.pop_front())
    print("pop_back() =", d.pop_back())
    print("pop_front() =", d.pop_front())
    print("pop_back() =", d.pop_back(), "size =", len(d))
    d.push_back(100)
    print("Повторное наполнение: push_back(100), pop_front() =", d.pop_front())

    print("\n5. ОЧЕРЕДЬ ИЗ ДВУХ СТЕКОВ: FIFO")
    incoming = Stack()
    outgoing = Stack()
    for x in (1, 2, 3):
        incoming.push(x)
    if len(outgoing) == 0:
        while len(incoming) > 0:
            outgoing.push(incoming.pop())
    print("Добавили: 1, 2, 3")
    print("После переноса извлекаем:", [outgoing.pop() for _ in range(len(outgoing))])


if __name__ == "__main__":
    main()
