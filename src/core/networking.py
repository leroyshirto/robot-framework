import network
import json
from libs import logging
from libs.websockets.ws_server import (
    WebSocketServer,
    WebSocketClient,
    ClientClosedError,
)


class RobotServerClient(WebSocketClient):
    __commands: dict = {}

    def __init__(self, conn, commands: dict = None):
        super().__init__(conn)
        self.__commands = commands

    def process(self):
        try:
            msg = self.connection.read()
            if not msg:
                return
            msg = msg.decode("utf-8")
            print(f"WebSocket RPC request text: {msg}")
            data = json.loads(msg)
            
            rpc_method_name = data.get("method", None)
            if not rpc_method_name:
                response = {"type": "error", "msg": "rpc request must have a method name"}
                self.connection.write(json.dumps(response))
                return

            rpc_method = self.__commands.get(rpc_method_name, None)
            if not rpc_method:
                response = {"type": "error", "msg": "method not found"}
                self.connection.write(json.dumps(response))
                return
            params = data.get("params", None)
            if params and len(params) > 0:
                method_response = rpc_method(**params)
            else:
                method_response = rpc_method()

            response = {
                "method": rpc_method_name,
                "params": params,
                "payload": method_response
            }

            response_json = json.dumps(response)
            print(f"WebSocket RPC response text: {response_json}")
            self.connection.write(response_json)
        except ValueError as e:
            response = {"type": "error", "msg": str(e)}
            self.connection.write(json.dumps(response))
        except ClientClosedError:
            self.connection.close()


class RobotServer(WebSocketServer):
    __socket_commands: dict = {}

    def __init__(self):
        super().__init__("index.html", 8)

    def _make_client(self, conn):
        return RobotServerClient(conn, self.socket_commands)

    @property
    def socket_commands(self):
        return self.__socket_commands


class NetworkManager:
    __logger: logging.Logger = None
    __ws_server: RobotServer = None

    def __init__(self, network_config: dict):

        self.__logger = logging.getLogger(name="network-manager")
        ssid = network_config.get("ssid", None)
        if not ssid:
            raise Exception("network_config dict must contain a ssid key")

        password = network_config.get("password", None)
        if not password:
            raise Exception("network_config dict must contain a password key")

        self.station = network.WLAN(network.STA_IF)
        self.init_wifi(ssid, password)

        self.__ws_server = RobotServer()

    @property
    def logger(self):
        return self.__logger

    def register_command(self, name: str, function):
        self.logger.debug(f"registering {name} command")
        self.__ws_server.socket_commands[name] = function

    def init_wifi(self, ssid: str, password: str):
        self.logger.info("connecting to wifi")
        if self.station.isconnected():
            self.logger.debug("wifi already connected")
            return

        # activate the station interface
        self.logger.debug("activating wifi interface")
        self.station.active(True)
        self.station.connect(ssid, password)
        while not self.station.isconnected():
            pass
        self.logger.info(
            f"connected to {ssid} network and was given IP: {self.station.ifconfig()[0]}"
        )
        self.logger.debug(f"{ssid} if config: {self.station.ifconfig()}")

    def start_ws_server(self):
        self.__ws_server.start()

    def stop_ws_server(self):
        self.__ws_server.stop()

    def tick(self):
        self.__ws_server.process_all()

    # Stop server destructor
    def __del__(self):
        self.stop_ws_server()
