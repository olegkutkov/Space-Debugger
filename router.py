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
from router_data import *

_ = gettext.gettext

''' Starlink Dishy info parser and formatter '''
class Router(Entity):
    def __init__(self, json_object):
        print("Loading Router")

        super().__init__('Router', json_object[ROUTER_REACHABLE_KEY], json_object[ROUTER_CLOUD_ACCESS_KEY]) 

        if self.reachable and not self.parse_device_info(json_object):
            raise Exception(_('Failed to load Router Device Info'))

        self.plugins = []

        if self.reachable:
            self.plugins.append(RouterNetwork(json_object))
            self.plugins.append(ModuleAlerts(json_object))
            self.plugins.append(Features(json_object))
            self.plugins.append(BootInfo(json_object))

    def get_device_image_file(self):
        if self.hw_version not in dev_images:
            return dev_images['unknown']

        return dev_images[self.hw_version]

    def is_sx_device(self):
        return True

    def get_module_readable_name(self):
        return _('Router')

    def get_readable_params(self, result):
        result[_('Hardware revision')] = self.hw_version
        result[_('Router ID')] = self.device_id
        result[_('Software version')] = self.sw_version
        result[_('Manufactured version')] = self.mf_version
        result[_('Development hardware')] = self.yes_or_no(self.is_developer)
        result[_('Anti-Rollback version')] = self.anti_rollback_version
        result[_('Software parts equal')] = self.yes_or_no(self.sw_parts_eq)
        result[' '] = ''

        result[_('Country code')] = self.country_code
        result[_('Device date/time')] = datetime.datetime.fromtimestamp(self.timestamp)
        result[_('Device timezone')] = 'GMT' + str(int(self.utc_off_hours / 60 / 60))
        result[_('Uptime')] = str(self.uptime) + ' ' + _('seconds')
        result[_('Boot count')] = self.boot_count

        result['  '] = ''

        result[_('Aviation')] = self.yes_or_no(self.is_aviation)
        result[_('Aviation conformed')] = self.yes_or_no(self.is_aviation_conformed)
        result[_('Captive portal enabled')] = self.yes_or_no(self.captiva_portal_enabled)

    def parse_device_info(self, json_object):
        if DEVICE_INFO_KEY not in json_object:
            return False

        device_info = json_object[DEVICE_INFO_KEY]
        device_state = json_object[DEVICE_STATE_KEY]

        self.device_id = device_info.get(DEVICE_INFO_ID_KEY, _('Unknown'))
        self.sw_version = device_info.get(DEVICE_INFO_SW_VER_KEY, _('Unknown'))
        self.hw_version = device_info.get(DEVICE_INFO_HW_VER_KEY, _('Unknown'))
        self.mf_version = device_info.get(DEVICE_INFO_MF_VER_KEY, _('Unknown'))
        self.gen_number = device_info.get(DEVICE_INFO_GEN_NUMBER, _('Unknown'))
        self.country_code = device_info.get(DEVICE_INFO_CC_KEY, _('Unknown'))
        self.utc_off_hours = device_info.get(DEVICE_INFO_UTC_OFF_KEY, 0)
        self.sw_parts_eq = device_info.get(DEVICE_INFO_SW_PARTS_EQ_KEY, False)
        self.is_developer = device_info.get(DEVICE_INFO_IS_DEV_KEY, False) 
        self.boot_count = device_info.get(DEVICE_INFO_BOOT_COUNT_KEY, 0)
        self.anti_rollback_version = device_info.get(DEVICE_INFO_ANTI_ROLLBACK_KEY, 0)

        self.timestamp = json_object.get(DEVICE_TIMESTAMP_KEY, 0)
        self.uptime = device_state.get(DEVICE_UPTIME_KEY, 0)

        self.is_aviation = json_object.get(ROUTER_IS_AVIATION_KEY, False)
        self.is_aviation_conformed = json_object.get(ROUTER_IS_AVIATION_CONFORMED_KEY, False)
        self.captiva_portal_enabled = json_object.get(ROUTER_CAPTIVE_PORTAL_ENABLED_KEY, False)

        return True

    def get_additional_data(self, result):
        for plugin in self.plugins:
            if plugin.is_data_ready():
                result[plugin.get_name()] = plugin.get_data() 

''' '''

class RouterNetwork(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        self.wan_ipv4 = json_object.get(ROUTER_WAN_IPV4_ADDRESS_KEY, "0.0.0.0")
        self.wan_ipv6 = json_object.get(ROUTER_WAN_IPV6_ADDRESS_LIST_KEY, [])
        self.dhcp_servers = json_object.get(ROUTER_WAN_DHPS_SERVERS_LIST_KEY, [])
        self.ping_drop_rate = json_object.get(ROUTER_PING_DROP_RATE_KEY, 0)
        self.dish_ping_drop_rate = json_object.get(ROUTER_DISH_PING_DROP_RATE_KEY, 0)
        self.dish_ping_latency_ms = json_object.get(ROUTER_DISH_PING_LATENCY_MS_KEY, 0)
        self.pop_ping_drop_rate = json_object.get(ROUTER_POP_PING_DROP_RATE_KEY, 0)
        self.pop_ping_latency_ms = json_object.get(ROUTER_POP_PING_LATENCY_MS_KEY, 0)

        self.data_ready = True

    def get_name(self):
        return 'Network'

    def get_data(self):
        self.ipv6_list = ', '.join(str(s) for s in self.wan_ipv6)
        self.dhcp_servers_list = ', '.join(str(s) for s in self.dhcp_servers)

        data = [
            [ _('WAN IPv4'), self.wan_ipv4 ],
            [ _('WAN IPv6'), self.ipv6_list],
            #[ _('DHCP servers'), self.dhcp_servers_list],
            [ _('Ping drop rate'), self.ping_drop_rate ],
            [ _('Starlink ping drop rate'), self.dish_ping_drop_rate ],
            [ _('Starlink ping latency, ms'), self.dish_ping_latency_ms ],
            [ _('PoP ping drop rate'), self.pop_ping_drop_rate ],
            [ _('PoP ping latency, ms'), self.pop_ping_latency_ms ]
        ]

        return [ _('Network'), data ]


class BootInfo(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        device_info = json_object[DEVICE_INFO_KEY]

        if ROUTER_BOOT_KEY not in device_info:
            return None

        boot_info = device_info[ROUTER_BOOT_KEY]

        self.last_reason = BootReason(boot_info.get(ROUTER_BOOT_LAST_REASON, 0))
        self.last_count = boot_info.get(ROUTER_BOOT_LAST_COUNT, 0)
        self.count_by_reason_map = boot_info.get(ROUTER_BOOT_COUNT_BY_REASON_MAP_KEY, [])

        self.data_ready = True

    def get_name(self):
        return 'BootInfo'

    def get_data(self):
        data = [
            [ _('Last reboot reason'), boot_reason_str[self.last_reason] ],
            [ _('Last boot count'), self.last_count ]
        ]

        for boot_reason in self.count_by_reason_map:
            boot_reason_code = BootReason(boot_reason[0])
            boot_reason_count = boot_reason[1]
            data.append([ _('Reason') + ': ' + boot_reason_str[boot_reason_code], \
                    _('count by this reason') + ': ' + str(boot_reason_count)])

        return [ _('Boot info'), data ]

