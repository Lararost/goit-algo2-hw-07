import random
import time
from collections import OrderedDict
from typing import List, Tuple


# Максимальна кількість результатів у LRU-кеші.
CACHE_SIZE = 1000

# OrderedDict дає змогу зберігати порядок використання елементів.
range_cache = OrderedDict()


def make_queries(
    n: int,
    q: int,
    hot_pool: int = 30,
    p_hot: float = 0.95,
    p_update: float = 0.03,
) -> List[Tuple]:
    """
    Генерує запити Range та Update.

    Більшість Range-запитів повторюють популярні діапазони,
    що дозволяє оцінити ефективність кешування.
    """
    hot = [
        (
            random.randint(0, n // 2),
            random.randint(n // 2, n - 1),
        )
        for _ in range(hot_pool)
    ]

    queries = []

    for _ in range(q):
        if random.random() < p_update:
            index = random.randint(0, n - 1)
            value = random.randint(1, 100)
            queries.append(("Update", index, value))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)

            queries.append(("Range", left, right))

    return queries


def range_sum_no_cache(
    array: List[int],
    left: int,
    right: int,
) -> int:
    """
    Обчислює суму елементів масиву в діапазоні
    без використання кешу.
    """
    return sum(array[left:right + 1])


def update_no_cache(
    array: List[int],
    index: int,
    value: int,
) -> None:
    """
    Оновлює значення елемента масиву без кешу.
    """
    array[index] = value


def range_sum_with_cache(
    array: List[int],
    left: int,
    right: int,
) -> int:
    """
    Обчислює суму елементів у діапазоні
    з використанням LRU-кешу.
    """
    key = (left, right)

    if key in range_cache:
        # Позначаємо запис як нещодавно використаний.
        range_cache.move_to_end(key)
        return range_cache[key]

    result = sum(array[left:right + 1])
    range_cache[key] = result

    # Якщо кеш переповнений, видаляємо найстаріший запис.
    if len(range_cache) > CACHE_SIZE:
        range_cache.popitem(last=False)

    return result


def update_with_cache(
    array: List[int],
    index: int,
    value: int,
) -> None:
    """
    Оновлює елемент масиву та видаляє з кешу
    всі діапазони, до яких входить змінений індекс.
    """
    array[index] = value

    keys_to_delete = [
        key
        for key in range_cache
        if key[0] <= index <= key[1]
    ]

    for key in keys_to_delete:
        del range_cache[key]


def process_queries_no_cache(
    array: List[int],
    queries: List[Tuple],
) -> None:
    """
    Виконує всі запити без використання кешу.
    """
    for query in queries:
        operation = query[0]

        if operation == "Range":
            _, left, right = query
            range_sum_no_cache(array, left, right)

        elif operation == "Update":
            _, index, value = query
            update_no_cache(array, index, value)


def process_queries_with_cache(
    array: List[int],
    queries: List[Tuple],
) -> None:
    """
    Виконує всі запити з використанням LRU-кешу.
    """
    for query in queries:
        operation = query[0]

        if operation == "Range":
            _, left, right = query
            range_sum_with_cache(array, left, right)

        elif operation == "Update":
            _, index, value = query
            update_with_cache(array, index, value)


def main() -> None:
    """
    Генерує масив і запити, після чого порівнює
    час виконання з кешем та без кешу.
    """
    random.seed(42)

    n = 100_000
    q = 50_000

    initial_array = [
        random.randint(1, 100)
        for _ in range(n)
    ]

    queries = make_queries(
        n=n,
        q=q,
        hot_pool=30,
        p_hot=0.95,
        p_update=0.03,
    )

    # Окремі копії потрібні, щоб обидва способи
    # працювали з однаковими початковими даними.
    array_without_cache = initial_array.copy()
    array_with_cache = initial_array.copy()

    start_time = time.perf_counter()

    process_queries_no_cache(
        array_without_cache,
        queries,
    )

    no_cache_time = time.perf_counter() - start_time

    # Очищуємо кеш перед тестуванням.
    range_cache.clear()

    start_time = time.perf_counter()

    process_queries_with_cache(
        array_with_cache,
        queries,
    )

    cache_time = time.perf_counter() - start_time

    print(f"Без кешу: {no_cache_time:.2f} с")
    print(f"LRU-кеш:  {cache_time:.2f} с")

    if cache_time > 0:
        speedup = no_cache_time / cache_time
        print(f"Прискорення: x{speedup:.2f}")


if __name__ == "__main__":
    main()
