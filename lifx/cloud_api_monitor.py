if __name__ == '__main__':
    exit('Please use "client.py"')

try:
    from modules.http_lib import Methods as http
    from modules.logger import root_logger
    from connector.client import Client
    from connector.device import Device
    from lifx.cloud_api_configuration import LIFX_API_KEY, LIFX_CLOUD_URL
    from modules.device_pool import DevicePool
except ImportError as ex:
    exit("{} - {}".format(__name__, ex.msg))
import json, time
from threading import Thread


logger = root_logger.getChild(__name__)


class Monitor(Thread):
    _known_devices = dict()
    _known_groups = dict()

    def __init__(self):
        super().__init__()
        unknown_devices = self._queryLifxCloud()
        if unknown_devices:
            self._evaluate(unknown_devices)
        self.start()


    def run(self):
        while True:
            time.sleep(30)
            unknown_devices = self._queryLifxCloud()
            if unknown_devices:
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
                device = Device(new_device_id, 'iot#8bded448-ef40-44db-88ac-bbf991398a28', name)
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
                connected = unknown_devices[changed_device_id].get('connected')
                if not connected:
                    try:
                        Client.disconnect(changed_device_id)
                    except AttributeError:
                        DevicePool.remove(changed_device_id)
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
