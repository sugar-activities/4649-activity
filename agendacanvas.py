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

import simplejson
import gtk
from sugar.graphics.toolbutton import ToolButton
from gettext import gettext as _
import gobject
import os
from sugar.graphics.objectchooser import ObjectChooser

NAMES = []
AGES = []
NUMBERS = []
EMAILS = []
DIRECTIONS = []
AVATARS = []

IMAGE = gtk.Image()

icon_theme = gtk.icon_theme_get_default()
icon_theme.append_search_path('icons/')

if __name__ == "__main__":
    a  = gtk.settings_get_default()
    a.set_property('gtk-icon-theme-name', 'sugar')
    a.set_property('gtk-theme-name', 'sugar-100')

def pixbuf(path):
    pix = gtk.gdk.pixbuf_new_from_file_at_size(path, 200, 200)
    return pix


class utils():
    iter_sel = None
    model = None
    entrys = []


class AddTelephoneArea(gtk.VBox):
    def __init__(self, button, canvas):
        super(AddTelephoneArea, self).__init__()
        self.bb = button
        self.canvas = canvas
        self.hbox = gtk.HBox()
        self.nombre = gtk.Entry()
        self.nn = gtk.Label(_('Write a name:'))
        x = gtk.gdk.screen_width() / 2
        self.set_size_request(x, -1)
        self.hbox.pack_start(self.nn, False, False, 6)
        self.hbox.pack_start(self.nombre, True, True, 6)
        self.pack_start(self.hbox)
        self.toolbar = gtk.Toolbar()
        #
        self.toolbar.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
        #
        self.btn = gtk.ToolButton()
        self.btn.set_icon_name('dialog-ok')
        self.btn.connect('clicked', self.add)
        #
        self.separator = gtk.SeparatorToolItem()
        self.separator.props.draw = False
        self.separator.set_expand(True)
        #
        self.toolbar.insert(self.separator, -1)
        self.toolbar.insert(self.btn, -1)
        self.pack_end(self.toolbar)
        self.show_all()

    def add(self, widget):
        name = self.nombre.get_text()
        if name != "":
            self.canvas._add(name)
            self.nombre.set_text("")
            self.bb.props.palette.popdown(True)


class canvas(gtk.HPaned):

    def __init__(self):
        super(canvas, self).__init__()
        ####
        self.toolbar = gtk.Toolbar()
        self.remove = ToolButton('remove')
        self.remove.set_tooltip(_('Remove this contact'))
        self.addbtn = ToolButton('add')
        self.addbtn.connect('clicked', self._show_palette_add_button)

        self.sep = gtk.SeparatorToolItem()
        self.toolarea = AddTelephoneArea(self.addbtn, self)
        self.sep.props.draw = False
        self.sep.set_expand(True)
        self.toolbar.insert(self.sep, -1)
        self.toolbar.insert(self.remove, -1)
        ###
        self.ficha = Ficha()
        self.set1 = Telefonos(self.remove, self.ficha)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add_with_viewport(self.set1)
        self.vbx = gtk.VBox()
        self.vbx.pack_start(self.scroll, True, True, 0)
        self.vbx.pack_end(self.toolbar, False, True, 0)
        self.vbx.set_size_request(gtk.gdk.screen_width() / 3, -1)

        self.add1(self.vbx)
        self.add2(self.ficha)
        self.show_all()
        self.addbtn.set_tooltip(_('Add a new contact'))

        if __name__ == "__main__":
                self.toolbar.insert(self.addbtn, -1)
                if os.path.isfile("users"):
                    self.read_file('users')

        self._create_palette_add_button(self.addbtn)

    def read_file(self, file_path):
        fd = open(file_path, 'r')
        text = fd.read()
        data = simplejson.loads(text)
        fd.close()
        current = 0
        for x in data['names']:
            numero = data['telephones'][current]
            edad = data['ages'][current]
            email = data['emails'][current]
            direction = data['directions'][current]
            avatar = data['avatars'][current]
            self._add(x, numero, edad, email, direction, avatar)
            current += 1

    def _show_palette_add_button(self, button):
        button.props.palette.popup(immediate=True, state=1)

    def _create_palette_add_button(self, button):
        pallete = button.get_palette()
        pallete.set_content(self.toolarea)

    txt = _("Unknown")
    pt = os.path.join(os.getcwd(), 'avatars', 'none.svg')
    td = _("None")

    def _add(self, name, number=txt, age=1, email=td, direct=txt, av=pt):
        self.set1._add_telephone(name, number, age, email, direct, av)
        self.show_all()


