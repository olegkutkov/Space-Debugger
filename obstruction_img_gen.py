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

import math 
from PIL import Image, ImageDraw

img_h = 600
img_w = 600

''' Outline box size for data circle '''
nom_outline_box = (10, 10, 590, 590)
max_radius = 290

ang_span = 30

obstruction_line_width = 5

###

''' Draw line from center to the point on circle using angle and distance '''
def line_to_deg(draw, ang_deg, dist):
    ang_rad = math.radians(ang_deg + 270)

    new_x = (dist * math.cos(ang_rad)) + img_w/2
    new_y = (dist * math.sin(ang_rad)) + img_h/2 + 1

    draw.line([(img_w/2, img_h/2), (new_x, new_y)], width=obstruction_line_width, fill='#820000')

''' Generate simple obstructions vizualization '''
def generate_img_from_list(wedge_list):
    img = Image.new(mode="RGB", size=(img_h, img_w))

    draw = ImageDraw.Draw(img)

    ''' Add labels 
        Bitmap font is used, not super readable...
        Fix this with truetype font ?
    '''
    draw.text((1,285), "W")
    draw.text((595,285), "E")
    draw.text((290, 0), "N")
    draw.text((290, 590), "S")

    draw.pieslice(nom_outline_box, start=0, end=360, fill="#0067bc")

    start_sect = 0

    for item in wedge_list:
        val = item * 100
        if val:
            for offset in range(0, ang_span):
                sect_angle = start_sect + offset
                line_to_deg(draw, sect_angle, max_radius * item)

        start_sect = start_sect + ang_span

    draw.line([(img_w/2, 0), (img_w/2, img_h)], fill='white')
    draw.line([(0, img_h/2), (img_w, img_h/2)], fill='white')

    return img

