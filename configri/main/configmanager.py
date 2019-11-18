#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""A configurable configuration manager. How about that."""
from collections import OrderedDict
from typing import Optional, Mapping, Union

from configri.utils import try_to_cast, NO_VALUE
from configri.backends import JSONBackend, TOMLBackend

backend_map = {"toml": TOMLBackend, "json": JSONBackend}

BACKENDS_AVAILABLE = [*backend_map]


class ConfigManager:
    def __init__(
        self,
        config_file,
        backend: str = "json",
        defaults: Optional[Union[Mapping, None]] = None,
    ):
        if not defaults:
            defaults = OrderedDict()

        backend_engine = backend_map[backend]
        self.backend = backend_engine(config_file)
        self.defaults = defaults
        self.__saved_data = OrderedDict()
        self.__data_has_changes = False
        self.__unsaved_changes = OrderedDict()
        self.__cached_changed_data = OrderedDict()

        self.reload(force_from_disk=True)

    def clear_changes(self):
        """Reverts all unsaved changes to the dataset."""
        self.__cached_changed_data = None
        self.__unsaved_changes = OrderedDict()
        self.__data_has_changes = False

    @property
    def data(self):
        """A copy of all data with changes overlaid."""
        # Apply changes if necessary
        if self.__data_has_changes:
            self.__cached_changed_data = OrderedDict(
                **self.__saved_data, **self.__unsaved_changes
            )

        # Create the cached data dict if it's missing
        elif not self.__cached_changed_data:
            self.__cached_changed_data = self.__saved_data

        return self.__cached_changed_data

    def reload(self, save_changes=False, force_from_disk=False):
        """Reloads the configuration data from the backing file."""
        # Save changes if requested & necessary
        if save_changes and self.__data_has_changes:
            self.save()

        # Clear any change flags and data sets back to their original state
        self.clear_changes()

        # If a forced load-from-disk is required, perform it
        if force_from_disk:
            self.__saved_data, _ = self.backend.load_or_create(self.defaults)

    def __setitem__(self, key, value):
        self.__unsaved_changes[key] = value
        self.__data_has_changes = True

    def __getitem__(self, item):
        if item in self.data:
            return self.data[item]
        else:
            raise ValueError("no item with name '%s' in config" % item)

    def get(self, item, default):
        """A basic dict-like get method."""
        if item in self.data:
            return self[item]
        else:
            return default

    def get_int(self, item, default=NO_VALUE) -> int:
        return try_to_cast(self[item], int, default=default)

    def get_bool(self, item, default=NO_VALUE):
        return try_to_cast(self[item], bool, default=default)

    def get_float(self, item, default=NO_VALUE):
        """Gets a key, attempting to return it as a float."""
        return try_to_cast(self[item], float, default=default)

    def save(self):
        """Saves all changes to the dataset."""
        self.__saved_data = self.backend.save(self.data)
        self.clear_changes()

    def update(self, *dicts):
        if not dicts:
            return
        for dct in dicts:
            self.__unsaved_changes.update(dct)
        self.__data_has_changes = True

    def __str__(self):
        return f"ConfigManager({self.backend.source}, {self.backend.backend_type}, ...)"

    def __repr__(self):
        return f"ConfigManager({self.backend.source}, {self.backend.backend_type}, {self.defaults!r})"
