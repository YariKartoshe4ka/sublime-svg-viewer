import os
import sublime
import sublime_plugin
from tempfile import gettempdir
from hashlib import sha256
from shutil import which



# Sublime plugin events functions
def plugin_loaded():
    SvgViewerViewSvgCommand.settings = sublime.load_settings('svg-viewer.sublime-settings')

def plugin_unloaded():
    sublime.save_settings('svg-viewer.sublime-settings')



# Funcions for work with converters
def get_index_by_converter(converter):
    return list(SvgViewerViewSvgCommand.converters.keys()).index(converter)

def get_converter_by_index(index):
    return list(SvgViewerViewSvgCommand.converters.keys())[index]

def get_converters():
    return list(SvgViewerViewSvgCommand.converters.keys())


# Commands
class SvgViewerViewSvgCommand(sublime_plugin.TextCommand):
    tmp_dir = os.path.join(gettempdir(), 'svg-viewer')

    converters = {
        'inkspace': 'inkspace --export-type=png "{name}" -o "{out}"',
        'cairosvg': 'cairosvg "{name}" -o "{out}" -d {dpi}'
    }

    def run(self, edit):
        converter = self.settings.get('converter', '')

        if not converter or not which(converter) or converter not in self.converters.keys():
            self.view.window().show_quick_panel(get_converters(), self.convert)
        else:
            self.convert(get_index_by_converter(converter))


    def convert(self, index):
        if index >= 0:
            self.settings.set('converter', get_converter_by_index(index))

            if not os.path.exists(self.tmp_dir):
                os.mkdir(self.tmp_dir)

            name = self.view.file_name()
            
            dpi = self.settings.get('dpi', 300)

            out = sha256(open(name).read().encode('utf-8')).hexdigest() + '.png'
            out = os.path.join(self.tmp_dir, out)

            if os.path.exists(out):
                self.view.window().open_file(out, flags=sublime.TRANSIENT if self.settings.get('open_picture_in_preview_mode') else 0)
            else:
                cmd = self.converters[get_converter_by_index(index)].format(name=name, out=out, dpi=dpi)

                os.popen(cmd)

            self.view.window().open_file(out, flags=sublime.TRANSIENT if self.settings.get('open_picture_in_preview_mode') else 0)


class SvgViewerChangeConverter(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().show_quick_panel(get_converters(), self.change)

    def change(self, index):
        SvgViewerViewSvgCommand.settings.set('converter', get_converter_by_index(index))


