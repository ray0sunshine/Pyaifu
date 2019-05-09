import json
import os

main_config = 'helper/config/main_config.json'


class Config:
    i = None

    dataNames = [
        'window',
        'user',
        'pass',
        'pixel_threshold'
    ]

    def __init__(self):
        Config.i = self
        if not os.path.exists(main_config):
            print('creating new main_config - fill out ./' + main_config + ' and restart')
            o = {}
            for dataName in self.dataNames:
                o[dataName] = ''
            self.createConfig(o, main_config)

        with open(main_config, 'r') as config:
            self.data = json.load(config)

    def createConfig(self, o, name):
        with open(name, 'w') as config:
            json.dump(o, config, indent=4)
