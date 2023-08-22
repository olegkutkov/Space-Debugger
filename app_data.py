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

import gettext
from enum import Enum
from common_data import *

_ = gettext.gettext

dev_images = {
    'unknown': 'resources/devices/unknown_app.png',
    'ios': 'resources/devices/ios_app.png',
    'android': 'resources/devices/android_app.png',
    'web': 'resources/devices/web_app.png'
}

STATUS_KEY = 'status'
DEVICE_KEY = 'device'
DEVICE_APP_KEY = 'app'
DEVICE_APP_VERSION_KEY = 'version'
DEVICE_APP_ENVIRONMENT_KEY = 'environment'
DEVICE_APP_BUILD_KEY = 'build'
DEVICE_APP_HASH_KEY = 'hash'
DEVICE_APP_TIMESTAMP_KEY = 'timestamp'
DEVICE_APP_FEATURES_KEY = 'features'

DEVICE_PLATFORM_KEY = 'platform'
DEVICE_PLATFORM_OS_KEY = 'os'
DEVICE_PLATFORM_VERSION_KEY = 'version'

DEVICE_TIMESTAMP_KEY = 'timestamp'
DEVICE_UPTIME_KEY = 'uptime'
DEVICE_WIFI_KEY = 'wifi'
DEVICE_WIFI_IP_ADDR_KEY = 'ipAddress'

DEVICE_SENSORS_KEY = 'sensors'

DEVICE_NAME_KEY = 'name'
DEVICE_MODEL_KEY = 'model'
DEVICE_ID_KEY = 'deviceId'

DEVICE_NETWORK_KEY = 'network'
DEVICE_NETWORK_VPN_KEY = 'vpn'
DEVICE_NETWORK_NETINFO_KEY = 'netinfo'
DEVICE_NETWORK_NETINFO_TYPE_KEY = 'type'
DEVICE_NETWORK_NETINFO_IS_CONNECTED_KEY = 'isConnected'
DEVICE_NETWORK_NETINFO_WIFI_ENABLED_KEY = 'isWifiEnabled'
DEVICE_NETWORK_NETINFO_DETAILS_KEY = 'details'
DEVICE_NETWORK_NETINFO_DETAILS_IP_ADDR_KEY = 'ipAddress'
DEVICE_NETWORK_NETINFO_DETAILS_LINK_SPEED_KEY = 'linkSpeed'
DEVICE_NETWORK_NETINFO_DETAILS_FREQ_KEY = 'frequency'
DEVICE_NETWORK_NETINFO_DTAILS_SIGNAL_LEVEL_KEY = 'strength'
DEVICE_NETWORK_NETINFO_DETAILS_BSSID_KEY = 'bssid'
DEVICE_NETWORK_NETINFO_DETAILS_SSID_KEY = 'ssid'
DEVICE_NETWORK_IS_INTERNET_REACHABLE = 'isInternetReachable'
DEVICE_NETWORK_PUBLIC_IP_KEY = 'publicIp'
DEVICE_NETWORK_IS_STARLINK_KEY = 'starlink'
DEVICE_NETWORK_GATEWAY_IP_ADDR_KEY = 'gatewayIp'

