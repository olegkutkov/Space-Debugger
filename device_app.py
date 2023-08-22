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

        app_object = json_object

        if STATUS_KEY in json_object:
          app_object = json_object[STATUS_KEY]

        if DEVICE_APP_KEY not in app_object:
            raise Exception(_('Failed to load device app info'))

        device_app = app_object[DEVICE_APP_KEY]

        self.device_app_version = device_app.get(DEVICE_APP_VERSION_KEY, _('Unknown'))
        self.device_app_environment = device_app.get(DEVICE_APP_ENVIRONMENT_KEY, _('Unknown'))
        self.device_app_build = device_app.get(DEVICE_APP_BUILD_KEY, '')
        self.device_app_hash = device_app.get(DEVICE_APP_HASH_KEY, '')
        self.device_app_timestamp = device_app.get(DEVICE_APP_TIMESTAMP_KEY, 0)        

        self.platform_os = 'unknown'

        if DEVICE_PLATFORM_KEY in app_object:
            self.platform_os = app_object[DEVICE_PLATFORM_KEY].get(DEVICE_PLATFORM_OS_KEY, 'unknown')

        self.plugins = []

        if self.platform_os != 'web' and self.platform_os != 'unknown':
            self.platform_os_version = app_object[DEVICE_PLATFORM_KEY].get(DEVICE_PLATFORM_VERSION_KEY, '')
            self.timestamp = app_object.get(DEVICE_TIMESTAMP_KEY, 0)
            self.uptime = app_object.get(DEVICE_UPTIME_KEY, 0)
            self.device = app_object.get(DEVICE_NAME_KEY, '')
            self.device_model = app_object.get(DEVICE_MODEL_KEY, '')
            self.device_id = app_object.get(DEVICE_ID_KEY, '')
            wifi_section = app_object.get(DEVICE_WIFI_KEY)
            if wifi_section:
                self.wifi_ip = wifi_section.get(DEVICE_WIFI_IP_ADDR_KEY, '0.0.0.0')
                self.wifi_ssid = wifi_section.get(DEVICE_NETWORK_NETINFO_DETAILS_SSID_KEY, '')
            else:
                self.wifi_ip = _('unknown')
                self.wifi_ssid = _('unknown')

            self.plugins.append(DeviceNetwork(app_object))
            self.plugins.append(DeviceSensors(app_object))

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
            result[_('WiFi SSID')] = self.wifi_ssid
            

    def get_additional_data(self, result):
        for plugin in self.plugins:
            if plugin.is_data_ready():
                result[plugin.get_name()] = plugin.get_data() 

'' ''

class DeviceNetwork(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        app_object = json_object

        if STATUS_KEY in json_object:
          app_object = json_object[STATUS_KEY]

        if DEVICE_NETWORK_KEY not in app_object:
            return None

        network = app_object[DEVICE_NETWORK_KEY]
        network_info = app_object[DEVICE_NETWORK_KEY][DEVICE_NETWORK_NETINFO_KEY]
        network_info_details = network_info.get(DEVICE_NETWORK_NETINFO_DETAILS_KEY, None)

        self.is_vpn = network.get(DEVICE_NETWORK_VPN_KEY, False)
        self.gateway_ip = network.get(DEVICE_NETWORK_GATEWAY_IP_ADDR_KEY, '0.0.0.0')
        self.public_ip = network.get(DEVICE_NETWORK_PUBLIC_IP_KEY, '0.0.0.0')
        self.is_starlink_conn = network.get(DEVICE_NETWORK_IS_STARLINK_KEY, False)

        self.net_type = network_info.get(DEVICE_NETWORK_NETINFO_TYPE_KEY, 'wifi')
        self.is_bypass_mode = not network_info.get(DEVICE_NETWORK_NETINFO_WIFI_ENABLED_KEY, True)
        self.is_connected = network_info.get(DEVICE_NETWORK_NETINFO_IS_CONNECTED_KEY, False)
        self.is_internet_available = network_info.get(DEVICE_NETWORK_IS_INTERNET_REACHABLE, False)

        if network_info_details is not None:
            self.ip_addr = network_info_details.get(DEVICE_NETWORK_NETINFO_DETAILS_IP_ADDR_KEY, '0.0.0.0')
            self.local_link_speed = network_info_details.get(DEVICE_NETWORK_NETINFO_DETAILS_LINK_SPEED_KEY, 0)
            self.local_link_speed =  str(self.local_link_speed) + ' Mbps'

            self.wifi_link_freq = network_info_details.get(DEVICE_NETWORK_NETINFO_DETAILS_FREQ_KEY, 0)
            self.wifi_ssid = network_info_details.get(DEVICE_NETWORK_NETINFO_DETAILS_SSID_KEY, '')
            self.wifi_bssid = network_info_details.get(DEVICE_NETWORK_NETINFO_DETAILS_BSSID_KEY, '')
            self.wifi_signal_level = network_info_details.get(DEVICE_NETWORK_NETINFO_DTAILS_SIGNAL_LEVEL_KEY, 150)
        else:
            self.ip_addr = ""
            self.local_link_speed = ""
            self.local_link_speed = ""
            self.wifi_link_freq = ""
            self.wifi_ssid = ""
            self.wifi_bssid = ""
            self.wifi_signal_level = ""

        self.data_ready = True

    def get_name(self):
        return 'DeviceNetwork'

    def get_data(self):
        data = [
            [ _('Local connection type'), self.net_type ],
            [ _('Local connection speed'), self.local_link_speed ],
            [ _('Is VPN'), self.yes_or_no(self.is_vpn) ],
            [ _('Is connected'), self.yes_or_no(self.is_connected) ],
            [ _('Internet available'), self.yes_or_no(self.is_internet_available) ],
            [ _('Connected via Starlink'), self.yes_or_no(self.is_starlink_conn) ],
            [ _('Starlink router bypass mode'), self.yes_or_no(self.is_bypass_mode) ],
            [ _('Local IP address'), self.ip_addr ],
            [ _('Gateway IP address'), self.gateway_ip ],
            [ _('Public IP address'), self.public_ip]
        ]

        if self.net_type == 'wifi':
            wifi_data = [
                [ _('WiFi SSID'), self.wifi_ssid ],
                [ _('WiFi BSSID'), self.wifi_bssid ],
                [ _('WiFi frequency'), self.wifi_link_freq ],
                [ _('WiFi signal strength'), self.wifi_signal_level ]
            ]

            data += wifi_data

        return [ _('Network'), data ]

class DeviceSensors(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        app_object = json_object

        if STATUS_KEY in json_object:
          app_object = json_object[STATUS_KEY]

        if DEVICE_SENSORS_KEY not in app_object:
            return None

        self.sensors_data = app_object[DEVICE_SENSORS_KEY]

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

