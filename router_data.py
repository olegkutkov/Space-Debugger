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

gettext.bindtextdomain('space-debugger', './locales')
gettext.textdomain('space-debugger')

_ = gettext.gettext

dev_images = {
	'v1': 'resources/devices/router_v1.png',
	'v2': 'resources/devices/router_v2.png'
}

class BootReason(Enum):
    BOOT_REASON_UNKNOWN = 0
    FORGOTTEN = 1
    POWER_CYCLE = 2
    COMMAND = 3
    SOFTWARE_UPDATE = 4
    CONFIG_UPDATE = 5
    UPTIME_FDIR = 6
    REPEATER_FDIR = 7
    AVIATION_ETH_WAN_FDIR = 8
    KERNEL_PANIC = 9
    AVIATION_5M_OUTAGE_FDIR = 10

    @classmethod
    def _missing_(cls, value):
        return cls.BOOT_REASON_UNKNOWN

boot_reason_str = {
    BootReason.BOOT_REASON_UNKNOWN: _('Unknown'),
    BootReason.FORGOTTEN: _('Forgotten'),
    BootReason.POWER_CYCLE: _('Power cycle'),
    BootReason.COMMAND: _('Command'),
    BootReason.SOFTWARE_UPDATE: _('Software update'),
    BootReason.CONFIG_UPDATE: _('Configuration update')
}

ROUTER_KEY = 'router'
ROUTER_REACHABLE_KEY = 'reachable'
ROUTER_CLOUD_ACCESS_KEY = 'cloud'

ROUTER_CAPTIVE_PORTAL_ENABLED_KEY = 'captivePortalEnabled'
ROUTER_IS_AVIATION_KEY = 'isAviation'
ROUTER_IS_AVIATION_CONFORMED_KEY = 'isAviationConformed'

ROUTER_BOOT_KEY = 'boot'
ROUTER_BOOT_COUNT_BY_REASON_MAP_KEY = 'countByReasonMap'
ROUTER_BOOT_LAST_REASON = 'lastReason'
ROUTER_BOOT_LAST_COUNT = 'lastCount'

ROUTER_WAN_IPV4_ADDRESS_KEY = 'ipv4WanAddress'
ROUTER_WAN_IPV6_ADDRESS_LIST_KEY = 'ipv6WanAddressesList'
ROUTER_WAN_DHPS_SERVERS_LIST_KEY = 'dhcpServersList'
ROUTER_PING_DROP_RATE_KEY = 'pingDropRate'
ROUTER_PING_LATENCY_MS_KEY = 'pingLatencyMs'
ROUTER_DISH_PING_DROP_RATE_KEY = 'dishPingDropRate'
ROUTER_DISH_PING_LATENCY_MS_KEY = 'dishPingLatencyMs'
ROUTER_POP_PING_DROP_RATE_KEY = 'popPingDropRate'
ROUTER_POP_PING_LATENCY_MS_KEY = 'popPingLatencyMs'