class Telefonos(gtk.TreeView):

    def __init__(self, rmbutton, ficha):
        super(Telefonos, self).__init__()
        self.set_property("rules-hint", True)

        self._model = gtk.ListStore(str)
        #
        gobject.timeout_add(10, self.check)
        #
        self.ficha = ficha
        self.btn = rmbutton
        self.btn.connect('clicked', self.remove)
        #
        self.selection = self.get_selection()
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        self.selection.set_select_function(self.user_press)
        #
        self.set_model(self._model)
        #
        self.user = gtk.CellRendererText()
        self.user.set_property('editable', False)
        self.users = gtk.TreeViewColumn(_("Contacts:"))
        self.users.pack_start(self.user, True)
        self.append_column(self.users)
        #
        self.current = 0
        self.users.add_attribute(self.user, 'text', 0)
        self.show_all()

    def user_press(self, selection):
        iter_sel = self._model.get_iter(selection)
        name = self._model.get_value(iter_sel, 0)
        utils.iter_sel = iter_sel
        utils.model = self._model
        echo = False
        a = 0
        while not echo:
            if name == NAMES[a]:
                    utils.current = a
                    echo = True
            a += 1
        self.ficha.name_entry.set_text(name)
        self.ficha.age_entry.set_text(str(AGES[utils.current]))
        self.ficha.telephone_entry.set_text(str(NUMBERS[utils.current]))
        self.ficha.email_entry.set_text(str(EMAILS[utils.current]))
        self.ficha.direction_entry.set_text(str(DIRECTIONS[utils.current]))
        IMAGE.set_from_pixbuf(pixbuf(str(AVATARS[utils.current])))
        IMAGE.show_all()
        for x in list(self.ficha.user):
            self.ficha.user.remove(x)
        self.ficha.user.add(IMAGE)
        self.ficha.user.disconnect(self.ficha.conectado)
        pt = str(AVATARS[utils.current])
        self.ficha.conectado = self.ficha.user.connect('clicked',
                                self.ficha.open, pt)
        self.ficha.show_all()
        return True

    def _add_telephone(self, name, number, age, email, direction, avatar):
        self._model.insert(self.current, [name])
        self.up()
        NAMES.append(name)
        AGES.append(age)
        NUMBERS.append(number)
        EMAILS.append(email)
        DIRECTIONS.append(direction)
        AVATARS.append(avatar)
        IMAGE.set_from_pixbuf(pixbuf(avatar))
        IMAGE.show_all()

        self.show_all()

    def check(self):
        """ Aca nadie se hace el "vivo".. :P """
        model, iter = self.selection.get_selected()
        tipo = str(type(iter))
        if "None" in tipo:
            self.btn.set_sensitive(False)
            self.ficha.name_entry.set_text("")
            self.ficha.show_all()
            self.ficha.set_sensitive(False)
            for x in utils.entrys:
                if not "button" in str(x):
                    x.set_text("")
                else:
                    x.set_text(1)
        else:
            self.btn.set_sensitive(True)
            self.ficha.set_sensitive(True)
        return True

    def remove(self, widget):
        model, iter = self.selection.get_selected()
        d = self._model.get_value(iter, 0)
        self._model.remove(iter)
        NAMES.remove(d)
        self.down()

    def up(self):
        self.current += 1

    def down(self):
        self.current -= 1


