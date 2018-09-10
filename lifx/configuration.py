if __name__ == '__main__':
    exit('Please use "client.py"')

import os, inspect, configparser

conf_path = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
conf_file = 'lifx.conf'

config = configparser.ConfigParser()


if not os.path.isfile(os.path.join(conf_path, conf_file)):
    print('No config file found')
    config['LIFX'] = {
        'cloud_url': 'https://api.lifx.com/v1',
        'api_key': ''
    }
    config['SEPL'] = {
        'device_type': ''
    }
    with open(os.path.join(conf_path, conf_file), 'w') as cf:
        config.write(cf)
    exit("Created blank config file at '{}'".format(conf_path))


try:
    config.read(os.path.join(conf_path, conf_file))
except Exception as ex:
    exit(ex)


LIFX_CLOUD_URL = config['LIFX']['cloud_url']
LIFX_API_KEY = config['LIFX']['api_key']
SEPL_DEVICE_TYPE = config['SEPL']['device_type']

if not LIFX_API_KEY:
    exit('Please provide a Lifx API key')

if not SEPL_DEVICE_TYPE:
    exit('Please provide a SEPL device type')
