#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Various utility methods and helpers."""

from os import name as operating_system
from os import environ
from os.path import join, expanduser, expandvars
from pathlib import Path as Pypath
from collections import namedtuple as NamedTuple  # sue me

# Used as a default like None, but in cases where None is a good value to use
#  in real life
class __NO_VALUE:
    pass
NO_VALUE = __NO_VALUE()

def expand(path: str) -> Pypath:
    """`expand` resolves variables in a pathname."""
    return Pypath(expanduser(expandvars(path)))


__XDG_VARS = ["XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME"]
ConfigDirectories = NamedTuple("ConfigDirectories", "config,data,cache")


def _is_xdg_compliant() -> bool:
    """True if the environment explicitly support the XDG standard."""
    if all([var in environ for var in __XDG_VARS]):
        return True


def _get_base(app_name: str) -> Pypath:
    """Gets the application's base data directory."""
    if operating_system == "nt":
        return expand(f"%appdata%\\{app_name}")
    else:
        return expand(f"$HOME/.{app_name}")


def _get_dirs(app_name, create=False):
    """Gets the config, data and cache dirs for the application."""
    if _is_xdg_compliant():
        return ConfigDirectories(environ[var] for var in __XDG_VARS)

    base: Pypath = _get_base(app_name)
    config = join(base, "config")
    data = join(base, "data")
    cache = join(base, "cache")

    if create:
        for item in [base, config, data, cache]:
            Pypath(item).mkdir(parents=True, exist_ok=True)

    return ConfigDirectories(config, data, cache)


def try_to_cast(value, to, default=NO_VALUE):
    """Attempts to return `to(value)`, falling back to `default` if necessary.

    The silly default value of `default` is used because None might very well
    be the exact default value someone wants back, and that'd be problematic.
    """
    try:
        return to(value)
    except (ValueError, TypeError):
        if default != NO_VALUE:
            return default
        raise
