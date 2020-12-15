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

from gi.repository import Gtk, Gio, GLib
from .updutillogger import UpdutilLogger
import os

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
    save_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chooser_button.connect('clicked', self.on_chooser_clicked)
        self.save_button.connect('clicked', self.on_save_clicked)

    def reset(self):
        self.success_result_label.hide()
        self.success_result_label.set_text('')
        self.failure_result_label.hide()
        self.failure_result_label.set_text('')
        self.output_label.hide()
        self.output_window.hide()
        self.output_buffer.set_text('')
        self.path_entry.set_text('')
        self.save_button.hide()

    def on_chooser_clicked(self, button):
        self.reset()

        chooser = Gtk.FileChooserNative.new('Choose Script', self,
                                            Gtk.FileChooserAction.OPEN,
                                            'Run', None)
        res = chooser.run()
        if res != Gtk.ResponseType.ACCEPT:
            return

        path = chooser.get_filename()
        self.path_entry.set_text(path)

        self.chooser_button.set_sensitive(False)

        popen_args = []
        if os.path.isfile('/.flatpak-info'):
            popen_args += ['flatpak-spawn', '--host']
        popen_args += ['pkexec']
        if not os.access(path, os.X_OK):
            popen_args += ['bash']
        popen_args += [path]
        self._log.info('Executing command: {}'.format(' '.join(popen_args)))

        try:
            proc = Gio.Subprocess.new(popen_args,
                                      Gio.SubprocessFlags.STDOUT_PIPE |
                                      Gio.SubprocessFlags.STDERR_MERGE)
            proc.communicate_utf8_async(None, None, self.on_process_exit, None)
        except GLib.Error as err:
            self.failure_result_label.set_text('Error executing script: {}'.format(err.message))
            self.failure_result_label.show()
            self.chooser_button.set_sensitive(True)

    def on_process_exit(self, proc, res, data=None):
        success = False
        try:
            success, stdout, _ = proc.communicate_utf8_finish(res)
        except GLib.Error as err:
            error_message = err.message

        if success:
            exit_status = proc.get_exit_status()
            # Check the exit status. In the case of 126 or 127 it is probably
            # from pkexec not the script itself. 127 is returned when the
            # script lacks the executable bit in its permissions, but that is
            # checked above.
            if exit_status == 0:
                self.success_result_label.set_text('Result from script: ✓ Success')
                self.success_result_label.show()
            elif exit_status == 127:
                self.failure_result_label.set_text('Error obtaining authorization')
                self.failure_result_label.show()
            elif exit_status == 126:
                self.failure_result_label.set_text('Error obtaining authorization: user dismissed dialog')
                self.failure_result_label.show()
            else:
                self.failure_result_label.set_text('Result from script: ✗ Failure (code {})'.format(exit_status))
                self.failure_result_label.show()

            self.output_label.show()
            self.output_window.show()
            self.output_buffer.set_text(stdout)
            self.save_button.show()
        else: # subprocess failed for some reason other than exit status
            self.failure_result_label.set_text('Result from script: ✗ Failure ({})'.format(error_message))
            self.failure_result_label.show()

        self.chooser_button.set_sensitive(True)

    def on_save_clicked(self, button):
        chooser = Gtk.FileChooserNative.new('Save Log', self,
                                            Gtk.FileChooserAction.SAVE,
                                            None, None)
        chooser.set_do_overwrite_confirmation(True)

        script_path = self.path_entry.get_text()
        script_name = GLib.path_get_basename(script_path)
        if len(script_name) > 0:
            chooser.set_current_name(script_name + '.log')

        res = chooser.run()
        if res != Gtk.ResponseType.ACCEPT:
            return

        path = chooser.get_filename()
        start, end = self.output_buffer.get_bounds()
        buffer_text = self.output_buffer.get_text(start, end, True)
        # FIXME: Catch errors here and print them?
        GLib.file_set_contents(path, buffer_text.encode('utf-8'))
