# Copyright 2020-2021 Mufeed Ali
# Copyright 2020-2021 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from gi.repository import GObject, Gtk

from dialect.define import RES_PATH


@Gtk.Template(resource_path=f'{RES_PATH}/lang-selector.ui')
class DialectLangSelector(Gtk.Popover):
    __gtype_name__ = 'DialectLangSelector'

    # Get widgets
    search = Gtk.Template.Child()
    scroll = Gtk.Template.Child()
    revealer = Gtk.Template.Child()
    recent_list = Gtk.Template.Child()
    separator = Gtk.Template.Child()
    lang_list = Gtk.Template.Child()

    # Propeties
    selected = GObject.Property(type=str)  # Key of the selected lang

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Connect popover closed signal
        self.connect('closed', self._closed)
        # Connect list signals
        self.recent_list.connect('row-activated', self._activated)
        self.lang_list.connect('row-activated', self._activated)
        # Set filter func to lang list
        self.lang_list.set_filter_func(self.filter_func, None, False)
        # Connect search entry changed signal
        self.search.connect('changed', self._update_search)

    def filter_func(self, row, _data, _notify_destroy):
        search = self.search.get_text()
        return bool(re.search(search, row.name, re.IGNORECASE))

    def set_languages(self, languages):
        # Clear list
        children = self.lang_list
        for child in children:
            self.lang_list.remove(child)

        # Load langs list
        for code, name in languages.items():
            row_selected = (code == self.selected)
            self.lang_list.insert(LangRow(code, name.capitalize(), row_selected), -1)

    def insert_recent(self, code, name, position=-1):
        row_selected = (code == self.selected)
        self.recent_list.insert(LangRow(code, name, row_selected), position)

    def clear_recent(self):
        children = self.recent_list
        for child in children:
            self.recent_list.remove(child)

    def refresh_selected(self):
        for lang in self.lang_list:
            lang.selected = (lang.code == self.selected)

    def _activated(self, _list, row):
        # Close popover
        self.popdown()
        # Set selected property
        self.set_property('selected', row.code)

    def _closed(self, _popover):
        # Reset scroll
        vscroll = self.scroll.get_vadjustment()
        vscroll.set_value(0)
        # Clear search
        self.search.set_text('')

    def _update_search(self, _entry):
        search = self.search.get_text()
        if search != '':
            self.revealer.set_reveal_child(False)
        else:
            self.revealer.set_reveal_child(True)
        self.lang_list.invalidate_filter()


class LangRow(Gtk.ListBoxRow):

    def __init__(self, code, name, selected=False, **kwargs):
        super().__init__(**kwargs)

        self.code = code
        self.name = name

        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        label = Gtk.Label()
        label.set_text(self.name)
        label.set_halign(Gtk.Align.START)
        label.set_margin_start(4)
        self.get_style_context().add_class('langselector')
        row_box.prepend(label)
        self.selected_icon = Gtk.Image.new_from_icon_name('object-select-symbolic')
        row_box.prepend(self.selected_icon)
        self.set_child(row_box)
        self.selected = selected

    @property
    def selected(self):
        return self.selected_icon.get_visible()

    @selected.setter
    def selected(self, value):
        self.selected_icon.set_visible(value)
