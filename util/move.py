from time import sleep
from typing import Callable

from dex_core import Motor, ColorSensor


def simple_follow_line_1cs(m1: Motor, m2: Motor, c: ColorSensor, continue_condition: Callable[[], bool]):
    """Простейший алгоритм движеня по линии с помощью одного цветового датчика."""
    gray = 33.0  # яркость "серого", т.е. когда датчик на половину над черной и наполовну над белой областями
    a = 0.1   # чувствительность отклонения от линии
    v = 20.0  # базовая скорость
    while continue_condition():  # проверяем условие продолжения цикла
        r = c.get_reflected()  # считываем величину отраженного света
        d = (gray - r) * a     # вычисляем степень поворота
        m1.set_dps(v - d)      # установить угловую скорость на моторе 1
        m2.set_dps(v + d)      # установить угловую скорость на моторе 2
        sleep(0.01)            # ждем 10 миллисекунд -- даем поработать моторам
    m1.set_dps(0)  # останавливем мотор 1
    m2.set_dps(0)  # останавливем мотор 2


def follow_line_1cs(m1: Motor, m2: Motor, c: ColorSensor, continue_condition: Callable[[], bool]):
    """Алгоритм движеня по линии с помощью одного цветового датчика.
       Отличие от простейшего алгоритма в том что происходит замедление при сильном отклонении от 'серой' зоны
       (т.е. от края линии)."""
    gray = 33.0  # яркость "серого", т.е. когда датчик на половину над черной и наполовну над белой областями
    a = 0.1   # чувствительность отклонения от линии
    v = 20.0  # базовая скорость
    while continue_condition():  # проверяем условие продолжения цикла
        r = c.get_reflected()  # считываем величину отраженного света
        d = (gray - r) * a     # вычисляем степень поворота
        f = max(0.0, 1 - abs(gray - r) / gray)
        m1.set_dps(v*f - d)    # установить угловую скорость на моторе 1
        m2.set_dps(v*f + d)    # установить угловую скорость на моторе 2
        sleep(0.01)            # ждем 10 миллисекунд -- даем поработать моторам
    m1.set_dps(0)  # останавливем мотор 1
    m2.set_dps(0)  # останавливем мотор 2


def follow_line_2cs(m1: Motor, m2: Motor, c1: ColorSensor, c2: ColorSensor, continue_condition: Callable[[], bool]):
    gray = 33.0
    a = 1.
    v = 20.0
    while continue_condition():
        r1 = c1.get_reflected()
        r2 = c2.get_reflected()
        d = (r1 - r2) * a
        f = 1 - max(abs(gray - r1), abs(gray - r2)) / gray
        m1.set_dps(v*f - d)
        m2.set_dps(v*f + d)
        sleep(0.01)
    m1.set_dps(0)
    m2.set_dps(0)
