#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""A configurable configuration manager. How about that."""

from utils import try_to_cast
from backends import JSONBackend, TOMLBackend

backend_map = {"toml": TOMLBackend, "json": JSONBackend}

BACKENDS_AVAILABLE = [*backend_map]


class ConfigManager:
    def __init__(self, config_file, backend="json", defaults=None):
        if not defaults:
            defaults = dict()

        self.backend = backend_map[backend](config_file)
        self.defaults = defaults
        self.data = self.backend.load()

    def __getitem__(self, item):
        if item in self.data:
            return self.data[item]
        else:
            raise ValueError("no item with name %s in config" % item)

    def get(self, item, default):
        try:
            return self[item]
        except KeyError:
            return default

    def getint(self, item):
        return try_to_cast(self[item], int)

    def getbool(self, item):
        return bool(self[item])

    def getfloat(self, item):
        """Gets a key, attempting to return it as a float."""
        return try_to_cast(self[item], float)

    def save(self):
        return self.backend.save(self.data)
