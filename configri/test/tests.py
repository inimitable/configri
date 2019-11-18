#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""""
from os import path
from random import random, choices
from string import digits, punctuation, ascii_letters
from typing import Tuple

import pytest

from configri.main.configmanager import ConfigManager as CMgr

cwd = path.dirname(__file__)
printable_no_whitespace = ascii_letters + digits + punctuation


def call(obj, attr):
    """A syntactically-prettier way to call a method via getattr."""
    return getattr(obj, attr)()


def random_string(length=12):
    """Returns a random string of printable characters."""
    return "".join(choices(printable_no_whitespace, k=length))


def make_config_file(extension):
    file = path.join(cwd, f"config.{extension}")

    # clear contents
    with open(file, "w") as f:
        f.write("")

    return file


@pytest.fixture
def random_key():
    """Returns a random string 12 chars long, suitable for dict keys."""
    return random_string(length=12)


@pytest.fixture
def random_data():
    """Returns a random kind of hashable data, suitable for dict values."""
    selection = random()
    if selection <= 0.33:
        return random_string()
    elif selection <= 0.66:
        return 1, 2, 3, 5, 7, 9, 11, 13, 17
    else:
        return 86_681_492_395


@pytest.fixture()
def new_config_file():
    def inner(extension):
        return make_config_file(extension)

    return inner


@pytest.fixture
def prepopulated_config_managers():
    defaults = {"name": "BaseConfig", "version": 13, "use_always": True}
    return (
        CMgr(
            config_file=path.join(cwd, "config.json"),
            backend="json",
            defaults=defaults,
        ),
        CMgr(
            config_file=path.join(cwd, "config.toml"),
            backend="toml",
            defaults=defaults,
        ),
    )


@pytest.fixture
def clean_config_managers() -> Tuple[CMgr, CMgr]:
    return (
        CMgr(config_file=make_config_file("json"), backend="json"),
        CMgr(config_file=make_config_file("toml"), backend="toml"),
    )


def test_backend_load_or_create(clean_config_managers):
    for mgr in clean_config_managers:
        data = {"name": "BaseConfig", "version": 13, "use_always": True}
        mgr.backend.save(data)
        data = {"name": "BaseConfig", "version": 22, "use_always": False}
        data, created = mgr.backend.load_or_create(data)
        assert data["version"] == 13


def test_get_int(prepopulated_config_managers):
    for mgr in prepopulated_config_managers:
        assert isinstance(mgr.get_int("version"), int)
        with pytest.raises(ValueError):
            mgr.get_int("name")


def test_get_bool(prepopulated_config_managers):
    for mgr in prepopulated_config_managers:
        assert mgr.get_bool("use_always") is True
        assert mgr.get_bool("name") is True


def test_get_float(prepopulated_config_managers):
    for mgr in prepopulated_config_managers:
        assert mgr.get_float("version") == 13
        with pytest.raises(ValueError):
            mgr.get_float("name")


def test_clear_changes(clean_config_managers, random_key, random_data):
    """Ensure that unsaved changes can be cleared without reloading from disk."""
    reset_methods = ["clear_changes", "reload"]

    for reset_method in reset_methods:
        for mgr in clean_config_managers:
            mgr: CMgr

            # Make sure all data structures are set correctly after a temp change
            mgr[random_key] = random_data
            assert random_key not in mgr._ConfigManager__saved_data
            assert random_key in mgr._ConfigManager__unsaved_changes
            assert mgr._ConfigManager__data_has_changes
            assert mgr[random_key] == random_data

            # Call each kind of reset method
            call(mgr, reset_method)

            # Make sure the data has been reset to the right state
            assert mgr.get(random_key, False) is False


def test_save_soft_changes(clean_config_managers, random_key, random_data):
    """Ensure that unsaved changes are correctly persisted when requested."""
    for mgr in clean_config_managers:
        mgr: CMgr

        mgr[random_key] = random_data
        mgr.save()
        assert mgr._ConfigManager__data_has_changes is False
        assert random_key in mgr._ConfigManager__saved_data
        assert random_key not in mgr._ConfigManager__unsaved_changes
        assert mgr[random_key] == random_data

        mgr.clear_changes()

        assert mgr._ConfigManager__data_has_changes is False
        assert random_key in mgr._ConfigManager__saved_data
        assert random_key not in mgr._ConfigManager__unsaved_changes
        assert mgr[random_key] == random_data
