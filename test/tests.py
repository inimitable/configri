#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""""""
from os import path

import pytest

from backends import JSONBackend, TOMLBackend
from main.configmanager import ConfigManager

current_dir = path.dirname(__file__)


@pytest.fixture
def config_manager():
    return ConfigManager(config_file=path.join(current_dir, "config.json"))


def test_config_load_or_create():
    for backend, ext in [(JSONBackend, "json"), (TOMLBackend, "toml")]:
        back = backend(path.join(current_dir, f"config.{ext}"))
        data = {"name": "BaseConfig", "version": 13, "use_always": True}
        back.create(data)
        data = {"name": "BaseConfig", "version": 22, "use_always": False}
        data, created = back.load_or_create(data)
        assert data["version"] == 13


def test_get_int(config_manager):
    assert isinstance(config_manager.getint("version"), int)
    with pytest.raises(ValueError):
        config_manager.getint("name")


def test_get_bool(config_manager):
    assert config_manager.getbool("use_always") == True
    assert config_manager.getbool("name") == True


def test_get_float(config_manager):
    assert config_manager.getfloat("version") == 13
    with pytest.raises(ValueError):
        config_manager.getfloat("name")
