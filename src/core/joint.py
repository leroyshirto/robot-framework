from .servo import Servo


class Joint:
    __name: str
    __parent: None  # type Joint
    __servo: Servo = None

    children = []  # The decedents
    min_angle: int = None  # min angle the joint can move
    max_angle: int = None  # max angle the joint can move
    home_angle: int = 0  # the starting angle

    def __init__(
        self,
        name: str,
        servo: Servo,
        parent=None,
        min_angle: int = None,
        max_angle: int = None,
        home_angle: int = 0,
    ):
        self.__name = name
        self.__parent = parent
        self.__servo = servo

        self.min_angle = min_angle
        self.max_angle = max_angle
        self.home_angle = home_angle

        self.home()

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
        if self.min_angle and new_angle < self.min_angle:
            new_angle = self.min_angle
        if self.max_angle and new_angle > self.max_angle:
            new_angle = self.max_angle

        self.servo.angle = new_angle

    def home(self):
        self.servo.angle = self.home_angle
