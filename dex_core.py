import time
from typing import Optional, cast, List

import brickpi3
from brickpi3 import BrickPi3

RGB = (int, int, int)
Percent = int


class Core:
    """Объектно ориентированная обертка для BrickPi3 API."""
    def __init__(self):
        self.BP = brickpi3.BrickPi3()

        self.PORT_S1 = SensorPort(self, self.BP.PORT_1)
        self.PORT_S2 = SensorPort(self, self.BP.PORT_2)
        self.PORT_S3 = SensorPort(self, self.BP.PORT_3)
        self.PORT_S4 = SensorPort(self, self.BP.PORT_4)

        self.PORT_A = MotorPort(self, self.BP.PORT_A)
        self.PORT_B = MotorPort(self, self.BP.PORT_B)
        self.PORT_C = MotorPort(self, self.BP.PORT_C)
        self.PORT_D = MotorPort(self, self.BP.PORT_D)

    def reset_all(self):
        """
        Сбрасывает состояние робота. Устанавливает всем сенсорам тип NONE, двигатели переводит в режим float, а пределы
        мощности моторов в значения по умолчанию и возвращает контроль гад светодиодом прошивке BrickPi3.
        """
        self.BP.reset_all()

    def print_info(self):
        BP = self.BP
        # Each of the following BP.get functions return a value that we want to display.
        print("Manufacturer    : ", BP.get_manufacturer())  # read and display the serial number
        print("Board           : ", BP.get_board())  # read and display the serial number
        print("Serial Number   : ", BP.get_id())  # read and display the serial number
        print("Hardware version: ", BP.get_version_hardware())  # read and display the hardware version
        print("Firmware version: ", BP.get_version_firmware())  # read and display the firmware version
        print("Battery voltage : ", BP.get_voltage_battery())  # read and display the current battery voltage
        print("9v voltage      : ", BP.get_voltage_9v())  # read and display the current 9v regulator voltage
        print("5v voltage      : ", BP.get_voltage_5v())  # read and display the current 5v regulator voltage
        print("3.3v voltage    : ", BP.get_voltage_3v3())  # read and display the current 3.3v regulator voltage


class Port:
    """Абстрактный класс для всех видов портов."""
    def __init__(self, core: Core, port_id):
        self.core = core
        self.port_id = port_id

    def get_core(self):
        """Возвращает ссылку на ядро которому принадлежит данный порт."""
        return self.core


class Sensor:
    """Абстрактный класс для всех видов сенсоров."""
    def __init__(self, port, stype):
        self._port = port
        self._stype = None
        self._set_sensor_type(stype)

    def _set_sensor_type(self, stype):
        if self._stype != stype:
            self.get_core().BP.set_sensor_type(self._port.port_id, stype)
            self._stype = stype
            time.sleep(0.02)

    def get_core(self):
        """Возвращает ссылку на ядро которому принадлежит данный сенсор."""
        return self._port.get_core()

    def get_data(self) -> object:
        """Возвращает градусы и угловую скорость в градусах в секунду."""
        n = 1
        while True:
            try:
                return self.get_core().BP.get_sensor(self._port.port_id)
            except brickpi3.SensorError as _error:
                if n % 20 == 0:
                    print("[ERROR] {} на порту {} не готов.".format(type(self).__name__, self._port.port_id))
                n += 1
                time.sleep(0.05)


class GyroSensor(Sensor):
    """Гироскопический сенсор, или по простоому -- компас."""
    def __init__(self, port):
        super().__init__(port, port.get_core.BP.SENSOR_TYPE.EV3_GYRO_ABS_DPS)

    def get_degrees(self) -> int:
        """Возвращает градусы."""
        l = self.get_data()
        assert isinstance(l, list)
        return l[0]

    def get_dps(self) -> int:
        """возвращает угловую скорость в градусах в секунду."""
        l = self.get_data()
        assert isinstance(l, list)
        return l[1]


class TouchSensor(Sensor):
    """Датчик касания -- или по простому кнопка."""
    def __init__(self, port):
        super().__init__(port, port.get_core().BP.SENSOR_TYPE.TOUCH)

    def is_touch(self) -> bool:
        """Возвращает 'True'(Истина) если датчик в состоянии 'нажат' и 'False'(Ложь) если нет."""
        return self.get_data() == 1


class ColorSensor(Sensor):
    """Датчик цвета и света."""

    def __init__(self, port):
        super().__init__(port, port.get_core().BP.SENSOR_TYPE.EV3_COLOR_REFLECTED)
        self.get_data()

    def get_reflected(self) -> int:
        """Возвращает яркость отраженного красного света."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_COLOR_REFLECTED)
        return cast(int, self.get_data())

    def get_ambient(self) -> int:
        """Возвращает яркость внешнего освещения."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_COLOR_AMBIENT)
        return cast(int, self.get_data())

    def get_color(self) -> int:
        """Возвращает цвет воспринимаемый датчиком."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_COLOR_COLOR)
        return cast(int, self.get_data())

    def get_color_components(self) -> RGB:
        """Возвращает компоненты цвета воспринимаемого датчиком."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS)
        return self.get_data()


