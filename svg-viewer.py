import os
import sublime
import sublime_plugin
from tempfile import gettempdir
from hashlib import sha256
from shutil import which


def plugin_loaded():
    SvgViewerCommand.settings = sublime.load_settings('svg-viewer.sublime-settings')


class SvgViewerCommand(sublime_plugin.TextCommand):
    tmp_dir = os.path.join(gettempdir(), 'svg-viewer')

    converters = {
        'cairosvg': 'cairosvg {} -o {} -d {}'
    }

    def run(self, edit):
        converter = self.settings.get('converter', '')

        if not converter or not which(converter) or converter not in self.converters.keys():
            self.view.window().show_quick_panel(list(self.converters.keys()), self.convert)
        else:
            self.convert(list(self.converters.keys()).index(converter))


    def convert(self, index):
        if index >= 0:
            self.settings.set('converter', list(self.converters.keys())[index])

            if not os.path.exists(self.tmp_dir):
                os.mkdir(self.tmp_dir)

            name = self.view.file_name()
            
            dpi = self.settings.get('dpi', 300)

            out = sha256(open(name).read().encode('utf-8')).hexdigest() + '.png'
            out = os.path.join(self.tmp_dir, out)

            if os.path.exists(out):
                self.view.window().open_file(out, flags=sublime.TRANSIENT)
            else:
                cmd = self.converters[list(self.converters.keys())[index]].format(name, out, dpi)
                print(cmd)

                p = os.popen(cmd)
                exitcode = p.close()

                if exitcode:
                    raise Exception('File not SVG')

            self.view.window().open_file(out, flags=sublime.TRANSIENT)


