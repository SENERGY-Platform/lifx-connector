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

if __name__ == '__main__':
    exit('Please use "client.py"')

try:
    from connector_lib.modules.http_lib import Methods as http
    from connector_lib.client import Client
    from connector_lib.device import Device
    from lifx.configuration import LIFX_API_KEY, LIFX_CLOUD_URL, SEPL_DEVICE_TYPE
    from connector_lib.modules.device_pool import DevicePool
    from lifx.logger import root_logger
except ImportError as ex:
    exit("{} - {}".format(__name__, ex.msg))
import json, time
from threading import Thread


logger = root_logger.getChild(__name__)


class Monitor(Thread):
    _known_devices = dict()

    def __init__(self):
        super().__init__()
        unknown_devices = self._queryLifxCloud()
        self._evaluate(unknown_devices)
        self.start()


    def run(self):
        while True:
            time.sleep(120)
            unknown_devices = self._queryLifxCloud()
            self._evaluate(unknown_devices)


    def _queryLifxCloud(self):
        unknown_lights = dict()
        response = http.get(
            '{}/lights/all'.format(
                LIFX_CLOUD_URL
            ),
            headers={
                'Authorization': 'Bearer {}'.format(LIFX_API_KEY),
            }
        )
        if response.status == 200:
            lights = json.loads(response.body)
            for light in lights:
                light_id = light.get('id')
                unknown_lights[light_id] = light
        else:
            logger.error("could not query lights - '{}'".format(response.status))
        return unknown_lights


    def _diff(self, known, unknown):
        known_set = set(known)
        unknown_set = set(unknown)
        missing = known_set - unknown_set
        new = unknown_set - known_set
        changed = {k for k in known_set & unknown_set if known[k] != unknown[k]}
        return missing, new, changed


    def _evaluate(self, unknown_devices):
        missing_devices, new_devices, changed_devices = self._diff(__class__._known_devices, unknown_devices)
        if missing_devices:
            for missing_device_id in missing_devices:
                logger.info("can't find '{}' with id '{}'".format(__class__._known_devices[missing_device_id].get('label'), missing_device_id))
                try:
                    Client.delete(missing_device_id)
                except AttributeError:
                    DevicePool.remove(missing_device_id)
        if new_devices:
            for new_device_id in new_devices:
                name = unknown_devices[new_device_id].get('label')
                logger.info("found '{}' with id '{}'".format(name, new_device_id))
                device = Device(new_device_id, SEPL_DEVICE_TYPE, name)
                product = unknown_devices[new_device_id].get('product')
                device.addTag('type', 'Extended color light')
                device.addTag('product', product.get('name'))
                device.addTag('manufacturer', product.get('company'))
                try:
                    Client.add(device)
                except AttributeError:
                    DevicePool.add(device)
        if changed_devices:
            for changed_device_id in changed_devices:
                seconds_since_seen = unknown_devices[changed_device_id].get('seconds_since_seen')
                if seconds_since_seen >= 60:
                    try:
                        Client.disconnect(changed_device_id)
                    except AttributeError:
                        DevicePool.remove(changed_device_id)
                    del unknown_devices[changed_device_id]
                else:
                    device = DevicePool.get(changed_device_id)
                    name = unknown_devices[changed_device_id].get('label')
                    if not name == device.name:
                        device.name = name
                        try:
                            Client.update(device)
                        except AttributeError:
                            DevicePool.update(device)
                        logger.info("name of '{}' changed to {}".format(changed_device_id, name))
        __class__._known_devices = unknown_devices
