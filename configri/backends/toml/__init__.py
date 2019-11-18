#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""A ConfigBackend for working with TOML files."""
from collections import OrderedDict

from toml import dumps, loads, TomlDecodeError
from logging import getLogger
from configri.backends.base import ConfigBackendBase


logger = getLogger(__name__)


class TOMLBackend(ConfigBackendBase):
    """A ConfigBackend for working with TOML files."""

    backend_type = "toml"

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

        except (FileNotFoundError, TomlDecodeError) as e:
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
            f.write(dumps(data))
        return data
