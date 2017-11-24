import os, sys, inspect
import_path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"connector_client")))
if import_path not in sys.path:
    sys.path.insert(0, import_path)

try:
    from modules.logger import root_logger
    from modules.http_lib import Methods as http
    from modules.device_pool import DevicePool
    from connector.client import Client
    from lifx.cloud_api_configuration import LIFX_CLOUD_URL, LIFX_API_KEY
    from lifx.cloud_api_monitor import Monitor
except ImportError as ex:
    exit("{} - {}".format(__name__, ex.msg))


logger = root_logger.getChild(__name__)


def router():
    while True:
        task = Client.receive()
        try:
            for part in task.payload.get('protocol_parts'):
                if part.get('name') == 'data':
                    command = part.get('value')
            http_resp = http.put(
                '{}/lights/id:{}/state'.format(
                    LIFX_CLOUD_URL, task.payload.get('device_url')
                ),
                command,
                headers={
                    'Authorization': 'Bearer {}'.format(LIFX_API_KEY),
                    'Content-Type': 'application/json'
                }
            )
            if http_resp.status not in (200, 207):
                logger.error("could not route message to LIFX API - '{}'".format(http_resp.status))
            response = str(http_resp.status)
        except Exception as ex:
            logger.error("error handling task - '{}'".format(ex))
            response = '500'
        Client.response(task, response)


if __name__ == '__main__':
    lifx_cloud_monitor = Monitor()
    connector_client = Client(device_manager=DevicePool)
    router()