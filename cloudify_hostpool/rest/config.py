########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.


DEFAULTS = {

    # default storage configuration is a file path under which the sqlite
    # database will be saved.
    'storage': 'host-pool-data.sqlite'
}


class Config(object):

    def __init__(self, config):
        self._config = config
        self._validate(config)

    @staticmethod
    def _validate(config):
        if 'pool' not in config:
            raise RuntimeError("'pool' property is missing from the "
                               "configuration")

    @property
    def pool(self):
        return self._config['pool']

    @property
    def storage(self):
        return self._config.get('storage', DEFAULTS['storage'])

_instance = None


def configure(config):
    global _instance
    _instance = Config(config)


def get():
    global _instance
    return _instance
