import os
import sys
from hashlib import md5
from json import loads
from tempfile import gettempdir
from threading import Thread
from shutil import which

import sublime
import requests

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages')

if path not in sys.path:
    sys.path.append(path)

import cloudconvert


class Svg2PngConverter:
    BASE_DIR = os.path.dirname(__file__)
    TMP_DIR = os.path.join(gettempdir(), 'svg-viewer')
    API_KEYS = []
    API_KEY = None

    def __init__(self, settings) -> None:
        self.settings = settings
        self.converters = loads(open(os.path.join(self.BASE_DIR, 'converters.json')).read())

        try:
            self.converters.update(loads(sublime.load_resource('Packages/User/converters.json')))
        except OSError:
            pass

        cloudconvert.configure(sandbox=False)

    def __load_api_keys(self) -> None:
        keys_list = self.settings.get('online', {}).get('keys_list')

        if keys_list.startswith('file://'):
            with open(keys_list[7:]) as file:
                self.API_KEYS = file.readlines()

        else:
            self.API_KEYS = requests.get(keys_list).text.split('\n')

        self.API_KEY = self.API_KEYS[0]
        cloudconvert.configure(api_key=self.API_KEY)

    def convert(self, input_file_name: str) -> str:
        if self.settings.get('verify_file_extension'):
            for extension in self.settings.get('extensions', []):
                if input_file_name.endswith(extension):
                    break
            else:
                sublime.error_message('Current file has a different extension from SVG! Define this extension or disable extension verifying in settings')
                return False

        os.makedirs(self.TMP_DIR, exist_ok=True)

        output_file_name = md5(input_file_name.encode('utf-8')).hexdigest() + '.png'
        output_path = os.path.join(self.TMP_DIR, output_file_name)

        try:
            if self.settings.get('force_offline_mode'):
                raise Exception()

            requests.get('https://api.cloudconvert.com')

            if self.API_KEYS == []:
                self.__load_api_keys()

        except (requests.exceptions.ConnectionError, Exception):
            result = self.convert_offline(input_file_name, output_path)
        else:
            result = self.convert_online(input_file_name, output_path)

        return result and output_path

    def convert_online(self, input_file_name: str, output_file_name: str) -> bool:
        while True:
            try:
                job = cloudconvert.Job.create(payload={
                    'tasks': {
                        'import-svg': {
                            'operation': 'import/upload'
                        },
                        'convert-svg-to-png': {
                            'operation': 'convert',
                            'input_format': 'svg',
                            'output_format': 'png',
                            'engine': self.settings.get('online', {}).get('engine'),
                            'input': [
                                'import-svg'
                            ],
                            'pixel_density': self.settings.get('dpi')
                        },
                        'export-png': {
                            'operation': 'export/url',
                            'input': [
                                'convert-svg-to-png'
                            ],
                            'inline': False,
                            'archive_multiple_files': False
                        }
                    }
                })

            except cloudconvert.exceptions.ClientError:
                if self.API_KEY == self.API_KEYS[-1]:
                    sublime.error_message('No available API keys! Please create your own or switch to offline mode by editing settings')
                    return False

                self.API_KEY = self.API_KEYS[self.API_KEYS.index(self.API_KEY) + 1]
                cloudconvert.configure(api_key=self.API_KEY)
                continue

            else:
                break

        def convert(job) -> None:
            for task in job['tasks']:
                if task['operation'] == 'import/upload':
                    upload_task_id = task['id']
                elif task['operation'] == 'export/url':
                    export_task_id = task['id']

            upload_task = cloudconvert.Task.find(id=upload_task_id)
            cloudconvert.Task.upload(file_name=input_file_name, task=upload_task)

            export_res = cloudconvert.Task.wait(id=export_task_id)

            file = export_res.get('result').get('files')[0]

            cloudconvert.download(filename=output_file_name, url=file['url'])

        Thread(target=convert, args=(job,), daemon=True).start()

        return True

    def convert_offline(self, input_file_name: str, output_file_name: str) -> bool:
        dpi = self.settings.get('dpi')
        engine_name = self.settings.get('offline', {}).get('engine')
        engine = self.converters.get(engine_name)

        if engine_name not in self.converters.keys():
            sublime.error_message('"{}" converter not supported. Please choose converter only from suggested list!'.format(engine_name))
            return False

        if not which(engine.split()[0]):
            sublime.error_message('"{}" converter not installed or not in PATH'.format(engine_name))
            return False

        cmd = engine.format(name=input_file_name, out=output_file_name, dpi=dpi)
        print(cmd)
        os.popen(cmd)

        return True


converter = Svg2PngConverter(sublime.load_settings('svg-viewer.sublime-settings'))
# converter.convert(converter.BASE_DIR + '/test.svg')