# main.py
#
# Copyright 2020 Endless OS Foundation LLC
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio

from .window import WorldpossibleScriptLauncherWindow


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='org.worldpossible.ScriptLauncher',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def show_warning_dialog(self, window):
        dialog = Gtk.MessageDialog(window,
                                   Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK,
                                   'This utility allows you to execute scripts with administrator privileges!')
        dialog.format_secondary_text('Only choose files from trusted sources to avoid harming your computer.')
        dialog.run()
        dialog.destroy()

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = WorldpossibleScriptLauncherWindow(application=self)
        win.present()
        self.show_warning_dialog(win)


def main(version):
    app = Application()
    return app.run(sys.argv)