class Ficha(gtk.VBox):

    def __init__(self):
        super(Ficha, self).__init__()
        """
        Image - Name -Entry-
        Age  -Entry-
        Telephone -Entry-
        Email -Entry-
        Direction -Entry-
        """
        ###
        self.namee = gtk.Label(_('Name:'))
        self.age = gtk.Label(_('Age:'))
        self.telephone = gtk.Label(_('Telephone:'))
        self.email = gtk.Label('Email:')
        self.direction = gtk.Label(_('Adress:'))

        self.namee.set_size_request(100, -1)
        self.age.set_size_request(100, -1)
        self.telephone.set_size_request(100, -1)
        self.email.set_size_request(100, -1)
        self.direction.set_size_request(100, -1)

        ###
        self.name_entry = gtk.Entry()
        self.user = gtk.Button()
        self.conectado = self.user.connect('clicked', self.open)
        IMAGE.set_size_request(200, 200)
        self.user.add(IMAGE)
        self.age_entry = gtk.SpinButton()

        #
        adj = gtk.Adjustment(1, 1, 90, 1, 10)
        self.age_entry.set_adjustment(adj)
        #
        self.telephone_entry = gtk.Entry()

        self.email_entry = gtk.Entry()
        self.direction_entry = gtk.Entry()
        utils.entrys.append(self.name_entry)
        utils.entrys.append(self.age_entry)
        utils.entrys.append(self.telephone_entry)
        utils.entrys.append(self.email_entry)
        utils.entrys.append(self.direction_entry)
        ##
        for x in utils.entrys:
            x.set_size_request(300, -1)
        ##

        self.windowd = None
        self.namebox = gtk.HBox()
        self.agebox = gtk.HBox()
        self.telephonebox = gtk.HBox()
        self.emailbox = gtk.HBox()
        self.directionbox = gtk.HBox()
        ###
        self.namebox.pack_start(self.user, expand=True, fill=True, padding=6)
        self.namebox.pack_start(self.namee, False, False, 6)
        self.namebox.pack_end(self.name_entry, True, True, 6)
        self.agebox.pack_start(self.age, False, False, 6)
        self.agebox.pack_end(self.age_entry, True, True, 6)
        self.telephonebox.pack_start(self.telephone, False, False, 6)
        self.telephonebox.pack_start(self.telephone_entry, True, True, 6)
        self.emailbox.pack_start(self.email, False, False, 6)
        self.emailbox.pack_end(self.email_entry, True, True, 6)
        self.directionbox.pack_start(self.direction, False, False, 6)
        self.directionbox.pack_end(self.direction_entry, True, True, 6)
        ##
        self.name_entry.connect('activate', self.set_param, NAMES)
        self.name_entry.connect('focus-in-event', self.set_param, NAMES)
        self.name_entry.connect('focus-out-event', self.set_param, NAMES)
        self.telephone_entry.connect('activate', self.set_param, NUMBERS)
        self.telephone_entry.connect('focus-in-event', self.set_param, NUMBERS)
        self.telephone_entry.connect('focus-out-event', self.set_param, NUMBERS)
        self.direction_entry.connect('activate', self.set_param, DIRECTIONS)
        self.direction_entry.connect('focus-in-event',
                                        self.set_param, DIRECTIONS)
        self.direction_entry.connect('focus-out-event',
                            self.set_param, DIRECTIONS)
        self.age_entry.connect('activate', self.set_param, AGES)
        self.age_entry.connect('focus-in-event', self.set_param, AGES)
        self.age_entry.connect('focus-out-event', self.set_param, AGES)
        self.email_entry.connect('activate', self.set_param, EMAILS)        
        self.email_entry.connect('focus-in-event', self.set_param, EMAILS)        
        self.email_entry.connect('focus-out-event', self.set_param, EMAILS)        
      
        ###
        self.pack_start(self.namebox, True, True, 6)
        self.pack_start(self.agebox, True, True, 6)
        self.pack_start(self.telephonebox, True, True, 6)
        self.pack_start(self.emailbox, True, True, 6)
        self.pack_start(self.directionbox, True, True, 6)
        self.show_all()

    def set_param(self, widget, event, lista):
        d = utils.model.get_value(utils.iter_sel, 0)
        echo = False
        a = 0
        while not echo:
            if d == NAMES[a]:
                    utils.current = a
                    echo = True
            a += 1
        if lista == NAMES:
            utils.model.set_value(utils.iter_sel, 0, widget.get_text())
        lista.__setitem__(utils.current, widget.get_text())

    def _set_img(self, widget, win):
        win.destroy()
        chooser = ObjectChooser()
        res = chooser.run()
        if res == gtk.RESPONSE_CANCEL:
            chooser.destroy()
        else:
            chooser.destroy()
            image = gtk.Image()
            ch = chooser.get_selected_object()
            self.user.disconnect(self.conectado)
            path = ch.file_path
            self.conectado = self.user.connect('clicked', self.open, path)
            pix = gtk.gdk.pixbuf_new_from_file_at_size(path, 200, 200)
            image.set_from_pixbuf(pix)
            for x in list(self.user):
                self.user.remove(x)
            self.user.add(image)
            ###
            d = utils.model.get_value(utils.iter_sel, 0)
            echo = False
            a = 0
            while not echo:
                if d == NAMES[a]:
                        utils.current = a
                        echo = True
                a += 1
            AVATARS.__setitem__(utils.current, path)
            ##
            self.show_all()

    def _set_img_button(self, widget, path, win):
        win.destroy()
        image = gtk.Image()
        pix = gtk.gdk.pixbuf_new_from_file_at_size(path, 200, 200)
        image.set_from_pixbuf(pix)
        self.user.disconnect(self.conectado)
        self.conectado = self.user.connect('clicked', self.open, path)
        for x in list(self.user):
            self.user.remove(x)
        ###
        d = utils.model.get_value(utils.iter_sel, 0)
        echo = False
        a = 0
        while not echo:
            if d == NAMES[a]:
                    utils.current = a
                    echo = True
            a += 1
        AVATARS.__setitem__(utils.current, path)
        ###
        self.set_sensitive(True)
        self.user.add(image)
        self.show_all()

    def open(self, widget, path="none"):
        win = gtk.Window(gtk.WINDOW_POPUP)
        av = Avatars(self._set_img_button, self._set_img, win, path)
        win.add(av)
        win.show()


