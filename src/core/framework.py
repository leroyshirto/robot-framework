from libs import logging
from core.networking import NetworkManager
from core.robot import Robot
from core.util import load_json_config


class RobotFramework:
    __robot: Robot = None
    __config: dict = None
    __network_manager: NetworkManager = None
    __logger: logging.Logger = None

    def __init__(self, robot: Robot, web_server: bool = True):

        self.__robot = robot
        self.__config = load_json_config("config/config.json")

        logging.leveledConfig(self.config.get("log_level", "info"))
        self.__logger = logging.getLogger(name="core-framework")

        if web_server:
            network_config = self.config.get("network", None)
            if not network_config:
                raise Exception("config.json must contain a network key")

            self.__network_manager = NetworkManager(network_config)
            self.__network_manager.start_ws_server()
            self.register_rpc_commands()

    @property
    def config(self):
        return self.__config

    @property
    def logger(self):
        return self.__logger

    @property
    def robot(self):
        return self.__robot

    @property
    def network_manager(self):
        return self.__network_manager

    def run_forever(self):
        try:
            # Main framework loop
            # TODO: allow each componant to declare their tick rate
            while True:
                self.network_manager.tick()
        except KeyboardInterrupt:
            pass
        # Teardown
        self.network_manager.stop_ws_server()
        self.logger.info("framework shutdown")

    def ping(self):
        return "pong"

    def get_config(self):
        return self.config
    
    def get_robot_config(self):
        return Robot.get_config(self.robot.name)

    def register_rpc_commands(self):
        self.network_manager.register_command("ping", self.ping)
        self.network_manager.register_command("get_config", self.get_config)
        self.network_manager.register_command("get_robot_config", self.get_robot_config)
