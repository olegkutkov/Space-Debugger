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
#vim:
#set expandtab
#set tabstop=4

import json
import gettext
from common_data import DEVICE_ALERTS_KEY
from common_data import DEVICE_FEATURES_KEY
from common_data import DEVICE_CONFIG_KEY
_ = gettext.gettext

''' Basic class for all entities like Dishy, Router, Local device '''
class Entity:
    def __init__(self, name, reachable, cloud_access):
        self.name = name
        self.reachable = reachable
        self.cloud_access = cloud_access

    def get_module_readable_name(self):
        return _(self.name)

    def is_reachable(self):
        return self.reachable

    def is_local_access(self):
        return not self.cloud_access

    def get_access_type(self):
        return _('Remote access') if self.cloud_access else _('Local access')

    ''' This method is widely used in all modules '''
    def yes_or_no(self, bool_val):
        return _('Yes') if bool_val else _('No')

    def get_device_image_file(self):
        return 'resources/devices/entity_astl.png'

    def is_sx_device(self):
        return False

    def get_additional_data(self, result):
        return False

''' Basic class for additional data plugins '''
class EntityModule:
    def __init__(self):
        self.data_ready = False

    def yes_or_no(self, bool_val):
        return _('Yes') if bool_val else _('No')

    def has_img(self):
        return False

    def is_data_ready(self):
        return self.data_ready

''' This module used both for Dishy and router so I moved it here '''
def camel_case_split(data):
    words = [[data[0]]]

    for c in data[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    return [''.join(word) for word in words]

def words_to_str(words):
    good_str = ''

    for word in words:
        good_str += word + ' '

    good_str = good_str.capitalize()

    return good_str

class ModuleAlerts(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        self.no_alerts = False

        if DEVICE_ALERTS_KEY not in json_object:
            self.no_alerts = True

        self.data = []
        alerts_data = json_object[DEVICE_ALERTS_KEY]

        self.words = []
 
        for alert in alerts_data:
           if alerts_data[alert]:
                self.words = camel_case_split(alert) 
                self.data.append([' ', words_to_str(self.words)])

        self.no_alerts = not len(self.data)
        self.data_ready = True

    def get_name(self):
        return 'Alerts'

    def get_data(self):
        if self.no_alerts:
            return [ _('Alerts'), [[' ', _('No alerts')]] ]

        return [ _('Alerts'), self.data ]

class ModuleConfig(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        self.no_config = False

        if DEVICE_CONFIG_KEY not in json_object:
            self.no_config = True

        self.data = []
        config_data = json_object[DEVICE_CONFIG_KEY]

        for cfg in config_data:
            if config_data[cfg]:
                self.words = camel_case_split(cfg)
                self.data.append([' ', words_to_str(self.words)])

        self.no_config = not len(self.data)
        self.data_ready = True

    def get_name(self):
        return 'Config'

    def get_data(self):
        if self.no_config:
            return [ _('Config'), [[' ', _('No config exposed')]] ]

        return [ _('Config'), self.data ]

class Features(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        self.no_features = False

        if DEVICE_FEATURES_KEY not in json_object:
            self.no_features = True

        self.data = []
        features_data = json_object[DEVICE_FEATURES_KEY]

        for feature in features_data:
            if features_data[feature]:
                self.words = camel_case_split(feature)
                self.data.append([' ', words_to_str(self.words)])

        self.no_features = not len(self.data)
        self.data_ready = True

    def get_name(self):
        return 'Features'

    def get_data(self):
        if self.no_features:
            return [ _('Features'), [[' ', _('No features')]] ]

        return [ _('Features'), self.data ]
