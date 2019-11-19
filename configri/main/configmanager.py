#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""A configurable configuration manager. How about that."""
from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Mapping, Union, Hashable, Any

from configri.utils import try_to_cast, NO_VALUE
from configri.backends import JSONBackend, TOMLBackend


class ConfigManager:
    """A ConfigManager is a configuration data storage object supporting ephemeral changes."""

    _BACKEND_MAP = {"toml": TOMLBackend, "json": JSONBackend}
    BACKENDS_AVAILABLE = [*_BACKEND_MAP]

    def __init__(
            self,
            config_file: Union[Path, str],
            backend: str = "json",
            defaults: Optional[Union[Mapping, None]] = None,
            ):
        """Create a new configuration manager.

        :param config_file: File where persistent configuration data should be stored.
        :param backend: Engine to use to support the configuration manager, from BACKENDS_AVAILABLE.
        :param defaults: Default values to insert into the configuration manager.
        """
        if not defaults:
            defaults = OrderedDict()

        backend_engine = ConfigManager._BACKEND_MAP[backend]
        self.backend = backend_engine(config_file)
        self.defaults = defaults
        self.__saved_data = OrderedDict()
        self.__data_has_changes = False
        self.__unsaved_changes = OrderedDict()
        self.__cached_changed_data = OrderedDict()

        self.reload(force_from_disk=True, use_defaults=True)

    def clear_changes(self) -> None:
        """Reverts all unsaved changes to the dataset."""
        self.__cached_changed_data = None
        self.__unsaved_changes = OrderedDict()
        self.__data_has_changes = False

    @property
    def data(self) -> OrderedDict:
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

    def reload(self, save_changes: bool = False, force_from_disk: bool = False, use_defaults: bool = False) -> None:
        """Reloads the configuration data from the backing file."""
        # Save changes if requested & necessary
        if save_changes and self.__data_has_changes:
            self.save()

        # Clear any change flags and data sets back to their original state
        self.clear_changes()

        # If a forced load-from-disk is required, perform it
        if use_defaults:
            self.__saved_data = self.defaults
        if force_from_disk:
            self.__saved_data, _ = self.backend.load_or_create(self.defaults)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self.__unsaved_changes[key] = value
        self.__data_has_changes = True

    def __getitem__(self, item: Hashable) -> Any:
        if item in self.data:
            return self.data[item]
        else:
            raise ValueError("no item with name '%s' in config" % item)

    def get(self, item: Hashable, default: Any) -> Any:
        """A dict-like get method."""
        if item in self.data:
            return self[item]
        else:
            return default

    def get_int(self, item: Hashable, default: Any = NO_VALUE) -> Any:
        """Gets an item from the configuration data, attempting to return it as an int."""
        return try_to_cast(self[item], int, default=default)

    def get_bool(self, item: Hashable, default: Any = NO_VALUE) -> Any:
        """Gets an item from the configuration data, attempting to return it as a bool."""
        return try_to_cast(self[item], bool, default=default)

    def get_float(self, item: Hashable, default: Any = NO_VALUE) -> Any:
        """Gets an item from the configuration data, attempting to return it as a float."""
        return try_to_cast(self[item], float, default=default)

    def save(self) -> None:
        """Saves all changes to the dataset."""
        self.__saved_data = self.backend.save(self.data)
        self.clear_changes()

    def update(self, *dicts: Mapping) -> None:
        """Updates the configuration data from one or many dictionaries."""
        if not dicts:
            return
        for dct in dicts:
            self.__unsaved_changes.update(dct)
        self.__data_has_changes = True

    def __str__(self) -> str:
        return f"ConfigManager({self.backend.source}, {self.backend.backend_type}, ...)"

    def __repr__(self) -> str:
        return f"ConfigManager({self.backend.source}, {self.backend.backend_type}, {self.defaults!r})"
