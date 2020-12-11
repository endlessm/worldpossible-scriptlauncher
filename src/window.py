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

from gi.repository import Gtk, Gio
from .updutillogger import UpdutilLogger

@Gtk.Template(resource_path='/org/worldpossible/updutil/window.ui')
class WorldpossibleUpdutilWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'WorldpossibleUpdutilWindow'

    _log = UpdutilLogger()

    chooser_button = Gtk.Template.Child()
    success_result_label = Gtk.Template.Child()
    failure_result_label = Gtk.Template.Child()
    output_label = Gtk.Template.Child()
    output_window = Gtk.Template.Child()
    output_buffer = Gtk.Template.Child()
    path_entry = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chooser_button.connect('clicked', self.on_chooser_clicked)

    def reset(self):
        self.chooser_button.set_sensitive(False)
        self.success_result_label.hide()
        self.success_result_label.set_text('')
        self.failure_result_label.hide()
        self.failure_result_label.set_text('')
        self.output_label.hide()
        self.output_window.hide()
        self.output_buffer.set_text('')
        self.path_entry.set_text('')

    def on_chooser_clicked(self, button):
        self.reset()

        chooser = Gtk.FileChooserNative()
        res = chooser.run()
        if res != Gtk.ResponseType.ACCEPT:
            self.chooser_button.set_sensitive(True)
            return

        path = chooser.get_filename()
        self.path_entry.set_text(path)
        self._log.info('Executing script on host system: {}'.format(path))
        popen_args = ['flatpak-spawn', '--host', 'pkexec', path]
        proc = Gio.Subprocess.new(popen_args,
                                  Gio.SubprocessFlags.STDOUT_PIPE |
                                  Gio.SubprocessFlags.STDERR_MERGE)
        proc.communicate_utf8_async(None, None, self.on_process_exit, None)

    def on_process_exit(self, proc, res, data=None):
        success = False
        try:
            success, stdout, _ = proc.communicate_utf8_finish(res)
        except GLib.Error as err:
            error_message = err.message

        if success:
            exit_status = proc.get_exit_status()
            if exit_status == 0:
                self.success_result_label.set_text('Result from script: ✓ Success')
                self.success_result_label.show()
            else:
                self.failure_result_label.set_text('Result from script: ✗ Failure (code {})'.format(exit_status))
                self.failure_result_label.show()

            self.output_label.show()
            self.output_window.show()
            self.output_buffer.set_text(stdout)
        else: # subprocess failed for some reason other than exit status
            self.failure_result_label.set_text('Result from script: ✗ Failure ({})'.format(error_message))
            self.failure_result_label.show()

        self.chooser_button.set_sensitive(True)
