import os
from json import loads

import sublime
import sublime_plugin

from .converter import Svg2PngConverter


def plugin_loaded():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    global settings, converters, converter
    settings = sublime.load_settings('svg-viewer.sublime-settings')
    converters = loads(open(os.path.join(BASE_DIR, 'converters.json')).read())

    try:
        converters.update(loads(sublime.load_resource('Packages/User/converters.json')))
    except OSError:
        pass

    converter = Svg2PngConverter(settings, converters)


class SvgViewerViewSvgCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        name = self.view.window().active_view().file_name()

        output_file_name = converter.convert(name)

        open_picture_in_preview_mode = settings.get('open_picture_in_preview_mode', True)
        always_view_svg_as_picture = settings.get('always_view_svg_as_picture', False)

        if output_file_name:
            flags = sublime.TRANSIENT if open_picture_in_preview_mode and not always_view_svg_as_picture else 0
            view = self.view.window().open_file(output_file_name, flags=flags)
            view.set_name(os.path.basename(name))


class SvgViewerChangeOfflineConverterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.engines = list(converters.keys())
        self.view.window().show_quick_panel(self.engines, self.on_done)

    def on_done(self, index: int):
        if index < 0:
            return

        offline = settings.get('offline')
        offline['engine'] = self.engines[index]
        settings.set('offline', offline)
        sublime.save_settings('svg-viewer.sublime-settings')


class SvgViewerChangeOnlineConverterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.engines = ['imagemagick', 'inkscape', 'chrome', 'graphicsmagick', 'rsvg']
        self.view.window().show_quick_panel(self.engines, self.on_done)

    def on_done(self, index: int):
        online = settings.get('online')
        online['engine'] = self.engines[index]
        settings.set('online', online)
        sublime.save_settings('svg-viewer.sublime-settings')


class SvgViewerAlwaysViewSvgAsPictureEventListener(sublime_plugin.ViewEventListener):
    def on_load(self):
        if settings.get('always_view_svg_as_picture'):
            for extension in settings.get('extensions'):
                if self.view.file_name().endswith(extension):
                    self.view.window().run_command('svg_viewer_view_svg')
                    self.view.close()
                    return
