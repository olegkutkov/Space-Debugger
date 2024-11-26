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

from entity import *
import gettext
import datetime

_ = gettext.gettext

#

PROGRAM_NAME = 'Space Debugger'
PROGRAM_VERSION = '0.7'

PROGRAM_AUTHOR = 'Oleg Kutkov'
PROGRAM_EMAIL = '<contact@olegkutkov.me>'
PROGRAM_WEBSITE = 'olegkutkov.me'
PROGRAM_START_YEAR = 2023

#

class AboutApp(Entity):
    def __init__(self):
        self.reachable = True

        print('Loading About')

    def get_device_image_file(self):
        return 'resources/devices/about.png'

    def is_sx_device(self):
        return False

    def get_module_readable_name(self):
        return _('About')

    def get_readable_params(self, result):
        result[' '] = PROGRAM_NAME + ' v' + PROGRAM_VERSION
        result['  '] = ''
        result['Author'] = PROGRAM_AUTHOR + ' ' + PROGRAM_EMAIL
        result['Website'] = PROGRAM_WEBSITE
        result['Years'] = str(PROGRAM_START_YEAR) + '-' + str(datetime.date.today().year)

