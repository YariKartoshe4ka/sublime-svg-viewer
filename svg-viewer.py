import os
import sublime
import sublime_plugin
from tempfile import gettempdir
from hashlib import md5
from shutil import which
from json import loads


# Sublime plugin events functions
def plugin_loaded():
    SvgViewerViewSvgCommand.settings = sublime.load_settings('svg-viewer.sublime-settings')


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
    converters = loads(sublime.load_resource('Packages/SVG Viewer/converters.json'))

    try:
        converters.update(loads(sublime.load_resource('Packages/User/converters.json')))
    except:
        pass

    def run(self, edit):
        converter = self.settings.get('converter', None)
        
        if converter:
            if not which(self.converters[converter].split(' ')[0]):
                sublime.error_message('"{}" converter not installed or not in PATH'.format(converter))
            elif converter not in self.converters.keys():
                sublime.error_message('"{}" converter not supported. Please choose converter only from suggested list!'.format(converter))
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

        name = self.view.window().active_view().file_name()

        dpi = self.settings.get('dpi', 96)
        open_picture_in_preview_mode = self.settings.get('open_picture_in_preview_mode', True)
        always_view_svg_as_picture = self.settings.get('always_view_svg_as_picture', False)

        out = md5(open(name).read().encode('utf-8')).hexdigest() + '.png'
        out = os.path.join(self.TMP_DIR, out)

        if not os.path.exists(out):
            cmd = self.converters[get_converter_by_index(index)].format(name=name, out=out, dpi=dpi)
            print(cmd)
            os.popen(cmd)

        flags = sublime.TRANSIENT if open_picture_in_preview_mode and not always_view_svg_as_picture else 0
        view = self.view.window().open_file(out, flags=flags)


class SvgViewerChangeConverterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().show_quick_panel(get_converters(), self.change)

    def change(self, index):
        SvgViewerViewSvgCommand.settings.set('converter', get_converter_by_index(index))
        sublime.save_settings('svg-viewer.sublime-settings')



# Events
class SvgViewerAlwaysViewSvgAsPictureEventListener(sublime_plugin.ViewEventListener):
    def on_load(self):
        if SvgViewerViewSvgCommand.settings.get('always_view_svg_as_picture', False):
            if self.view.file_name().endswith('.svg'):
                self.view.window().run_command('svg_viewer_view_svg')
                self.view.close()
