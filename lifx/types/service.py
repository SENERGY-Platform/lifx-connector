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


__all__ = ('SetPower', 'SetBrightness', 'SetColor', 'GetStatus', 'SetKelvin')


from ..configuration import config
from ..logger import root_logger
from requests import put, get, exceptions
import cc_lib, json, datetime


logger = root_logger.getChild(__name__.split(".", 1)[-1])

converter_pool = dict()


def cloudPut(d_id: str, data: dict):
    try:
        resp = put(
            url="https://{}/{}/id:{}/state".format(config.Cloud.host, config.Cloud.api_path, d_id),
            headers={"Authorization": "Bearer {}".format(config.Cloud.api_key)},
            json=data
        )
        if resp.status_code in (200, 207):
            resp = resp.json()
            if len(resp) < 2:
                if "results" in resp:
                    return False, "ok"
                else:
                    return True, "unknown error"
            else:
                err_msg = dict()
                if "errors" in resp:
                    err_msg.update(resp["errors"])
                if "warnings" in resp:
                    err_msg.update(resp["warnings"])
                return True, json.dumps(err_msg)
        else:
            return True, resp.status_code
    except exceptions.RequestException:
        return True, "could not send request to LIFX cloud"


def cloudGet(d_id: str):
    try:
        resp = get(
            url="https://{}/{}/id:{}".format(config.Cloud.host, config.Cloud.api_path, d_id),
            headers={"Authorization": "Bearer {}".format(config.Cloud.api_key)}
        )
        if resp.status_code == 200:
            try:
                return False, resp.json()
            except KeyError:
                return True, "unknown error"
        else:
            return True, resp.status_code
    except exceptions.RequestException:
        return True, "could not send request to LIFX cloud"


class SetColor(cc_lib.types.Service):
    local_id = "setColor"

    @staticmethod
    def task(device, hue: int, saturation: float, brightness: float, duration: float):
        err, body = cloudPut(
            device.id,
            {
                "power": "on",
                "brightness": brightness / 100,
                "color": {"hue": hue, "saturation": saturation / 100},
                "duration": duration
            }
        )
        if err:
            logger.error("'{}' for '{}' failed - {}".format(__class__.__name__, device.id, body))
        return {"status": int(err)}


class SetKelvin(cc_lib.types.Service):
    local_id = "setKelvin"

    @staticmethod
    def task(device, kelvin: int, brightness, duration: float):
        err, body = cloudPut(
            device.id,
            {
                "power": "on",
                "color": {"kelvin": kelvin},
                "brightness": brightness / 100,
                "duration": duration
             }
        )
        if err:
            logger.error("'{}' for '{}' failed - {}".format(__class__.__name__, device.id, body))
        return {"status": int(err)}


# class SetOn(cc_lib.types.Service):
#     local_id = "setOn"
#
#     @staticmethod
#     def task(device, duration: float):
#         err, body = cloudPut(device.id, {"power": "on", "duration": duration})
#         if err:
#             logger.error("'{}' for '{}' failed - {}".format(__class__.name, device.id, body))
#         return {"status": int(err)}
#
#
# class SetOff(cc_lib.types.Service):
#     local_id = "setOff"
#
#     @staticmethod
#     def task(device, duration: float):
#         err, body = cloudPut(device.id, {"power": "off", "duration": duration})
#         if err:
#             logger.error("'{}' for '{}' failed - {}".format(__class__.name, device.id, body))
#         return {"status": int(err)}


class SetPower(cc_lib.types.Service):
    local_id = "setPower"

    @staticmethod
    def task(device, power: str, duration: float):
        err, body = cloudPut(device.id, {"power": power, "duration": duration})
        if err:
            logger.error("'{}' for '{}' failed - {}".format(__class__.__name__, device.id, body))
        return {"status": int(err)}


class SetBrightness(cc_lib.types.Service):
    local_id = "setBrightness"

    @staticmethod
    def task(device, brightness, duration: float):
        err, body = cloudPut(device.id, {"power": "on", "brightness": brightness / 100, "duration": duration})
        if err:
            logger.error("'{}' for '{}' failed - {}".format(__class__.__name__, device.id, body))
        return {"status": int(err)}


class GetStatus(cc_lib.types.Service):
    local_id = "getStatus"

    @staticmethod
    def task(device):
        payload = {
                "status": 0,
                "power": "",
                "brightness": 0,
                "hue": 0,
                "saturation": 0,
                "kelvin": 0,
                "time": "{}Z".format(datetime.datetime.utcnow().isoformat())
            }
        err, body = cloudGet(device.id)
        if err:
            logger.error("'{}' for '{}' failed - {}".format(__class__.__name__, device.id, body))
        else:
            body = body.pop()
            payload["power"] = body["power"]
            payload["brightness"] = round(body["brightness"] * 100)
            payload["hue"] = body["color"]["hue"]
            payload["saturation"] = body["color"]["hue"]
            payload["kelvin"] = body["color"]["hue"]
        payload["status"] = int(err)
        return payload
