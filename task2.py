import sys
import timeit
from functools import lru_cache
from typing import Optional

import matplotlib.pyplot as plt


# Для обчислення Fibonacci(950) рекурсивним способом.
sys.setrecursionlimit(5000)


@lru_cache(maxsize=None)
def fibonacci_lru(n: int) -> int:
    """
    Обчислює число Фібоначчі з використанням LRU-кешу.
    """
    if not isinstance(n, int):
        raise TypeError("n має бути цілим числом.")

    if n < 0:
        raise ValueError("n не може бути від'ємним.")

    if n < 2:
        return n

    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)


class Node:
    """Вузол Splay Tree."""

    def __init__(self, key: int, value: int) -> None:
        self.key = key
        self.value = value
        self.left: Optional["Node"] = None
        self.right: Optional["Node"] = None
        self.parent: Optional["Node"] = None


class SplayTree:
    """
    Самобалансоване Splay Tree для зберігання
    вже обчислених чисел Фібоначчі.
    """

    def __init__(self) -> None:
        self.root: Optional[Node] = None

    def _rotate_left(self, node: Node) -> None:
        """Виконує лівий поворот."""
        right_child = node.right

        if right_child is None:
            return

        node.right = right_child.left

        if right_child.left is not None:
            right_child.left.parent = node

        right_child.parent = node.parent

        if node.parent is None:
            self.root = right_child
        elif node is node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child

        right_child.left = node
        node.parent = right_child

    def _rotate_right(self, node: Node) -> None:
        """Виконує правий поворот."""
        left_child = node.left

        if left_child is None:
            return

        node.left = left_child.right

        if left_child.right is not None:
            left_child.right.parent = node

        left_child.parent = node.parent

        if node.parent is None:
            self.root = left_child
        elif node is node.parent.left:
            node.parent.left = left_child
        else:
            node.parent.right = left_child

        left_child.right = node
        node.parent = left_child

    def _splay(self, node: Node) -> None:
        """
        Переміщує вибраний вузол до кореня дерева.
        """
        while node.parent is not None:
            parent = node.parent
            grandparent = parent.parent

            # Zig
            if grandparent is None:
                if node is parent.left:
                    self._rotate_right(parent)
                else:
                    self._rotate_left(parent)

            # Zig-zig: лівий випадок
            elif node is parent.left and parent is grandparent.left:
                self._rotate_right(grandparent)
                self._rotate_right(parent)

            # Zig-zig: правий випадок
            elif node is parent.right and parent is grandparent.right:
                self._rotate_left(grandparent)
                self._rotate_left(parent)

            # Zig-zag
            elif node is parent.right and parent is grandparent.left:
                self._rotate_left(parent)
                self._rotate_right(grandparent)

            else:
                self._rotate_right(parent)
                self._rotate_left(grandparent)

    def find(self, key: int) -> Optional[Node]:
        """
        Шукає вузол за ключем.

        Якщо вузол знайдено, він переміщується до кореня.
        """
        current = self.root
        last_visited = None

        while current is not None:
            last_visited = current

            if key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                self._splay(current)
                return current

        # Останній відвіданий вузол також переміщується
        # ближче до кореня.
        if last_visited is not None:
            self._splay(last_visited)

        return None

    def insert(self, key: int, value: int) -> None:
        """
        Додає нове значення до дерева або оновлює наявне.
        """
        if self.root is None:
            self.root = Node(key, value)
            return

        current = self.root
        parent = None

        while current is not None:
            parent = current

            if key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                current.value = value
                self._splay(current)
                return

        new_node = Node(key, value)
        new_node.parent = parent

        if key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._splay(new_node)


def fibonacci_splay(n: int, tree: SplayTree) -> int:
    """
    Обчислює число Фібоначчі та зберігає результати
    у Splay Tree.
    """
    if not isinstance(n, int):
        raise TypeError("n має бути цілим числом.")

    if n < 0:
        raise ValueError("n не може бути від'ємним.")

    cached_node = tree.find(n)

    if cached_node is not None:
        return cached_node.value

    if n < 2:
        result = n
    else:
        result = (
            fibonacci_splay(n - 1, tree)
            + fibonacci_splay(n - 2, tree)
        )

    tree.insert(n, result)

    return result


def measure_average_time(function, repeats: int = 5) -> float:
    """
    Вимірює середній час одного виконання функції.
    """
    measurements = timeit.repeat(
        function,
        repeat=repeats,
        number=1,
    )

    return sum(measurements) / len(measurements)


def print_results_table(
    n_values: list[int],
    lru_times: list[float],
    splay_times: list[float],
) -> None:
    """Виводить результати вимірювань у таблиці."""
    print("\nРезультати порівняння:\n")

    print(
        f"{'n':<8}"
        f"{'LRU Cache Time (s)':<24}"
        f"{'Splay Tree Time (s)':<24}"
    )

    print("-" * 56)

    for n, lru_time, splay_time in zip(
        n_values,
        lru_times,
        splay_times,
    ):
        print(
            f"{n:<8}"
            f"{lru_time:<24.8f}"
            f"{splay_time:<24.8f}"
        )


def create_plot(
    n_values: list[int],
    lru_times: list[float],
    splay_times: list[float],
) -> None:
    """Створює графік порівняння часу виконання."""
    plt.figure(figsize=(10, 6))

    plt.plot(
        n_values,
        lru_times,
        marker="o",
        label="LRU Cache",
    )

    plt.plot(
        n_values,
        splay_times,
        marker="x",
        label="Splay Tree",
    )

    plt.xlabel("Число Фібоначчі (n)")
    plt.ylabel("Середній час виконання (секунди)")
    plt.title(
        "Порівняння часу виконання для "
        "LRU Cache та Splay Tree"
    )

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        "fibonacci_comparison.png",
        dpi=150,
    )

    plt.show()


def print_conclusion(
    lru_times: list[float],
    splay_times: list[float],
) -> None:
    """Виводить короткий висновок про ефективність."""
    average_lru = sum(lru_times) / len(lru_times)
    average_splay = sum(splay_times) / len(splay_times)

    print("\nВисновок:")

    if average_lru < average_splay:
        difference = average_splay / average_lru

        print(
            "LRU Cache у середньому працює швидше "
            f"приблизно у {difference:.2f} разів."
        )
        print(
            "Це пояснюється швидким доступом до значень "
            "через хешовану структуру кешу."
        )
    else:
        difference = average_lru / average_splay

        print(
            "Splay Tree у середньому працює швидше "
            f"приблизно у {difference:.2f} разів."
        )

    print(
        "Splay Tree також повторно використовує обчислені "
        "значення, але потребує додаткових операцій повороту "
        "та перебудови дерева."
    )


def main() -> None:
    n_values = list(range(0, 951, 50))

    lru_times = []
    splay_times = []

    splay_tree = SplayTree()

    # Базові значення для Splay Tree.
    splay_tree.insert(0, 0)
    splay_tree.insert(1, 1)

    for n in n_values:
        lru_time = measure_average_time(
            lambda current_n=n: fibonacci_lru(current_n)
        )

        splay_time = measure_average_time(
            lambda current_n=n: fibonacci_splay(
                current_n,
                splay_tree,
            )
        )

        lru_times.append(lru_time)
        splay_times.append(splay_time)

    print_results_table(
        n_values,
        lru_times,
        splay_times,
    )

    create_plot(
        n_values,
        lru_times,
        splay_times,
    )

    print_conclusion(
        lru_times,
        splay_times,
    )

    print(
        "\nГрафік збережено у файлі "
        "fibonacci_comparison.png."
    )


if __name__ == "__main__":
    main()