class UltrasonicSensor(Sensor):
    """Ультразвуковой датчик расстояния до препятсятвия."""
    def __init__(self, port):
        super().__init__(port, port.get_core().BP.SENSOR_TYPE.EV3_ULTRASONIC_CM)
        self.get_data()

    def get_distance_cm(self) -> int:
        """Возвращает расстояние определяемое датчиком, в сантиметрах."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_ULTRASONIC_CM)
        return cast(int, self.get_data())

    def get_distance_inch(self) -> int:
        """Возвращает расстояние определяемое датчиком, в дюймах."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_ULTRASONIC_INCHES)
        return cast(int, self.get_data())

    def listen(self) -> bool:
        """Возвращает присутствие другого ультразвукового датчика: True - присутствует, False - нет."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_ULTRASONIC_LISTEN)
        return self.get_data() == 1


class InfraredSensor(Sensor):
    """Инфракрассный датчик расстояния до препятсятвия."""
    def __init__(self, port):
        super().__init__(port, port.get_core().BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)
        self.get_data()

    def get_proximity(self) -> Percent:
        """Возвращает близость препятствия в процентах: 1..100 ."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)
        return cast(int, self.get_data())

    def get_seek(self):# -> List[(int, int)]:
        """Возвращает значение 4-х каналов."""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_INFRARED_SEEK)
        return cast(List[(int, int)], self.get_data())

    def get_remote(self): # -> List[(int, int, int)]:
        """Возвращает значение 4-х каналов: список из 5-и значений - red-up/down, blue-up/down, broadcast"""
        self._set_sensor_type(self.get_core().BP.SENSOR_TYPE.EV3_INFRARED_REMOTE)
        return List[(int, int, int)]


class SensorPort(Port):
    """Абстрактный класс для сенсорных портов."""
    def __init__(self, core, port_id):
        super().__init__(core, port_id)
        self._sensor = None  # type: Optional[Sensor]

    def get_sensor(self):
        """Возвращает сенсор который был установлен в данный порт."""
        if self._sensor is None:
            raise ValueError("На порту {} не установлен сенсор.".format(self.port_id))
        return self._sensor

    def _set_sensor(self, sensor) -> Sensor:
        if self._sensor is not None:
            raise ValueError("На порт {} уже установлен сенсор {}.".format(self.port_id, self._sensor))
        self._sensor = sensor
        return sensor

    def set_gyro_sensor(self) -> GyroSensor:
        """Подключить к этому порту гироскоп."""
        s = self._set_sensor(GyroSensor(self))
        assert isinstance(s, GyroSensor)
        return s

    def set_touch_sensor(self) -> TouchSensor:
        """Подключить к этому порту датчик касания (кнопка)."""
        s = self._set_sensor(TouchSensor(self))
        assert isinstance(s, TouchSensor)
        return s

    def set_color_sensor(self) -> ColorSensor:
        """Подключить цветовой сенсор к этому порту."""
        s = self._set_sensor(ColorSensor(self))
        assert isinstance(s, ColorSensor)
        return s

    def set_ultrasonic_sensor(self) -> UltrasonicSensor:
        """Подключить к этому порту ультразвуковой датчик."""
        s = self._set_sensor(UltrasonicSensor(self))
        assert isinstance(s, UltrasonicSensor)
        return s

    def set_infra_sensor(self) -> InfraredSensor:
        """Подключить к этому порту инфракрасный датчик."""
        s = self._set_sensor(InfraredSensor(self))
        assert isinstance(s, InfraredSensor)
        return s


class Motor:
    """
    Класс предоставляющий API мотора.
    """
    def __init__(self, port):
        self._port = port # type: MotorPort
        self._core = port.get_core()
        self.reset_encoder()
        self.set_power_float(limit=100)

    def get_core(self):
        """Возвращает ссылку на ядро которому принадлежит данный мотор."""
        return self._port.get_core()

    def reset_encoder(self):
        """Сбрасывает энкодер двигателя в значение 0."""
        # reset encoder
        BP = self._core.BP  # type: BrickPi3
        BP.reset_motor_encoder(self._port.port_id)

    def set_power_float(self, limit: int = None):
        BP = self._core.BP
        BP.set_motor_power(BP.PORT_D, BP.MOTOR_FLOAT)
        if limit is not None:
            BP.set_motor_limits(self._port.port_id, limit)

    def set_power(self, value: int):
        BP = self._core.BP
        BP.set_motor_power(self._port.port_id, value)

    def get_degrees(self) -> int:
        """Возвращает текущее значение энкодера мотора в градусах."""
        return self._core.BP.get_motor_encoder(self._port.port_id)

    def set_dps(self, dps: float):
        """Установить желаемую скорость вращения мотора в градусах в секунду."""
        self._core.BP.set_motor_dps(self._port.port_id, dps)

    def get_status(self):
        """
            Возвращает подробное состояние мотора, а именно список из 4-х элементов:
            * флаги   -- 8 бит
                * bit 0 (LOW_VOLTAGE_FLOAT) -- если 1 то двигатель автоматически
                                                отключился из-за недостатка энергии.
                * bit 1 (OVERLOADED) -- если 1 то текущий dps сильно меньше целевого,
                                        т.е. мотор либо тоолько разгоняется,
                                        либо ему что-то препятствует.
            * энергия -- -100%..100%
            * энкодер -- в градусах
            * dps     -- угловая скорость вращения мотора в секундах
        """
        return self._core.BP.get_motor_status(self._port.port_id)


class MotorPort(Port):
    def __init__(self, core, port_id):
        super().__init__(core, port_id)
        self._motor = None  # type: Optional[Motor]

    def set_motor(self) -> Motor:
        """Установить мотор на данном порту."""
        return self._set_motor(Motor(self))

    def get_motor(self):
        if self._motor is None:
            raise ValueError("На порту {} не установлен мотор.".format(self.port_id))
        return self._motor

    def _set_motor(self, motor) -> Motor:
        if self._motor is not None:
            raise ValueError("На порт {} уже установлен мотор {}.".format(self.port_id, self._motor))
        self._motor = motor
        return motor
