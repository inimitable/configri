#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""""

from configri.backends import ConfigBackendBase
from configparser import ConfigParser


class INIBackend(ConfigBackendBase):
    def __init__(self, source, defaults=None):
        self.defaults = defaults
        self.data = dict()
        super().__init__(source)

    def load(self):
        parser = ConfigParser()
        parser.read(self.source)
        _out = dict()
        for key in parser.keys():
            _out[key] = parser[key]
        return _out

    def save(self, data):
        pass

    def set_source(self, source):
        pass

    def create(self, data):
        pass
