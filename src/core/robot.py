from machine import Pin, I2C
from .pca9685 import PCA9685
from .servo import DirectServo, PCAServo
from .joint import Joint
from .util import load_json_config

# Global joint cache
# TODO: Figure out a better way of doing this
robot_joints = {}


def joint_from_config_dict(joint_config: dict, attachments: dict):
    joint_servo_index = joint_config.get("servo_index", "")
    parts = joint_servo_index.split("/")
    if len(parts) < 2:
        raise Exception(
            f"invalid servo_index for joint {joint_config['name']} too few parts"
        )

    servo = None
    if (parts[0]) == "gpio":
        servo_pin = str(parts[1])
        if not servo_pin:
            raise Exception(
                f"invalid servo_index for joint {joint_config['name']}, gpio/pin is not valid"
            )
        servo = DirectServo(Pin(int(servo_pin)))
        print(f"created a DirectServo on gpio pin {servo_pin}")
    elif (parts[0]) == "pca9685":
        pca9685 = attachments.get("pca9685", None)
        if not pca9685:
            raise Exception(
                f"invalid servo_index for joint {joint_config['name']}, pca9685 attachment not found"
            )

        servo_channel = str(parts[1])
        if not servo_channel:
            raise Exception(
                f"invalid servo_index for joint {joint_config['name']}, pca9685/channel is not valid"
            )

        servo = PCAServo(pca9685, channel=int(servo_channel))
        print(f"created a PCAServo on pca9685 channel {servo_channel}")
    else:
        raise Exception(
            f"invalid joint config for joint {joint_config['name']} servo_index is required"
        )

    joint_children_config = joint_config.get("children", [])
    children = []
    for joint_child_config in joint_children_config:
        print(
            f"{joint_config['name']} child count {len(joint_child_config.get('children',[]))}"
        )
        print(
            f"adding joint child {joint_child_config['name']} to parent {joint_config['name']}"
        )
        children.append(joint_from_config_dict(joint_child_config, attachments))
        print(
            f"{joint_config['name']} child count {len(joint_child_config.get('children',[]))}"
        )

    new_joint = Joint(
        name=joint_config["name"],
        servo=servo,
        min_angle=joint_config.get("min_angle", None),
        max_angle=joint_config.get("max_angle", None),
        home_angle=joint_config.get("home_angle", 0),
    )

    for child in children:
        child.parent = new_joint

    new_joint.children = children

    robot_joints[new_joint.name] = new_joint

    return new_joint


class Robot:
    __name: str
    __joints: dict = None  # Dict[str, Joint]
    __attachments: dict = None

    def __init__(self, name: str, joints: dict, attachments: dict = None):
        self.__name = name
        self.__joints = joints

        if attachments is not None:
            self.__attachments = attachments

    @property
    def name(self):
        return self.__name

    @property
    def joints(self):
        return self.__joints

    @property
    def attachments(self):
        return self.__attachments

    @staticmethod
    def from_config(name: str):
        robo_config = load_json_config(f"config/robots/{name}.json")

        # Attachments
        attachments = {}
        for attachment_config in robo_config.get("attachments", []):
            if attachment_config.get("type", None) == "pca9685":
                sda_pin = attachment_config.get("sda_pin", None)
                if not sda_pin:
                    raise Exception(
                        "attachment config type: pca9685 must specify an sda_pin"
                    )

                scl_pin = attachment_config.get("scl_pin", None)
                if not scl_pin:
                    raise Exception(
                        "attachment config type: pca9685 must specify an scl_pin"
                    )

                i2c = I2C(sda=Pin(int(sda_pin)), scl=Pin(int(scl_pin)))

                print(
                    f"created an i2c pca9685 attachment on sda_pin: {sda_pin}, scl_pin: {scl_pin}"
                )

                attachments["pca9685"] = PCA9685(i2c)

        # Joints Dict[str, Joint]

        joints_config = robo_config.get("joints", [])

        # Initialise the joints for the robot
        # In the first pass initialise the joints
        # In the second pass link up the parent relations

        for joint_config in joints_config:
            print(f"joint config len: {len(joints_config)}")
            if joint_config["name"] not in robot_joints:
                robot_joints[joint_config["name"]] = joint_from_config_dict(
                    joint_config, attachments
                )

        return Robot(robo_config["name"], robot_joints, attachments)