class Avatars(gtk.VBox):
    def __init__(self, btnfunction, loadfunction, win, path="none"):
        super(Avatars, self).__init__()
        win.set_title(_('Select a avatar'))
        win.set_decorated(False)
        win.set_position(gtk.WIN_POS_CENTER)
        y = gtk.gdk.screen_height() - 100
        win.set_size_request(gtk.gdk.screen_width() - 100, y)
        self.win = win
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.hbox = gtk.HBox()
        self.show_all()
        self.function = btnfunction
        self.a = 0
        self.vbx = gtk.VBox()
        self.vbx.pack_start(self.hbox, False, False, 6)
        self.eventbox = gtk.EventBox()
        self.eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        self.eventbox.add(self.vbx)
        scroll.add_with_viewport(self.eventbox)
        
        ####
        # Sugar Style
        ####
        tl = gtk.Toolbar()
        tl.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
        self.loadfromjournal = ToolButton('open-from-journal')
        self.loadfromjournal.set_tooltip(_('Load from journal'))
        self.loadfromjournal.connect('clicked', loadfunction, win)
        self.accept = ToolButton('dialog-ok')
        self.accept.set_tooltip(_('Accept'))
        self.cancel = ToolButton('gtk-cancel')
        self.cancel.set_tooltip(_('Cancel'))
        self.cancel.connect('clicked', lambda x: win.destroy())
        sep = gtk.SeparatorToolItem()
        sep.set_expand(True)
        sep.props.draw = False
        tl.insert(self.loadfromjournal, 0)
        tl.insert(sep, 1)
        tl.insert(self.accept, 2)
        tl.insert(self.cancel, 3)
        tl.set_size_request(55, -1)
        self.pack_start(tl, False, False, 0)
        self.eventbox.add(scroll)
        self.pack_end(scroll, True, True, 0)
        ####
        self.path = None
        self.actual = None
        for x in os.listdir('avatars'):
            if path != "none":
                    if path == os.path.join(os.getcwd(), 'avatars', x):
                        sensitive = False
                    else:
                        sensitive = True
            else:
                sensitive = True
            self._gen_avatars(x, sensitive)
        gobject.timeout_add(10, self._check)

    def _check(self):
        a = str(type(self.path)).lower()
        if 'none' in a:
            self.accept.set_sensitive(False)
        else:
            self.accept.set_sensitive(True)
        return True

    def _gen_avatars(self, name, sensi):
        path = os.path.join(os.getcwd(), 'avatars', name)
        button = gtk.Button()
        if not sensi:
                self.actual = button
        button.set_sensitive(sensi)
        button.set_tooltip_text(path)
        image = gtk.Image()
        pix = gtk.gdk.pixbuf_new_from_file_at_size(path, 100, 100)
        image.set_from_pixbuf(pix)
        button.add(image)
        button.connect('clicked', self._set_path)
        if not self.a + 1 == 6:
            self.hbox.pack_start(button, False, False, 0)
            self.a += 1
        else:
            self.hbox = gtk.HBox()
            self.vbx.pack_start(self.hbox, False, False, 6)
            self.hbox.pack_start(button, False, False, 0)
            self.a = 0
        button.props.has_tooltip = False
        self.show_all()

    def _set_path(self, widget):
        try:
            self.actual.set_sensitive(True)
        except:
            pass
        self.path = widget.get_tooltip_text()
        self.accept.connect('clicked', self.function, self.path, self.win)
        widget.set_sensitive(False)
        self.actual = widget

if __name__ == "__main__":
    win = gtk.Window()
    win.add(canvas())
    win.set_size_request(600, 600)
    win.show_all()

    def destroy(widget, event, file_path="users"):
        data = {}
        data['names'] = NAMES
        data['telephones'] = NUMBERS
        data['ages'] = AGES
        data['emails'] = EMAILS
        data['directions'] = DIRECTIONS
        data['avatars'] = AVATARS

        fd = open(file_path, 'w')
        text = simplejson.dumps(data)
        fd.write(text)
        fd.close()

    win.connect('delete-event', destroy)
    gtk.main()
