"""
   Copyright 2019 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


from lifx.monitor import Monitor
from lifx.device_manager import DeviceManager
from lifx.controller import Controller
from lifx.logger import root_logger
import cc_lib, time


logger = root_logger.getChild(__name__)


device_manager = DeviceManager()


def on_connect(client: cc_lib.client.Client):
    devices = device_manager.devices
    for device in devices.values():
        try:
            if device.state["reachable"]:
                client.connectDevice(device, asynchronous=True)
        except cc_lib.client.DeviceConnectError:
            pass


connector_client = cc_lib.client.Client()
connector_client.setConnectClbk(on_connect)


cloud_monitor = Monitor(device_manager, connector_client)
controller = Controller(device_manager, connector_client)


if __name__ == '__main__':
    while True:
        try:
            connector_client.initHub()
            break
        except cc_lib.client.HubInitializationError:
            time.sleep(10)
    connector_client.connect(reconnect=True)
    cloud_monitor.start()
    controller.start()
    try:
        cloud_monitor.join()
        controller.join()
    except KeyboardInterrupt:
        print("\ninterrupted by user\n")
