"""Unit-тесты для проверки базовой работоспособности unit-тестовой среды Документоскоп.

Модуль содержит тест-заглушку, предназначенную для проверки корректной работы
инфраструктуры unit-тестов.
"""


def test_dummy_unit():
    """Проверяет, что сумма 1 + 1 равна 2.

    Returns:
        None

    Примечание:
        В unit-тестах использование assert допустимо, так как pytest корректно
        обрабатывает AssertionError.
    """
    assert 1 + 1 == 2  # noqa S101: допустимо в тестах pytest
