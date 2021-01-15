import os
import sublime
import sublime_plugin
from tempfile import gettempdir
from hashlib import sha256
from shutil import which
from json import load



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
    BASE_DIR = os.path.dirname(__file__)
    TMP_DIR = os.path.join(gettempdir(), 'svg-viewer')
    converters = load(open(os.path.join(BASE_DIR, 'converters.json')))

    def run(self, edit):
        converter = self.settings.get('converter', None)
        
        if converter:
            if not which(converter):
                sublime.error_message('"{}" converter not installed or not in PATH'.format(converter))
            elif converter not in self.converters.keys():
                sublime.error_message('"{}" converter not supported. Please choose converter only from list!'.format(converter))
            else:
                self.convert(get_index_by_converter(converter))
        else:
            self.view.window().show_quick_panel(get_converters(), self.convert)


    def convert(self, index):
        if index < 0:
            return

        self.settings.set('converter', get_converter_by_index(index))

        if not os.path.exists(self.TMP_DIR):
            os.mkdir(self.TMP_DIR)

        name = self.view.file_name()
        
        dpi = self.settings.get('dpi', 300)

        out = sha256(open(name).read().encode('utf-8')).hexdigest() + '.png'
        out = os.path.join(self.TMP_DIR, out)

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


