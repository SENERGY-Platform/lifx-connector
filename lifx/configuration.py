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


from simple_conf import configuration, section
from os import getcwd


@configuration
class LifxConf:

    @section
    class Cloud:
        host = "api.lifx.com/v1"
        api_path = "lights"
        api_key = None

    @section
    class Senergy:
        dt_lifx_a19 = None
        st_set_color = None
        st_set_kelvin = None
        st_set_on = None
        st_set_off = None
        st_set_brightness = None
        st_get_status = None

    @section
    class Logger:
        level = "info"

    @section
    class Controller:
        max_command_age = 15

config = LifxConf('lifx.conf', getcwd())


if not all((config.Cloud.host, config.Cloud.api_path, config.Cloud.api_key)):
    exit('Please provide LIFX information')

if not all(
        (
                config.Senergy.dt_lifx_a19,
                config.Senergy.st_set_color,
                config.Senergy.st_set_on,
                config.Senergy.st_set_off,
                config.Senergy.st_set_brightness,
                config.Senergy.st_get_status
        )
):
    exit('Please provide a SENERGY device and service types')
