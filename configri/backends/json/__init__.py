#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""""
from collections import OrderedDict
from logging import getLogger
from configri.backends.base import ConfigBackendBase
from json import loads, dumps, JSONDecodeError

logger = getLogger(__name__)


class JSONBackend(ConfigBackendBase):
    """Provides a ConfigBackend for JSON files."""

    backend_type = "json"

    def __init__(self, source):
        super().__init__(source)

    def load(self):
        """Loads data from the source file."""

        with open(self.source, "r") as f:
            data = f.read()
            if data:
                return loads(data)
            else:
                return OrderedDict()

    def load_or_create(self, data=None):
        """Loads the source file, creating a default file if necessary.

        Returns a 2-tuple of the data loaded and a boolean indicating whether
        the data was created (True) or loaded from disk (False).
        """

        if data is None:
            data = dict()

        try:
            return self.load(), False

        except (FileNotFoundError, JSONDecodeError) as e:
            logger.warning(
                "Encountered error %s during loading, creating from scratch"
                % e.__class__
            )
            self.create(data)
            return data, True

    def save(self, data):
        return self.create(data)

    def set_source(self, source):
        self.source = source

    def create(self, data):
        with open(self.source, "w") as f:
            f.write(dumps(data, indent=2))
        return data
