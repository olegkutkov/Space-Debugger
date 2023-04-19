#
#   Copyright 2023  Oleg Kutkov <contact@olegkutkov.me>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.  
#
#set expandtab
#set tabstop=4

import json
import gettext
import datetime
from entity import * 
from app_data import *

_ = gettext.gettext

class DeviceApp(Entity):
    def __init__(self, json_object):
        print('Loading Local device')

        super().__init__('App', True, False)

        if DEVICE_APP_KEY not in json_object:
            raise Exception(_('Failed to load device app info'))

        device_app = json_object[DEVICE_APP_KEY]

        self.device_app_version = device_app.get(DEVICE_APP_VERSION_KEY, _('Unknown'))
        self.device_app_environment = device_app.get(DEVICE_APP_ENVIRONMENT_KEY, _('Unknown'))
        self.device_app_build = device_app.get(DEVICE_APP_BUILD_KEY, '')
        self.device_app_hash = device_app.get(DEVICE_APP_HASH_KEY, '')
        self.device_app_timestamp = device_app.get(DEVICE_APP_TIMESTAMP_KEY, 0)        

        self.platform_os = 'unknown'

        if DEVICE_PLATFORM_KEY in json_object:
            self.platform_os = json_object[DEVICE_PLATFORM_KEY].get(DEVICE_PLATFORM_OS_KEY, 'unknown')

        self.plugins = []

        if self.platform_os != 'web' and self.platform_os != 'unknown':
            self.platform_os_version = json_object[DEVICE_PLATFORM_KEY].get(DEVICE_PLATFORM_VERSION_KEY, '')
            self.timestamp = json_object.get(DEVICE_TIMESTAMP_KEY, 0)
            self.uptime = json_object.get(DEVICE_UPTIME_KEY, 0)
            self.device = json_object.get(DEVICE_NAME_KEY, '')
            self.device_model = json_object.get(DEVICE_MODEL_KEY, '')
            self.device_id = json_object.get(DEVICE_ID_KEY, '')
            self.wifi_ip = json_object[DEVICE_WIFI_KEY].get(DEVICE_WIFI_IP_ADDR_KEY, '0.0.0.0')

            self.plugins.append(DeviceNetwork(json_object))
            self.plugins.append(DeviceSensors(json_object))

    def get_device_image_file(self):
        if self.platform_os not in dev_images:
            return dev_images['unknown']

        return dev_images[self.platform_os]
  
    def is_sx_device(self):
        return False

    def get_module_readable_name(self):
        return _('Local device')

    def get_readable_params(self, result):
        result[_('App version')] = self.device_app_version
        result[_('App environment')] = self.device_app_environment
        result[_('App build')] = self.device_app_build
        result[_('App hash')] = self.device_app_hash
        result[_('App timestamp')] = datetime.datetime.fromtimestamp(self.device_app_timestamp)

        result[' '] = ''

        result[_('Platform OS')] = self.platform_os

        if self.platform_os != 'web' and self.platform_os != 'unknown':
            result[_('Platform OS version')] = self.platform_os_version
            result[_('Device')] = self.device
            result[_('Device model')] = self.device_model
            result[_('Device id')] = self.device_id

            result['  '] = ''

            result[_('Device timestamp')] = datetime.datetime.fromtimestamp(self.timestamp)
            result[_('Device uptime')] = self.uptime
            result[_('WiFi IP address')] = self.wifi_ip
            

    def get_additional_data(self, result):
        for plugin in self.plugins:
            if plugin.is_data_ready():
                result[plugin.get_name()] = plugin.get_data() 

'' ''

class DeviceNetwork(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        if DEVICE_NETWORK_KEY not in json_object:
            return None

        network = json_object[DEVICE_NETWORK_KEY]
        network_info = json_object[DEVICE_NETWORK_KEY][DEVICE_NETWORK_NETINFO_KEY]
        network_info_details = network_info[DEVICE_NETWORK_NETINFO_DETAILS_KEY]

        self.is_vpn = network.get(DEVICE_NETWORK_VPN_KEY, False)
        self.gateway_ip = network.get(DEVICE_NETWORK_GATEWAY_IP_ADDR_KEY, '0.0.0.0')

        self.net_type = network_info.get(DEVICE_NETWORK_NETINFO_TYPE_KEY, 'wifi')
        self.is_connected = network_info.get(DEVICE_NETWORK_NETINFO_IS_CONNECTED_KEY, False)
        self.is_internet_available = network_info.get(DEVICE_NETWORK_IS_INTERNET_REACHABLE, False)

        self.ip_addr = network_info_details.get(DEVICE_NETWORK_NETINFO_DETAILS_IP_ADDR_KEY, '0.0.0.0')

        self.data_ready = True

    def get_name(self):
        return 'DeviceNetwork'

    def get_data(self):
        data = [
            [ _('Connection type'), self.net_type ],
            [ _('Is VPN'), self.yes_or_no(self.is_vpn) ],
            [ _('Is connected'), self.yes_or_no(self.is_connected) ],
            [ _('Internet available'), self.yes_or_no(self.is_internet_available) ],
            [ _('IP address'), self.ip_addr ],
            [ _('Gateway IP address'), self.gateway_ip ]
        ]

        return [ _('Network'), data ]

class DeviceSensors(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        if DEVICE_SENSORS_KEY not in json_object:
            return None

        self.sensors_data = json_object[DEVICE_SENSORS_KEY]

        self.data_ready = True

    def get_name(self):
        return 'DeviceSensors'

    def get_data(self):
        data = []

        for sensor in self.sensors_data:
            sensor_info = self.sensors_data[sensor]
            sensor_active = sensor_info['active']
            sensor_available = sensor_info['available']

            sensor_str = _('Available') + ': ' + self.yes_or_no(sensor_available) + \
                            '  ' + _('Active') + ': ' + self.yes_or_no(sensor_active)

            data.append([ sensor, sensor_str ])

        return [ _('Sensors'), data ]

