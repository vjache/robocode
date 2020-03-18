import time

from dex_core import Core

#
# В этом примере робот стартует и движется пока расстояние на сонаре больше 50-ти см.
#
# Требуются:
#   2 мотора
#   1 ультразвуковой датчик -- сонар

if __name__ == "__main__":
    # Инициализируем робота
    r = Core()
    sonar = r.PORT_S1.set_ultrasonic_sensor()
    motor1 = r.PORT_A.set_motor()
    motor2 = r.PORT_B.set_motor()

    # Робот действует
    motor1.set_dps(20)
    motor2.set_dps(20)

    # Пока расстояние (до препятствия) больше 50 см продолжаем движение.
    while sonar.get_distance_cm() > 50:
        time.sleep(0.1)

    motor1.set_dps(0)
    motor2.set_dps(0)
