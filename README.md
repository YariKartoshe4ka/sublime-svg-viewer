# SVG Viewer



### About

SVG Viewer is Sublime Text 3 plugin for viewing SVG files as pictures



### Installing

###### Plugin

1. Make sure you already have [Package Control](https://packagecontrol.io/) installed
2. Open command pallete by pressing <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>
3. Choose "**Package Control: Install Package**" and then press <kbd>Enter</kbd>
4. Select "**SVG Viewer**" and press <kbd>Enter</kbd>

###### Converter

After installing plugin, you need install SVG to PNG converter<br>
By default we support these converters:

- [CairoSVG](https://github.com/Kozea/CairoSVG)
- [Inkscape](https://inkscape.org/)

But you can [add](#contribution) another converter



### Using

1. Open SVG file
2. Open command pallete and select "**SVG Viewer: View SVG**"
3. (if fisrt run) Choose SVG converter from the suggested converters
4. Profit!


### Settings

If you want edit settings, key bindings or converters, do:<br>
Preferences &#8594; Package Settings &#8594; Settings / Key Bindings / Converters - Edit


### Contribution

If you use another SVG to PNG converter, do:

1. Fork this repository
2. Generate command and name of your converter, such as this
```json
{
    "converter": "converter --input-file \"{name}\" --output-file \"{out}\" --dpi {dpi}"
}
```
3. Add this string to the end of [converters.json](converters.json) file
4. Add a link to your converter in the push-request description
5. Send push-request
