#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Ignacio Rodríguez <nachoel01@gmail.com>
# Rafael Cordano <rafael.cordano@gmail.com>
# CeibalJAM! - Uruguay 2013


# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
from sugar.activity import activity
from sugar.activity.widgets import StopButton
from sugar.activity.widgets import ActivityToolbarButton
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toolbarbox import ToolbarBox
from gettext import gettext as _
from agendacanvas import canvas
import agendacanvas
import simplejson
import os
from agendacanvas import AddTelephoneArea



class Agenda(activity.Activity):

    def __init__(self, handle):
        super(Agenda, self).__init__(handle, True)
        tool = ToolbarBox()
        toolbar = tool.toolbar
        activitybtn = ActivityToolbarButton(self)
        self.separator = gtk.SeparatorToolItem()
        self.separator.props.draw = False
        self.separator.set_expand(True)
        stpbtn = StopButton(self)
        self.addbtn = ToolButton('add')
        self.addbtn.connect('clicked', self._show_palette_add_button)
        toolbar.insert(activitybtn, 0)
        toolbar.insert(gtk.SeparatorToolItem(), -1)
        toolbar.insert(self.addbtn, -1)
        toolbar.insert(self.separator, -1)
        toolbar.insert(stpbtn, -1)

        self.canvas = canvas()
        self.toolarea = AddTelephoneArea(self.addbtn, self.canvas)

        self.set_toolbar_box(tool)
        self.set_canvas(self.canvas)
        self.addbtn.set_tooltip(_('Add a new contact'))
        self._create_palette_add_button(self.addbtn)
        self.show_all()

    def _show_palette_add_button(self, button):
        button.props.palette.popup(immediate=True, state=1)

    def _create_palette_add_button(self, button):
        pallete = button.get_palette()
        pallete.set_content(self.toolarea)

    def read_file(self, file_path):
        fd = open(file_path, 'r')
        text = fd.read()
        data = simplejson.loads(text)
        fd.close()
	c = 0
	for x in data['avatars']:
		if os.path.exists(x):
			pass
		else:
			data['avatars'].__setitem__(c, os.path.join(os.getcwd(),
				'avatars','none.svg'))
		c += 1
        current = 0
        for x in data['names']:
            numero = data['telephones'][current]
            edad = data['ages'][current]
            email = data['emails'][current]
            direction = data['directions'][current]
            avatar = data['avatars'][current]
            self.canvas._add(x, numero, edad, email, direction, avatar)
            current += 1

    def write_file(self, file_path):
        data = {}
        data['names'] = agendacanvas.NAMES
        data['telephones'] = agendacanvas.NUMBERS
        data['ages'] = agendacanvas.AGES
        data['emails'] = agendacanvas.EMAILS
        data['directions'] = agendacanvas.DIRECTIONS
        data['avatars'] = agendacanvas.AVATARS

        fd = open(file_path, 'w')
        text = simplejson.dumps(data)
        fd.write(text)
        fd.close()

    def destroy(self):
        for x in os.listdir('.'):
            if 'pyo' in x:
                os.remove(x)
