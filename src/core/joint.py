from .servo import Servo


class Joint:
    __name: str
    __parent: None  # type Joint
    __servo: Servo = None

    def __init__(self, name: str, servo: Servo, parent=None):
        self.__name = name
        self.__parent = parent
        self.__servo = servo

    @property
    def name(self):
        return self.__name

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        self.__parent = value

    @property
    def servo(self):
        return self.__servo

    @property
    def angle(self):
        """The servo angle in degrees. Must be in the range ``0`` to ``actuation_range``.
        Is None when servo is disabled."""
        return self.servo.angle

    @angle.setter
    def angle(self, new_angle: int = None):
        self.servo.angle = new_angle
