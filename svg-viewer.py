import os
from json import loads

import sublime
import sublime_plugin

from .converter import Svg2PngConverter


def plugin_loaded():
    """ Loads plugin and creates all necessary objects """

    # Getting directory where current script is stored
    base_dir = os.path.dirname(os.path.abspath(__file__))

    global settings, converters, converter

    # Loading configurations
    settings = sublime.load_settings('svg-viewer.sublime-settings')

    with open(os.path.join(base_dir, 'converters.json'), encoding='utf-8') as file:
        converters = loads(file.read())

    try:
        converters.update(loads(sublime.load_resource('Packages/User/converters.json')))
    except Exception:
        pass

    # Creating an instance of converter
    converter = Svg2PngConverter(settings, converters)


class SvgViewerViewSvgCommand(sublime_plugin.TextCommand):
    """ Shows binary (PNG) picture by converting it from SVG """

    def is_visible(self):
        name = self.view.file_name()
        for extension in settings.get('extensions'):
            if name is not None and name.endswith(extension):
                return True
        return False

    def run(self, edit):  # noqa: U100
        # Getting full path to current file
        window = self.view.window()
        if window is None:
            return

        view = window.active_view()
        if view is None:
            return

        name = view.file_name()
        if name is None:
            return

        # Getting full path to generated PNG
        output_file_name = converter.convert(name)

        # Getting view settings
        open_picture_in_preview_mode = settings.get('open_picture_in_preview_mode', True)
        always_view_svg_as_picture = settings.get('always_view_svg_as_picture', False)

        # If picture was generated successfully, create view
        if output_file_name:
            flags = sublime.TRANSIENT * (
                open_picture_in_preview_mode and not always_view_svg_as_picture
            )
            window.open_file(output_file_name, flags=flags)


class SvgViewerChangeOfflineConverterCommand(sublime_plugin.TextCommand):
    """ Changes offline converter to another one from supported converters """

    def run(self, edit):  # noqa: U100
        # Setting engines from loaded converters dictionary
        self.engines = list(converters.keys())

        window = self.view.window()
        if window is None:
            return

        # Opening a panel with suggested engines
        window.show_quick_panel(self.engines, self.on_done)

    def on_done(self, index: int):
        # If index less than 0, panel was closed without selecting
        if index < 0:
            return

        # Getting dictionary with offline settings
        offline = settings.get('offline')

        # Setting new engine and updating offline settings
        offline['engine'] = self.engines[index]
        settings.set('offline', offline)

        # Saving settings
        sublime.save_settings('svg-viewer.sublime-settings')


class SvgViewerChangeOnlineConverterCommand(sublime_plugin.TextCommand):
    """ Changes online converter to another one from supported converters """

    def run(self, edit):  # noqa: U100
        # Setting engines which are available on cloudconvert.com
        self.engines = ['imagemagick', 'inkscape', 'chrome', 'graphicsmagick', 'rsvg']

        window = self.view.window()
        if window is None:
            return

        # Opening a panel with suggested engines
        window.show_quick_panel(self.engines, self.on_done)

    def on_done(self, index: int):
        # If index less than 0, panel was closed without selecting
        if index < 0:
            return

        # Getting dictionary with online settings
        online = settings.get('online')

        # Setting new engine and updating online settings
        online['engine'] = self.engines[index]
        settings.set('online', online)

        # Saving settings
        sublime.save_settings('svg-viewer.sublime-settings')


class SvgViewerAlwaysViewSvgAsPictureEventListener(sublime_plugin.ViewEventListener):
    """ Always opens SVG files as binary (PNG) pictures """

    def on_load(self):
        window = self.view.window()
        if window is None:
            return

        # If this mode is activated
        if settings.get('always_view_svg_as_picture'):

            # Checking file extension with the specified in the settings
            name = self.view.file_name()
            for extension in settings.get('extensions'):
                if name is None:
                    return

                if name.endswith(extension):

                    # Convert file and by the previously described command
                    window.run_command('svg_viewer_view_svg')
                    self.view.close()

                    return
