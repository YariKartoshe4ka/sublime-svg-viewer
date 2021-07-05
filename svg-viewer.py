import sublime
import sublime_plugin

from .converter import Svg2PngConverter

def plugin_loaded():
    global settings, converter
    settings = sublime.load_settings('svg-viewer.sublime-settings')
    converter = Svg2PngConverter(settings)


class SvgViewerViewSvgCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        name = self.view.window().active_view().file_name()

        output_file_name = converter.convert(name)

        open_picture_in_preview_mode = settings.get('open_picture_in_preview_mode', True)
        always_view_svg_as_picture = settings.get('always_view_svg_as_picture', False)

        if output_file_name:
            flags = sublime.TRANSIENT if open_picture_in_preview_mode and not always_view_svg_as_picture else 0
            self.view.window().open_file(output_file_name, flags=flags)
