"""
   Copyright 2018 InfAI (CC SES)

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

try:
    from connector_client.modules.http_lib import Methods as http
    from connector_client.modules.device_pool import DevicePool
    from connector_client.client import Client
    from lifx.configuration import LIFX_CLOUD_URL, LIFX_API_KEY
    from lifx.cloud_api_monitor import Monitor
    from lifx.logger import root_logger
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
