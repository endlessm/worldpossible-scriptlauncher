# window.py
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

from gi.repository import Gtk
import subprocess
from .updutillogger import UpdutilLogger

@Gtk.Template(resource_path='/org/worldpossible/updutil/window.ui')
class WorldpossibleUpdutilWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'WorldpossibleUpdutilWindow'

    _log = UpdutilLogger()

    chooser_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chooser_button.connect('clicked', self.on_chooser_clicked)

    def on_chooser_clicked(self, button):
        chooser = Gtk.FileChooserNative()
        chooser.run()
        path = chooser.get_filename()
        self._log.info('Executing script on host system: {}'.format(path))
        subprocess.check_call(['flatpak-spawn', '--host', 'pkexec', path])
